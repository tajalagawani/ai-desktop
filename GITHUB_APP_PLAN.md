# GitHub Desktop Clone - Full Implementation Plan

## Project Overview
Build a fully functional GitHub Desktop clone as a desktop app within the AI Desktop environment. The app will provide a GUI for all common Git operations, matching the functionality of the official GitHub Desktop application.

## Architecture Approach
**Simple & Lightweight:**
- ✅ All git operations = direct CLI commands
- ✅ Single API endpoint to execute commands
- ✅ No heavy npm libraries
- ✅ Runs natively on VPS with git already installed
- ✅ Parse command outputs and display in UI

---

## Phase 1: Core UI Structure & Layout (Week 1)

### 1.1 Main Layout Components

**Three-Column Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  [Repo Selector ▼]              [Fetch] [Push] [Pull]  │
├─────────────┬────────────────────┬──────────────────────┤
│             │                    │                      │
│  Sidebar    │   Main Content     │   Diff/Details Panel │
│  (Left)     │   (Center)         │   (Right)            │
│             │                    │                      │
│ - Changes   │   File List /      │   Code Diff          │
│ - History   │   Commit List      │   File Details       │
│ - Branches  │                    │   Commit Info        │
│ - Remotes   │                    │                      │
│ - Tags      │                    │                      │
│ - Stashes   │                    │                      │
│             │                    │                      │
└─────────────┴────────────────────┴──────────────────────┘
```

**Components to Build:**
- `components/apps/github/layout.tsx` - Main app container
- `components/apps/github/header.tsx` - Top bar with repo selector and actions
- `components/apps/github/sidebar.tsx` - Left navigation sidebar
- `components/apps/github/main-content.tsx` - Center content area
- `components/apps/github/diff-panel.tsx` - Right side diff viewer

### 1.2 Repository Selector
- Dropdown to switch between repositories
- "Add Repository" button (Clone, Create New, Add Existing)
- Current repository name and branch display
- Recent repositories list

### 1.3 Top Action Bar
- **Fetch Origin** - Check for remote updates
- **Pull Origin** - Pull latest changes
- **Push Origin** - Push local commits
- **Current Branch** - Branch selector dropdown
- **New Branch** - Create new branch button

---

## Phase 2: File Changes View (Week 2)

### 2.1 Changes Tab
**Features:**
- List of modified, added, deleted files
- Checkboxes to select files for staging
- File status icons (M=Modified, A=Added, D=Deleted, R=Renamed)
- Search/filter files
- "Discard Changes" option
- "Stash Changes" option

**Diff Viewer (Right Panel):**
- Side-by-side or unified diff view
- Syntax highlighting
- Line numbers
- Expand/collapse hunks
- Stage/unstage individual lines or hunks

### 2.2 Commit Panel (Bottom of Changes Tab)
- Commit message input (summary + description)
- "Commit to [branch-name]" button
- Amend last commit checkbox
- Co-authors selector
- Character count for commit message

**File List Item Component:**
```tsx
interface FileChange {
  path: string
  status: 'modified' | 'added' | 'deleted' | 'renamed'
  oldPath?: string // for renames
  staged: boolean
  additions: number
  deletions: number
}
```

---

## Phase 3: History View (Week 3)

### 3.1 Commit History Tab
**Features:**
- Chronological list of commits
- Commit graph showing branches/merges
- Search commits (message, author, SHA)
- Filter by branch
- Virtual scrolling for performance

**Commit List Item:**
- Commit message (first line)
- Author name and avatar
- Commit date/time (relative: "2 hours ago")
- Commit SHA (short)
- Branch tags/labels
- Undo/revert/cherry-pick actions

### 3.2 Commit Details (Right Panel)
When clicking a commit, show:
- Full commit message
- Author & committer info
- Commit SHA (full)
- Parent commit(s)
- Changed files list with diff stats
- Full diff for each file
- "Revert this commit" button
- "Cherry-pick to current branch" button
- "Create tag" button

**Data Structure:**
```tsx
interface Commit {
  sha: string
  author: { name: string; email: string; date: Date }
  committer: { name: string; email: string; date: Date }
  message: string
  parents: string[]
  files: FileChange[]
  stats: { additions: number; deletions: number; total: number }
}
```

---

## Phase 4: Branch Management (Week 4)

### 4.1 Branches Tab
**Features:**
- List of local branches
- List of remote branches
- Current branch highlighted
- "New Branch" button
- Branch search/filter
- Branch icons (current, published, unpublished)

**Branch Actions:**
- Checkout branch (switch to it)
- Rename branch
- Delete branch (with safety checks)
- Merge branch into current
- Rebase current branch onto another
- Publish branch (push to remote)
- Pull from remote

### 4.2 Branch Comparison
- Compare any two branches
- Show commits ahead/behind
- Show file differences
- "Merge" button if applicable

**Branch Component:**
```tsx
interface Branch {
  name: string
  type: 'local' | 'remote'
  isCurrent: boolean
  isPublished: boolean
  upstream?: string
  ahead: number // commits ahead of upstream
  behind: number // commits behind upstream
  lastCommit: Commit
}
```

---

## Phase 5: Repository Operations (Week 5)

### 5.1 Clone Repository
**UI Components:**
- URL input field
- Local path selector
- "Clone" button
- Progress indicator
- Authentication handling

### 5.2 Create New Repository
- Repository name input
- Description (optional)
- Local path selector
- "Initialize with README" checkbox
- .gitignore template selector
- License selector
- "Create Repository" button

### 5.3 Add Existing Repository
- Folder picker
- Detect if folder has .git
- Show repository info
- "Add Repository" button

### 5.4 Repository Settings
- Remote URLs (origin, upstream, etc.)
- Add/remove/edit remotes
- Default branch
- Git LFS settings
- Ignored files (.gitignore editor)

---

## Phase 6: Advanced Features (Week 6)

### 6.1 Stash Management
**Stashes Tab:**
- List of stashed changes
- Stash message/description
- Date created
- Files included in stash

**Actions:**
- Create new stash (with message)
- Apply stash
- Pop stash (apply and delete)
- Drop stash (delete)
- View stash diff

### 6.2 Tags
- List all tags
- Create lightweight/annotated tags
- Push tags to remote
- Delete tags
- Checkout tag

### 6.3 Cherry-pick
- Select commit from history
- Cherry-pick to current branch
- Resolve conflicts if needed

### 6.4 Interactive Rebase
- Reorder commits
- Squash commits
- Edit commit messages
- Drop commits

### 6.5 Conflict Resolution
**When merge/rebase conflicts occur:**
- List conflicted files
- Show conflict markers
- Three-way merge view (ours, theirs, result)
- "Use Ours" / "Use Theirs" / "Use Both" buttons
- Manual edit option
- "Mark as resolved" button
- Continue/abort merge

---

## Phase 7: Pull Requests & GitHub Integration (Week 7)

### 7.1 Pull Requests Tab
**Features:**
- List open PRs for current repository
- PR status (open, merged, closed)
- PR number, title, author
- Created/updated date
- Review status (approved, changes requested, pending)
- CI/CD check status

**PR Details View:**
- Full description
- Comments/reviews
- Commits included
- Files changed
- Checks status
- "Checkout PR" button
- "View on GitHub" button

### 7.2 Create Pull Request
- Source branch selector
- Target branch selector (usually main/master)
- Title input
- Description textarea
- Reviewers selector
- Labels selector
- "Create Pull Request" button

---

## Phase 8: Backend - Simple Git CLI Commands (Week 8)

### 8.1 Single API Route - Execute Git Commands
**One simple API route:**

```typescript
// app/api/git/route.ts
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function POST(request: Request) {
  const { repoPath, command } = await request.json()

  try {
    const { stdout, stderr } = await execAsync(command, {
      cwd: repoPath,
      maxBuffer: 10 * 1024 * 1024 // 10MB buffer
    })

    return Response.json({
      success: true,
      output: stdout,
      error: stderr
    })
  } catch (error: any) {
    return Response.json({
      success: false,
      error: error.message
    }, { status: 500 })
  }
}
```

### 8.2 Frontend Git Operations - Just CLI Commands!
**All operations are simple git commands:**

```typescript
// hooks/use-git.ts
async function runGit(repoPath: string, command: string) {
  const response = await fetch('/api/git', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repoPath, command })
  })
  return response.json()
}

