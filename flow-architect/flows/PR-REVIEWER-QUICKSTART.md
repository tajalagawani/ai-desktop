# GitHub PR Reviewer - Quick Start Guide

## ✅ Setup Complete!

Your GitHub, OpenAI, and Slack are already authenticated via the signature system!

## 🚀 How to Use

### Option 1: Review PRs via MCP Tools (Recommended)

You can execute the workflow using the MCP tools directly:

```javascript
// Example: Review PRs for a specific repository
mcp__flow-architect-signature__execute_node_operation({
  node_type: "github",
  operation: "list_pull_requests",
  params: {
    owner: "your-username",
    repo: "your-repo-name",
    state: "open"
  }
})
```

### Option 2: Run the ACT Workflow

Execute the complete workflow file:

**File:** `flows/github-pr-reviewer.act`

**Required Parameters:**
- `owner` - GitHub repository owner (e.g., "tajalagawani")
- `repo` - Repository name (e.g., "ai-desktop")
- `slack_channel` - Slack channel (e.g., "#pr-reviews" or "C1234567890")

**Example Command:**

```bash
# Via API (if you have ACT execution endpoint)
curl -X POST http://localhost:3000/api/act/execute \
  -H "Content-Type: application/json" \
  -d '{
    "flowPath": "flows/github-pr-reviewer.act",
    "params": {
      "owner": "tajalagawani",
      "repo": "your-repo-name",
      "slack_channel": "#pr-reviews"
    }
  }'
```

## 📋 What The Workflow Does

1. **Fetches Open PRs** - Gets all open pull requests from your repository
2. **Processes PR Data** - Extracts key information (title, author, description)
3. **Creates Review Prompt** - Prepares a comprehensive prompt for AI review
4. **AI Analysis** - Sends PR to OpenAI GPT-4 for code review
5. **Formats Review** - Parses and structures the AI response
6. **Posts to Slack** - Sends a beautifully formatted message to Slack
7. **Returns Summary** - Provides execution status and results

## 🎯 Example Output

When executed successfully, you'll get a Slack message like:

```
🔍 AI Code Review Complete

PR #42: Add user authentication feature
Author: developer123
Repository: my-awesome-app

────────────────────

Summary:
This PR implements JWT-based authentication with login/logout endpoints
and user session management.

Key Changes:
- Added User model with password hashing
- Implemented JWT token generation
- Created authentication middleware

Potential Issues:
- Password hash cost factor should be increased to 12
- Missing rate limiting on login endpoint
- JWT secret should be rotated regularly

Recommendations:
- Add input validation for email format
- Implement refresh token mechanism
- Add unit tests for auth middleware

Verdict: Request Changes
Address security concerns before merging.

📎 View PR on GitHub

────────────────────
📊 Total open PRs: 3 | ⚡ Reviewed by OpenAI GPT-4
```

## 🔄 Automated Reviews (Scheduled)

To automatically review PRs every hour, create a scheduled version:

**File:** `flows/github-pr-reviewer-scheduled.act`

Add a timer node:

```yaml
nodes:
  - id: schedule_reviews
    type: timer
    schedule: "0 * * * *"  # Every hour
    mode: "cron"
    timezone: "UTC"
    handler: "fetch_prs"
```

## 🎨 Customization

### Change AI Model

Edit line 108 in `github-pr-reviewer.act`:

```yaml
model: "gpt-4"          # Most thorough
# model: "gpt-4-turbo"  # Faster, cheaper
# model: "gpt-3.5-turbo" # Cheapest option
```

### Adjust Review Length

Edit line 115:

```yaml
max_tokens: 1000  # Increase for more detailed reviews
```

### Review Multiple PRs

Currently reviews the first open PR. To review ALL PRs, modify the Python code
at line 74 to loop through all PRs instead of just `prs[0]`.

## 🔐 Authentication Status

✅ **GitHub** - Authenticated as tajalagawani
✅ **OpenAI** - Authenticated (API key configured)
✅ **Slack** - Authenticated (token configured)

## 📊 Get Slack Channel ID

If you need your Slack channel ID:

```javascript
mcp__flow-architect-signature__execute_node_operation({
  node_type: "slack",
  operation: "list_channels",
  params: {}
})
```

Look for the channel in the results and use its `id` field.

## 🛠️ Test Individual Services

### Test GitHub Connection

```javascript
mcp__flow-architect-signature__execute_node_operation({
  node_type: "github",
  operation: "list_pull_requests",
  params: {
    owner: "tajalagawani",
    repo: "ai-desktop",
    state: "open"
  }
})
```

### Test OpenAI Connection

```javascript
mcp__flow-architect-signature__execute_node_operation({
  node_type: "openai",
  operation: "chat_completion",
  params: {
    model: "gpt-4",
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: "Say hello!" }
    ],
    max_tokens: 50
  }
})
```

### Test Slack Connection

```javascript
mcp__flow-architect-signature__execute_node_operation({
  node_type: "slack",
  operation: "post_message",
  params: {
    channel: "#general",
    text: "Test message from AI Desktop!"
  }
})
```

## 💡 Tips

1. **Start Small** - Test with a repo that has 1-2 open PRs first
2. **Check Costs** - OpenAI GPT-4 costs ~$0.03-0.10 per review
3. **Channel Permissions** - Ensure your Slack app has permission to post to the channel
4. **Rate Limits** - GitHub allows 5,000 API requests/hour with authentication

## 🚨 Troubleshooting

### "No open PRs found"
- Verify the repository name is correct
- Check that there are actually open PRs in the repo

### "OpenAI API error"
- Verify your OpenAI API key has credits
- Check you have access to GPT-4 models

### "Slack message failed"
- Verify the channel exists
- Check your Slack token permissions
- Try using channel ID instead of name

## 📝 Next Steps

1. Test the workflow with a real repository
2. Customize the AI review prompts
3. Set up scheduled reviews (hourly/daily)
4. Extend to review ALL PRs instead of just the first one
5. Add GitHub webhooks to trigger on PR creation

---

**All services are already authenticated and ready to use!** 🎉
