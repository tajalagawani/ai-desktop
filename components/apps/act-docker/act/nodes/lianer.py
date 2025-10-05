"""
Phased Memory Model - Generic wrapper for HuggingFace-style models
Supports:
 - Any transformer model (PreTrainedModel) that outputs hidden_states/attentions when requested
 - Per-layer KV prefix injection via MemoryPrefix with per-layer gating and caps
 - Multi-signal memory scoring (l2, attention, entropy, saliency)
 - Improved InfoNCE contrastive loss
 - Optional saliency caching / intermittent saliency computation
 - Dynamic phase sparsity heuristic
 - Correct nucleus (top-p) sampling implementation
 - Options to disable attention/hidden output collection for efficiency

Usage: import this file and instantiate PhasedMemoryModel with a HuggingFace model class or model

Note: This file is kept self-contained for clarity; adapt components to your codebase as needed.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Literal, Any

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import PreTrainedModel, PreTrainedTokenizerBase


################################################################################
# Utilities
################################################################################

@dataclass
class MemoryScoringWeights:
    l2: float = 0.0
    attention: float = 1.0
    entropy: float = 0.5
    saliency: float = 0.0  # requires training (grads)


def token_entropy_from_logits(logits: torch.Tensor) -> torch.Tensor:
    """
    logits: [B, T, V]
    returns: entropy per token [B, T]
    """
    probs = F.softmax(logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    ent = -(probs * log_probs).sum(dim=-1)
    return ent


################################################################################
# Prefix adapter (generic, per-layer caps + gating)
################################################################################

class MemoryPrefix(nn.Module):
    """
    Projects memory vectors (B, M, D) into per-layer K/V prefixes compatible with HF past_key_values.
    Supports learned scalar gates and per-layer caps.
    """
    def __init__(self, n_layer: int, hidden_size: int, n_head: int, per_layer_caps: Optional[List[int]] = None):
        super().__init__()
        self.n_layer = n_layer
        self.hidden_size = hidden_size
        self.n_head = n_head
        if hidden_size % n_head != 0:
            raise ValueError("hidden_size must be divisible by n_head")
        self.head_dim = hidden_size // n_head
        self.per_layer_caps = per_layer_caps or [None] * n_layer

        # per-layer projections
        self.key_projs = nn.ModuleList([nn.Linear(hidden_size, hidden_size) for _ in range(n_layer)])
        self.val_projs = nn.ModuleList([nn.Linear(hidden_size, hidden_size) for _ in range(n_layer)])
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.layer_gates = nn.Parameter(torch.ones(n_layer))

    def forward(self, mem: Optional[torch.Tensor]) -> List[Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        """
        mem: [B, M, D] or None
        returns list length n_layer of (k, v) or None, where shapes are [B, H, M', Dh]
        """
        if mem is None or (hasattr(mem, 'numel') and mem.numel() == 0):
            return [None] * self.n_layer

        B, M, D = mem.shape
        x = self.layer_norm(mem)
        out: List[Optional[Tuple[torch.Tensor, torch.Tensor]]] = []
        for l in range(self.n_layer):
            xl = x
            cap = self.per_layer_caps[l]
            if cap is not None and M > cap:
                xl = xl[:, :cap, :]
            gate = torch.clamp(self.layer_gates[l], min=0.0)
            if gate.item() == 0.0:
                out.append(None)
                continue
            k = self.key_projs[l](xl) * gate
            v = self.val_projs[l](xl) * gate
            # reshape to [B, H, M', Dh]
            k = k.view(B, -1, self.n_head, self.head_dim).permute(0, 2, 1, 3).contiguous()
            v = v.view(B, -1, self.n_head, self.head_dim).permute(0, 2, 1, 3).contiguous()
            out.append((k, v))
        return out


################################################################################
# Generic Phased Memory model wrapper
################################################################################

class PhasedMemoryModel(nn.Module):
    """
    Wraps any PreTrainedModel (HuggingFace) and provides phased generation + prefix memory injection.

    Important flags:
      - collect_attentions: whether to request attentions from the base model (costly)
      - collect_hidden_states: whether to request hidden states (costly)

    The wrapper exposes the same forward semantics but adds memory scoring & candidate selection.
    """

    def __init__(
        self,
        base_model: PreTrainedModel,
        *,
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        n_phases: int = 10,
        sparsity_ratio: float = 0.23,
        max_memory_tokens: int = 64,
        topk_per_phase: int = 16,
        burst_reactivation_k: int = 8,
        per_layer_caps: Optional[List[int]] = None,
        scoring_weights: MemoryScoringWeights = MemoryScoringWeights(),
        entropy_temperature: float = 1.0,
        saliency_stop_grad: bool = True,
        collect_attentions: bool = True,
        collect_hidden_states: bool = True,
        dynamic_sparsity: bool = True,
        saliency_interval: int = 5,  # compute saliency once every N training steps (if enabled)
    ):
        super().__init__()
        if not isinstance(base_model, PreTrainedModel):
            raise ValueError("base_model must be a HuggingFace PreTrainedModel instance")

        self.base_model = base_model
        self.tokenizer = tokenizer
        self.config = base_model.config

        self.n_phases = n_phases
        self.sparsity_ratio = sparsity_ratio
        self.vocab_size = getattr(self.config, 'vocab_size', None)
        self.hidden_size = getattr(self.config, 'hidden_size', getattr(self.config, 'n_embd', None))
        self.n_layer = getattr(self.config, 'n_layer', None)
        self.n_head = getattr(self.config, 'n_head', None)

        # memory / prefix
        self.max_memory_tokens = max_memory_tokens
        self.topk_per_phase = topk_per_phase
        self.burst_reactivation_k = burst_reactivation_k
        self.per_layer_caps = per_layer_caps or ([None] * (self.n_layer or 0))
        self.memory_projector = nn.Linear(self.hidden_size, self.hidden_size)
        self.prefix_adapter = MemoryPrefix(n_layer=self.n_layer, hidden_size=self.hidden_size, n_head=self.n_head, per_layer_caps=self.per_layer_caps)

        # scoring and misc
        self.scoring_weights = scoring_weights
        self.entropy_temperature = entropy_temperature
        self.saliency_stop_grad = saliency_stop_grad

        # flags (efficiency)
        self.collect_attentions = collect_attentions
        self.collect_hidden_states = collect_hidden_states

        # dynamics
        self.dynamic_sparsity = dynamic_sparsity
        self.saliency_interval = saliency_interval
        self._train_step_counter = 0

        # track indices for burst reactivation
        self.register_buffer("last_phase_top_indices", torch.zeros(1, 0, dtype=torch.long), persistent=False)

        # optional linear head (if your base model doesn't have a lm_head)
        if hasattr(base_model, 'lm_head'):
            self.lm_head = base_model.lm_head
        else:
            self.lm_head = nn.Linear(self.hidden_size, self.vocab_size, bias=False)

    ############################################################################
    # Phase masks (with dynamic sparsity heuristic)
    ############################################################################
    def _build_phase_masks(self, input_ids: torch.Tensor, phase: int, logits: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Returns [B, T] mask of active tokens (1) vs inactive (0).
        If final phase -> all ones.
        Dynamic sparsity: uses avg token entropy (if logits provided) to reduce sparsity when model is uncertain.
        Burst reactivation: re-activates top indices tracked from previous phase.
        """
        B, T = input_ids.shape
        device = input_ids.device
        if phase >= self.n_phases - 1 or T == 0:
            return torch.ones(B, T, device=device, dtype=torch.float)

        base_active_ratio = max(1e-6, 1.0 - self.sparsity_ratio)

        # dynamic adjust: if logits provided, compute mean entropy and increase active ratio when entropy high
        if self.dynamic_sparsity and logits is not None:
            ent = token_entropy_from_logits(logits)  # [B, T]
            # mean entropy normalized by log(V)
            max_ent = math.log(self.vocab_size or ent.size(-1) or 1)
            ent_mean = ent.mean(dim=-1) / (max_ent + 1e-9)  # [B]
            # higher entropy -> more tokens active (linearly interpolate)
            # clamp contribution to [0, 0.5] so we don't disable sparsity fully
            ent_factor = ent_mean.clamp(0.0, 1.0) * 0.5
            active_ratios = (base_active_ratio + ent_factor).clamp(min=0.05, max=1.0)
        else:
            active_ratios = torch.full((B,), base_active_ratio, device=device)

        mask = torch.zeros(B, T, device=device, dtype=torch.float)
        for b in range(B):
            active_tokens = min(max(1, int(round(T * float(active_ratios[b].item())))), T)
            if active_tokens >= T:
                mask[b, :] = 1.0
                continue
            # rolling window start
            if True:  # retain rolling as default
                max_start = max(0, T - active_tokens)
                start = (phase * max(1, active_tokens // 2)) % (max_start + 1)
            else:
                start = 0
            end = start + active_tokens
            mask[b, start:end] = 1.0

        # burst reactivation
        if self.last_phase_top_indices is not None and self.last_phase_top_indices.numel() > 0:
            for b in range(B):
                idxs = self.last_phase_top_indices[min(b, self.last_phase_top_indices.size(0) - 1)]
                idxs = idxs[idxs < T]
                mask[b, idxs] = 1.0

        return mask

    ############################################################################
    # Memory bank utilities
    ############################################################################
    @staticmethod
    def _l2_scores(vecs: torch.Tensor) -> torch.Tensor:
        return torch.norm(vecs, dim=-1)

    @staticmethod
    def _gather_topk_indices(scores: torch.Tensor, k: int) -> torch.Tensor:
        B, L = scores.shape
        k_eff = min(k, L)
        if k_eff <= 0:
            return torch.zeros(B, 0, dtype=torch.long, device=scores.device)
        _, idx = torch.topk(scores, k=k_eff, dim=-1)
        return idx

    def _select_topk(self, candidates: torch.Tensor, scores: torch.Tensor, k: int) -> torch.Tensor:
        """candidates: [B, T, D], scores: [B, T] -> [B, k, D] sorted by score desc"""
        B, T, D = candidates.shape
        if T == 0 or k <= 0:
            return candidates[:, :0]
        idx = self._gather_topk_indices(scores, k)
        idx_exp = idx.unsqueeze(-1).expand(-1, -1, D)
        top = torch.gather(candidates, dim=1, index=idx_exp)
        return top

    def _compress_bank(self, bank: Optional[torch.Tensor]) -> Optional[torch.Tensor]:
        if bank is None or bank.numel() == 0:
            return None
        B, M, D = bank.shape
        if M <= self.max_memory_tokens:
            return bank
        scores = self._l2_scores(bank)
        idx = self._gather_topk_indices(scores, self.max_memory_tokens).unsqueeze(-1).expand(-1, -1, D)
        return torch.gather(bank, 1, idx)

    ############################################################################
    # Scoring signals
    ############################################################################
    def _compute_attention_scores(self, attns: List[torch.Tensor]) -> torch.Tensor:
        """
        attns: list of [B, H, T, S] from each layer.
        returns token-level scores [B, S]
        """
        if not attns:
            # fallback to zeros
            return torch.zeros(1, 0)
        L = len(attns)
        take = max(1, L // 3)
        tail = attns[-take:]
        score_list = []
        for A in tail:
            # A: [B, H, T, S]
            last_q = A[:, :, -1, :]  # [B, H, S]
            score_list.append(last_q.mean(dim=1))  # [B, S]
        scores = torch.stack(score_list, dim=0).mean(dim=0)  # [B, S]
        # normalize per example
        return scores / (scores.amax(dim=-1, keepdim=True) + 1e-6)

    def _compute_saliency_scores(self, hidden: torch.Tensor, loss: torch.Tensor) -> torch.Tensor:
        """
        hidden: [B, T, D] (requires grad)
        loss: scalar loss
        returns: [B, T] saliency = ||d loss / d hidden||
        """
        grads = torch.autograd.grad(loss, hidden, retain_graph=True, create_graph=not self.saliency_stop_grad)[0]
        sal = grads.norm(dim=-1)
        return sal / (sal.amax(dim=-1, keepdim=True) + 1e-6)

    def _combine_scores(self, *, l2_s: Optional[torch.Tensor], attn_s: Optional[torch.Tensor], ent_s: Optional[torch.Tensor], sal_s: Optional[torch.Tensor]) -> torch.Tensor:
        terms = []
        w = self.scoring_weights
        if l2_s is not None and w.l2 != 0:
            terms.append(w.l2 * (l2_s / (l2_s.amax(dim=-1, keepdim=True) + 1e-6)))
        if attn_s is not None and w.attention != 0:
            terms.append(w.attention * attn_s)
        if ent_s is not None and w.entropy != 0:
            terms.append(w.entropy * (ent_s / (ent_s.amax(dim=-1, keepdim=True) + 1e-6)))
        if sal_s is not None and w.saliency != 0:
            terms.append(w.saliency * (sal_s / (sal_s.amax(dim=-1, keepdim=True) + 1e-6)))
        if not terms:
            # default fallback
            return l2_s if l2_s is not None else (attn_s if attn_s is not None else torch.zeros_like(ent_s))
        s = torch.stack(terms, dim=0).sum(dim=0)
        return s

    ############################################################################
    # Forward wrapper
    ############################################################################
    def forward(
        self,
        input_ids: torch.Tensor,
        phase: int,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None,
        memory_bank: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        teacher_logits: Optional[torch.Tensor] = None,
        compute_saliency: bool = False,
    ) -> Dict[str, Any]:
        device = input_ids.device
        B, T = input_ids.shape

        # Decide whether to request attentions/hidden states from base model
        req_attn = self.collect_attentions
        req_hidden = self.collect_hidden_states or (compute_saliency and labels is not None)

        # Build sparsity mask. We may pass a quick logits=None; dynamic sparsity can use logits if available later
        sparsity_mask = self._build_phase_masks(input_ids, phase, logits=None)

        # Build prefix past from memory bank
        prefix_past = self.prefix_adapter(memory_bank) if memory_bank is not None else [None] * self.n_layer

        # helper to concatenate past_key_values and prefix past
        def concat_past(prefix, past):
            if prefix is None:
                return past
            if past is None:
                return prefix
            cat = []
            for p, kv in zip(prefix, past):
                if p is None:
                    cat.append(kv)
                else:
                    pk, pv = p
                    k, v = kv
                    k_cat = torch.cat([pk, k], dim=2)
                    v_cat = torch.cat([pv, v], dim=2)
                    cat.append((k_cat, v_cat))
            return cat

        eff_past = concat_past(prefix_past if prefix_past[0] is not None else None, past_key_values)

        # Call base model
        model_kwargs = dict(
            input_ids=input_ids,
            attention_mask=attention_mask,
            past_key_values=eff_past,
            use_cache=True,
            output_attentions=req_attn,
            output_hidden_states=req_hidden,
        )
        outputs = self.base_model(**model_kwargs)

        # Extract hidden + logits
        # Many HF models put hidden state at outputs.last_hidden_state
        hidden: torch.Tensor = getattr(outputs, 'last_hidden_state', None)
        if hidden is None and hasattr(outputs, 'hidden_states') and outputs.hidden_states:
            hidden = outputs.hidden_states[-1]
        if hidden is None:
            raise RuntimeError("Base model did not return hidden states; enable output_hidden_states on the model")

        logits = self.lm_head(hidden) if hasattr(self, 'lm_head') else None

        loss = None
        ce_loss = None
        kd_loss = None
        contrastive_loss = None

        # Standard CE
        if labels is not None and logits is not None:
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = labels[:, 1:].contiguous()
            ce_loss = F.cross_entropy(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
            loss = ce_loss

        # KD
        if teacher_logits is not None and logits is not None:
            Ttemp = self.entropy_temperature
            # Use KL in a numerically stable way: cross_entropy between teacher probs and log probs from student
            t_probs = F.softmax(teacher_logits / Ttemp, dim=-1)
            s_log_probs = F.log_softmax(logits / Ttemp, dim=-1)
            kd = F.kl_div(s_log_probs, t_probs, reduction='batchmean') * (Ttemp ** 2)
            kd_loss = kd
            loss = kd if loss is None else (loss + kd)

        # Contrastive memory (InfoNCE)
        contrastive_weight = 0.05
        if labels is not None and contrastive_weight > 0:
            with torch.no_grad():
                target = hidden.detach().roll(shifts=-1, dims=1)
            proj = self.memory_projector(hidden)  # [B, T, D]
            mem_mask = (sparsity_mask == 0).float().unsqueeze(-1)
            q = F.normalize(proj * mem_mask, dim=-1)  # query vectors from inactive positions
            k = F.normalize(target, dim=-1)
            # InfoNCE per example: for each position i, positive is k[i], negatives are other positions in same example
            # compute logits: q @ k.T => [B, T, T]
            sim = torch.matmul(q, k.transpose(1, 2)) / (self.entropy_temperature + 1e-9)
            # mask out positions that are entirely zero (inactive) to avoid numerical issues
            # construct labels: diagonal indices
            B_, T_, _ = sim.shape
            # reshape to (B*T, T) and targets idx
            sim_flat = sim.view(B_ * T_, T_)
            labels_nce = torch.arange(T_, device=sim.device).repeat(B_)
            # cross entropy expects logits where correct class is at labels_nce
            nce_loss = F.cross_entropy(sim_flat, labels_nce, reduction='none')
            nce_loss = nce_loss.view(B_, T_)
            # average only positions that were inactive
            mask_positions = (mem_mask.squeeze(-1) > 0).float()  # [B, T]
            if mask_positions.sum() > 0:
                nce = (nce_loss * mask_positions).sum() / (mask_positions.sum() + 1e-9)
            else:
                nce = nce_loss.mean()
            contrastive_loss = nce * contrastive_weight
            loss = contrastive_loss if loss is None else (loss + contrastive_loss)

        # === Memory scoring ===
        # compute signals; avoid expensive grads unless requested and allowed (compute_saliency)
        compute_sal = compute_saliency and (labels is not None) and ((self._train_step_counter % max(1, self.saliency_interval)) == 0)

        with torch.no_grad() if not compute_sal else torch.enable_grad():
            # prepare masks
            inactive_mask = (self._build_phase_masks(input_ids, phase, logits=logits) == 0).float()

            proj_hidden = self.memory_projector(hidden)
            l2_s = self._l2_scores(proj_hidden) * inactive_mask

            attn_s = None
            if req_attn and hasattr(outputs, 'attentions'):
                attn_s = self._compute_attention_scores(outputs.attentions) * inactive_mask

            ent_s = None
            if logits is not None:
                ent_s = token_entropy_from_logits(logits) * inactive_mask

            sal_s = None
            if compute_sal:
                tmp_loss = loss if loss is not None else ce_loss if ce_loss is not None else (torch.tensor(0.0, device=device))
                sal_s = self._compute_saliency_scores(hidden, tmp_loss) * inactive_mask

            combined = self._combine_scores(l2_s=l2_s, attn_s=attn_s, ent_s=ent_s, sal_s=sal_s)

            # Track top indices for burst reactivation
            with torch.no_grad():
                self.last_phase_top_indices = self._gather_topk_indices(combined, self.burst_reactivation_k)

            # Choose next memory candidates by top-k combined scores
            next_memory_candidates = self._select_topk(proj_hidden, combined, self.topk_per_phase)

        # increment train step counter
        if self.training:
            self._train_step_counter += 1

        return {
            'logits': logits,
            'past_key_values': getattr(outputs, 'past_key_values', None),
            'next_memory_candidates': next_memory_candidates,  # [B, K, D]
            'sparsity_mask': sparsity_mask,
            'loss': loss,
            'ce_loss': ce_loss,
            'kd_loss': kd_loss,
            'contrastive_loss': contrastive_loss,
            'hidden_states': getattr(outputs, 'hidden_states', None),
            'attentions': getattr(outputs, 'attentions', None),
        }


################################################################################
# Generation loop (corrected nucleus sampling and batched handling)
################################################################################

@torch.no_grad()
def phased_generate_with_prefix_memory(
    wrapped: PhasedMemoryModel,
    tokenizer: PreTrainedTokenizerBase,
    prompt: str,
    max_length: int = 100,
    device: Optional[str] = None,
    temperature: float = 1.0,
    top_p: float = 1.0,
    do_sample: bool = True,
):
    wrapped.eval()
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    wrapped.to(device)

    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)
    generated = input_ids

    past_kv = None
    memory_bank = None  # [1, M, D]

    for phase in range(wrapped.n_phases):
        if generated.size(1) >= max_length:
            break
        remaining = max_length - generated.size(1)
        steps_this_phase = max(1, remaining // max(1, (wrapped.n_phases - phase)))

        for _ in range(steps_this_phase):
            # call model with last token
            out = wrapped(
                input_ids=generated[:, -1:],
                phase=phase,
                attention_mask=None,
                past_key_values=past_kv,
                memory_bank=memory_bank,
                compute_saliency=False,
            )
            logits = out['logits'][:, -1, :]
            past_kv = out['past_key_values']
            next_mem = out['next_memory_candidates']

            # Sample / greedy
            if not do_sample:
                next_token = logits.argmax(dim=-1, keepdim=True)
            else:
                if temperature != 1.0:
                    logits = logits / max(1e-6, temperature)
                probs = F.softmax(logits, dim=-1)

                # Top-p (nucleus) sampling: select minimal set of tokens with cumulative prob >= top_p
                if top_p < 1.0:
                    sorted_probs, sorted_idx = torch.sort(probs, descending=True)
                    cumulative = torch.cumsum(sorted_probs, dim=-1)
                    # find cutoff index per batch
                    # we want to keep tokens up to the index where cumulative >= top_p (inclusive)
                    cutoff = (cumulative >= top_p).float().argmax(dim=-1)  # index of first True
                    # build mask of allowed tokens
                    batch_idx = torch.arange(probs.size(0), device=probs.device)
                    cutoff_exp = cutoff.unsqueeze(-1).expand(-1, probs.size(-1))
                    rank_positions = torch.arange(probs.size(-1), device=probs.device).unsqueeze(0).expand(probs.size(0), -1)
                    allow_mask = (rank_positions <= cutoff_exp)
                    # map allow_mask from sorted ranks back to original token indices
                    allow_mask_orig = torch.zeros_like(allow_mask).float()
                    allow_mask_orig.scatter_(1, sorted_idx, allow_mask.float())
                    probs = probs * allow_mask_orig
                    probs = probs / probs.sum(dim=-1, keepdim=True).clamp(min=1e-9)

                next_token = torch.multinomial(probs, num_samples=1)

            generated = torch.cat([generated, next_token], dim=1)
            if generated.size(1) >= max_length:
                break

        # Update memory bank after the phase
        if next_mem is not None and next_mem.numel() > 0:
            if memory_bank is None or memory_bank.numel() == 0:
                memory_bank = next_mem
            else:
                memory_bank = torch.cat([memory_bank, next_mem], dim=1)
            memory_bank = wrapped._compress_bank(memory_bank)

    text = tokenizer.decode(generated[0].tolist(), skip_special_tokens=True)
    return text


################################################################################
# Training step helper
################################################################################

def training_step(
    wrapped: PhasedMemoryModel,
    batch: Dict[str, torch.Tensor],
    teacher: Optional[PreTrainedModel] = None,
    optimizer: Optional[torch.optim.Optimizer] = None,
    compute_saliency: bool = False,
    unroll_phases: int = 1,  # how many phases to unroll for this training step
):
    wrapped.train()
    input_ids: torch.Tensor = batch['input_ids']
    labels: torch.Tensor = batch['labels']

    device = next(wrapped.parameters()).device
    input_ids = input_ids.to(device)
    labels = labels.to(device)

    teacher_logits = None
    if teacher is not None:
        teacher.eval()
        with torch.no_grad():
            t_out = teacher(input_ids=input_ids, output_hidden_states=False, output_attentions=False)
            teacher_logits = getattr(t_out, 'logits', None)

    # optionally unroll multiple phases to let model learn dynamics
    total_loss = None
    total_ce = None
    total_kd = None
    total_contrast = None

    past_kv = None
    memory_bank = None
    for u in range(max(1, unroll_phases)):
        out = wrapped(
            input_ids=input_ids,
            phase=min(u, wrapped.n_phases - 1),
            labels=labels,
            teacher_logits=teacher_logits,
            compute_saliency=compute_saliency,
            attention_mask=None,
            past_key_values=past_kv,
            memory_bank=memory_bank,
        )

        loss = out['loss'] if out['loss'] is not None else torch.tensor(0.0, device=device)
        if total_loss is None:
            total_loss = loss
        else:
            total_loss = total_loss + loss

        total_ce = (total_ce or 0.0) + (out.get('ce_loss') or 0.0)
        total_kd = (total_kd or 0.0) + (out.get('kd_loss') or 0.0)
        total_contrast = (total_contrast or 0.0) + (out.get('contrastive_loss') or 0.0)

        # update memory bank simulation
        next_mem = out['next_memory_candidates']
        if next_mem is not None and next_mem.numel() > 0:
            if memory_bank is None or memory_bank.numel() == 0:
                memory_bank = next_mem
            else:
                memory_bank = torch.cat([memory_bank, next_mem], dim=1)
            memory_bank = wrapped._compress_bank(memory_bank)

        # update past kv for next unroll step (allowing learning to use cache)
        past_kv = out['past_key_values']

    avg_loss = total_loss / float(max(1, unroll_phases))

    if optimizer is not None:
        optimizer.zero_grad()
        avg_loss.backward()
        torch.nn.utils.clip_grad_norm_(wrapped.parameters(), 1.0)
        optimizer.step()

    return {
        'loss': float(avg_loss.detach().cpu().item()),
        'ce_loss': float(total_ce / float(max(1, unroll_phases))),
        'kd_loss': float(total_kd / float(max(1, unroll_phases))),
        'contrastive_loss': float(total_contrast / float(max(1, unroll_phases))),
    }


################################################################################
# Example quick usage
################################################################################
if __name__ == '__main__':
    # Minimal quick demo showing instantiation pattern (do not run large models on CPU)
    try:
        from transformers import GPT2LMHeadModel, GPT2Tokenizer

        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        base = GPT2LMHeadModel.from_pretrained('gpt2')

        wrapped = PhasedMemoryModel(
            base_model=base,
            tokenizer=tokenizer,
            n_phases=4,
            sparsity_ratio=0.3,
            max_memory_tokens=48,
            topk_per_phase=12,
            per_layer_caps=[32] * base.config.n_layer,
            scoring_weights=MemoryScoringWeights(l2=0.2, attention=1.0, entropy=0.7, saliency=0.0),
            collect_attentions=True,
            collect_hidden_states=True,
            dynamic_sparsity=True,
            saliency_interval=10,
        )

        out = phased_generate_with_prefix_memory(wrapped, tokenizer, "Hello world", max_length=60, temperature=0.9, top_p=0.95)
        print(out)
    except Exception as e:
        print("Quick demo failed (likely due to missing HF models or CPU limits):", e)