// Usage examples:
await runGit('/var/www/my-repo', 'git status --short')
await runGit('/var/www/my-repo', 'git add .')
await runGit('/var/www/my-repo', 'git commit -m "My commit"')
await runGit('/var/www/my-repo', 'git push origin main')
await runGit('/var/www/my-repo', 'git log --oneline -n 50')
await runGit('/var/www/my-repo', 'git diff HEAD')
await runGit('/var/www/my-repo', 'git branch')
await runGit('/var/www/my-repo', 'git checkout -b new-branch')
```

**That's it! No heavy libraries needed.**

### 8.3 Git Commands Reference - Complete List

**Repository Management:**
```bash
# Clone repository
git clone <url> <path>

# Initialize new repository
git init <path>

# Check if folder is git repo
git rev-parse --git-dir

# Get current repository info
git remote -v
git config --get remote.origin.url
```

**File Changes:**
```bash
# Get status (short format for parsing)
git status --short --porcelain

# Stage files
git add <file>
git add .
git add --all

# Unstage files
git reset HEAD <file>

# Discard changes
git checkout -- <file>
git restore <file>

# Get diff
git diff                    # unstaged changes
git diff --staged           # staged changes
git diff HEAD               # all changes
git diff <file>             # specific file
```

**Commits:**
```bash
# Create commit
git commit -m "message"
git commit -m "title" -m "description"

# Amend last commit
git commit --amend -m "new message"
git commit --amend --no-edit

# Revert commit
git revert <sha>

# Get commit history
git log --oneline -n 50
git log --all --graph --oneline
git log --pretty=format:"%h|%an|%ae|%ad|%s" --date=iso

# Show commit details
git show <sha>
git show <sha> --stat
git show <sha> -- <file>
```

**Branches:**
```bash
# List branches
git branch                  # local only
git branch -r               # remote only
git branch -a               # all branches

# Get current branch
git branch --show-current
git rev-parse --abbrev-ref HEAD

# Create branch
git branch <name>
git checkout -b <name>

# Switch branch
git checkout <name>
git switch <name>

# Rename branch
git branch -m <old> <new>

# Delete branch
git branch -d <name>        # safe delete
git branch -D <name>        # force delete

# Track remote branch
git branch --set-upstream-to=origin/<name>

# Get branch status (ahead/behind)
git rev-list --left-right --count origin/main...HEAD
```

**Merge & Rebase:**
```bash
# Merge branch
git merge <branch>
git merge --no-ff <branch>

# Abort merge
git merge --abort

# Rebase
git rebase <branch>
git rebase --continue
git rebase --abort

# Interactive rebase
git rebase -i HEAD~5
```

**Remote Operations:**
```bash
# Fetch from remote
git fetch origin
git fetch --all

# Pull (fetch + merge)
git pull origin <branch>
git pull --rebase origin <branch>

# Push to remote
git push origin <branch>
git push -u origin <branch>  # set upstream
git push --force-with-lease

# List remotes
git remote -v

# Add remote
git remote add <name> <url>

# Remove remote
git remote remove <name>

# Change remote URL
git remote set-url origin <url>
```

**Stash:**
```bash
# Create stash
git stash
git stash save "message"
git stash push -m "message"

# List stashes
git stash list

# Show stash diff
git stash show stash@{0}
git stash show -p stash@{0}  # with full diff

# Apply stash
git stash apply stash@{0}
git stash pop stash@{0}      # apply and delete

# Drop stash
git stash drop stash@{0}

# Clear all stashes
git stash clear
```

**Tags:**
```bash
# List tags
git tag

# Create tag
git tag <name>
git tag -a <name> -m "message"  # annotated tag

# Show tag info
git show <tag>

# Delete tag
git tag -d <name>

# Push tags
git push origin <tag>
git push origin --tags

# Delete remote tag
git push origin --delete <tag>
```

**Cherry-pick:**
```bash
# Cherry-pick commit
git cherry-pick <sha>

# Cherry-pick multiple commits
git cherry-pick <sha1> <sha2>

# Cherry-pick without committing
git cherry-pick -n <sha>

# Abort cherry-pick
git cherry-pick --abort
```

**Conflicts:**
```bash
# Check for conflicts
git diff --name-only --diff-filter=U

# List conflicted files
git ls-files -u

# Accept ours/theirs
git checkout --ours <file>
git checkout --theirs <file>

# Mark as resolved
git add <file>
```

**Information:**
```bash
# Get file history
git log --follow -- <file>

# Get blame/annotations
git blame <file>

# Count commits
git rev-list --count HEAD

# Get repository size
git count-objects -vH

# Check if repo is clean
git diff-index --quiet HEAD --

# Get last commit SHA
git rev-parse HEAD
git rev-parse --short HEAD
```

### 8.4 Parsing Git Command Outputs

**Parse git status:**
```typescript
// git status --short --porcelain
// Output: "M  file.txt"  (modified)
//         "A  new.txt"   (added)
//         "D  old.txt"   (deleted)
//         "?? untracked.txt"  (untracked)

function parseStatus(output: string): FileChange[] {
  return output.split('\n').filter(Boolean).map(line => {
    const status = line.substring(0, 2)
    const path = line.substring(3)

    return {
      path,
      status: status.includes('M') ? 'modified' :
              status.includes('A') ? 'added' :
              status.includes('D') ? 'deleted' :
              status.includes('??') ? 'untracked' : 'unknown',
      staged: status[0] !== ' ' && status[0] !== '?'
    }
  })
}
```

**Parse git log:**
```typescript
// git log --pretty=format:"%h|%an|%ae|%ad|%s" --date=iso
// Output: "abc123|John Doe|john@example.com|2025-01-16 10:30:00 +0000|Commit message"

function parseLog(output: string): Commit[] {
  return output.split('\n').filter(Boolean).map(line => {
    const [sha, authorName, authorEmail, date, message] = line.split('|')

    return {
      sha,
      author: { name: authorName, email: authorEmail, date: new Date(date) },
      message
    }
  })
}
```

**Parse git branch:**
```typescript
// git branch --all
// Output: "* main"  (current branch)
//         "  develop"
//         "  remotes/origin/main"

function parseBranches(output: string): Branch[] {
  return output.split('\n').filter(Boolean).map(line => {
    const isCurrent = line.startsWith('*')
    const name = line.replace('*', '').trim()
    const isRemote = name.startsWith('remotes/')

    return {
      name: isRemote ? name.replace('remotes/origin/', '') : name,
      isCurrent,
      type: isRemote ? 'remote' : 'local'
    }
  })
}
```

**Parse git diff:**
```typescript
// git diff returns standard unified diff format
// Just display it in a <pre> tag with syntax highlighting!

function parseDiff(output: string) {
  // Split into hunks for better display
  const lines = output.split('\n')

  return lines.map(line => ({
    content: line,
    type: line.startsWith('+') ? 'addition' :
          line.startsWith('-') ? 'deletion' :
          line.startsWith('@@') ? 'hunk' : 'context'
  }))
}
```

### 8.5 Repository State Management
**Store repository information:**
```typescript
// data/github-app-data.ts
export interface Repository {
  id: string
  name: string
  path: string
  currentBranch: string
  remotes: Remote[]
  lastFetched?: Date
  ahead: number
  behind: number
}

export interface AppState {
  repositories: Repository[]
  currentRepoId: string | null
  settings: GitHubAppSettings
}
```

---

## Phase 9: UI/UX Polish (Week 9)

### 9.1 Visual Design
**Color Scheme (Match GitHub Desktop):**
- Background: `#24292e` (dark) / `#ffffff` (light)
- Sidebar: `#1f2428` (dark) / `#f6f8fa` (light)
- Primary: `#0366d6` (GitHub blue)
- Success: `#28a745` (green)
- Danger: `#d73a49` (red)
- Warning: `#ffd33d` (yellow)

**Fonts:**
- System font stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", ...`
- Monospace for code: `"SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace`

### 9.2 Animations & Transitions
- Smooth panel transitions
- Loading states with spinners
- Success/error toast notifications
- Progress bars for long operations (clone, fetch, push)

### 9.3 Keyboard Shortcuts
```
Cmd/Ctrl + N    : New Repository
Cmd/Ctrl + O    : Add Repository
Cmd/Ctrl + T    : New Branch
Cmd/Ctrl + Enter: Commit
Cmd/Ctrl + P    : Push
Cmd/Ctrl + Shift + P : Pull
Cmd/Ctrl + F    : Find in Files
Cmd/Ctrl + B    : Branches View
Cmd/Ctrl + H    : History View
Cmd/Ctrl + 1-9  : Switch tabs
```

### 9.4 Accessibility
- ARIA labels
- Keyboard navigation
- Focus management
- Screen reader support

---

## Phase 10: Testing & Optimization (Week 10)

### 10.1 Error Handling
- Network errors (remote unreachable)
- Authentication errors
- Merge conflicts
- Permission errors
- Invalid repository paths
- User-friendly error messages
- Retry mechanisms

### 10.2 Performance Optimization
- Virtual scrolling for long lists
- Debounce search inputs
- Lazy load commit history
- Cache repository status
- Web Worker for heavy Git operations
- Diff computation optimization

### 10.3 Edge Cases
- Empty repositories
- Large files
- Binary files
- Submodules
- Detached HEAD state
- Orphaned commits
- Force push scenarios

---

## Technical Stack

### Frontend
- **React** - Component library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Zustand** - State management (already have it)
- **date-fns** - Date formatting (already have it)

### Backend
- **Git CLI** - Direct git commands via `exec`
- **child_process** - Execute commands (built-in Node.js)
- **No extra libraries needed!**

### New Dependencies (Optional)
```json
{
  "dependencies": {
    "react-diff-view": "^3.x",  // For code diffs (optional, can use simple pre tags)
  }
}
```

**That's it! Keep the app lightweight by using what's already available on the VPS.**

---

## File Structure

```
components/apps/github/
├── index.tsx                  # Main GitHub app component
├── layout/
│   ├── header.tsx            # Top action bar
│   ├── sidebar.tsx           # Left sidebar navigation
│   └── three-panel.tsx       # Three-column layout
├── changes/
│   ├── changes-list.tsx      # List of changed files
│   ├── file-item.tsx         # Single file change item
│   ├── commit-panel.tsx      # Commit message + button
│   └── stage-controls.tsx    # Stage/unstage controls
├── history/
│   ├── commit-list.tsx       # Virtual scrolling commit list
│   ├── commit-item.tsx       # Single commit item
│   ├── commit-graph.tsx      # Branch visualization
│   └── commit-details.tsx    # Right panel commit details
├── branches/
│   ├── branch-list.tsx       # All branches
│   ├── branch-item.tsx       # Single branch
│   ├── branch-compare.tsx    # Compare branches
│   └── branch-actions.tsx    # Create/delete/merge
├── pull-requests/
│   ├── pr-list.tsx           # All PRs
│   ├── pr-item.tsx           # Single PR
│   └── pr-details.tsx        # PR details view
├── repository/
│   ├── clone-dialog.tsx      # Clone repository
│   ├── create-dialog.tsx     # Create new repo
│   ├── add-dialog.tsx        # Add existing repo
│   └── settings-dialog.tsx   # Repository settings
├── diff/
│   ├── diff-viewer.tsx       # Monaco-based diff viewer
│   ├── unified-diff.tsx      # Unified diff view
│   ├── split-diff.tsx        # Side-by-side diff
│   └── hunk-controls.tsx     # Stage/unstage hunks
├── conflicts/
│   ├── conflict-list.tsx     # List of conflicts
│   ├── conflict-editor.tsx   # Three-way merge editor
│   └── conflict-actions.tsx  # Resolve/abort
└── shared/
    ├── file-icon.tsx         # File type icons
    ├── commit-avatar.tsx     # Author avatar
    ├── branch-badge.tsx      # Branch labels
    ├── loading-spinner.tsx   # Loading states
    └── toast.tsx             # Notifications

app/api/
└── git/route.ts              # Single API - executes any git command

data/
├── github-app-data.ts        # Types and interfaces
└── github-app-store.ts       # Zustand store

hooks/
├── use-git-status.ts         # Poll repository status
├── use-git-log.ts            # Fetch commit history
├── use-git-diff.ts           # Get file diffs
└── use-repositories.ts       # Manage repo list
```

---

## Implementation Priority

### Must Have (MVP)
1. ✅ Clone repository
2. ✅ View changes
3. ✅ Stage/unstage files
4. ✅ Commit changes
5. ✅ Push to remote
6. ✅ Pull from remote
7. ✅ View commit history
8. ✅ Switch branches
9. ✅ Create new branch
10. ✅ View diffs

### Should Have
11. ✅ Merge branches
12. ✅ Resolve conflicts
13. ✅ Stash changes
14. ✅ Discard changes
15. ✅ Amend commits
16. ✅ Create repository
17. ✅ Add existing repository
18. ✅ Multiple repositories

### Nice to Have
19. ⚠️ Pull requests view
20. ⚠️ Cherry-pick commits
21. ⚠️ Interactive rebase
22. ⚠️ Tags management
23. ⚠️ Submodules
24. ⚠️ Git LFS support
25. ⚠️ Blame view

---

## Success Criteria

1. **Functionality**: All core Git operations work correctly
2. **UI/UX**: Matches GitHub Desktop's look and feel
3. **Performance**: Handles repositories with 1000+ commits smoothly
4. **Reliability**: Proper error handling for all edge cases
5. **Accessibility**: Keyboard navigation and screen reader support
6. **Documentation**: Clear README with usage instructions

---

## Timeline Summary

- **Week 1-2**: Core UI + Changes View
- **Week 3-4**: History + Branches
- **Week 5-6**: Advanced Features
- **Week 7**: Pull Requests
- **Week 8**: Backend Integration
- **Week 9**: Polish
- **Week 10**: Testing

**Total Estimated Time**: 10 weeks for full-featured GitHub Desktop clone

---

## Next Steps

1. Review and approve this plan
2. Set up project structure
3. Install required dependencies
4. Start with Phase 1 (Core UI)
5. Iterate and test each phase

Would you like me to start implementing Phase 1 now?
