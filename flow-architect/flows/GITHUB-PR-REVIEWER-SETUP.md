# GitHub PR Reviewer with OpenAI and Slack

## Overview

This workflow automatically reviews all new GitHub pull requests using OpenAI's GPT-4 and posts the review summaries to Slack.

## Workflow File

`flows/github-pr-reviewer.flow`

## What It Does

1. **Fetches Open PRs** - Gets all open pull requests from your GitHub repository
2. **Extracts PR Details** - Collects PR metadata (title, author, description, etc.)
3. **Fetches PR Diff** - Downloads the actual code changes
4. **Formats for AI** - Prepares the diff for OpenAI analysis
5. **AI Review** - Sends to OpenAI GPT-4 for code review analysis
6. **Extracts Review** - Parses the AI-generated review
7. **Formats Slack Message** - Creates a rich Slack message with the review
8. **Sends to Slack** - Posts the review to your Slack channel
9. **Logs Success** - Records the successful review

## Required Environment Variables

Before running this workflow, you need to set up the following environment variables in your `.env` file:

### 1. GitHub Access Token

```bash
GITHUB_ACCESS_TOKEN="ghp_your_github_personal_access_token"
GITHUB_OWNER="your-github-username"
GITHUB_REPO="your-repo-name"
```

**How to get a GitHub token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name (e.g., "PR Reviewer")
4. Select scopes:
   - `repo` (full control of private repositories)
   - `read:org` (if reviewing org repos)
5. Click "Generate token"
6. Copy the token immediately (you won't see it again)

### 2. OpenAI API Key

```bash
OPENAI_API_KEY="sk-proj-your_openai_api_key"
```

**How to get an OpenAI API key:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Give it a name (e.g., "PR Reviewer")
4. Copy the key immediately

**Note:** This workflow uses GPT-4o which requires OpenAI API credits. Check your usage at https://platform.openai.com/usage

### 3. Slack Webhook URL

```bash
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**How to create a Slack webhook:**
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Give it a name (e.g., "PR Reviewer Bot")
4. Select your workspace
5. Go to "Incoming Webhooks"
6. Toggle "Activate Incoming Webhooks" to On
7. Click "Add New Webhook to Workspace"
8. Select the channel where you want PR reviews posted
9. Copy the webhook URL

## Setup Instructions

### Step 1: Create `.env` file

In the `flow-architect` directory, create a `.env` file:

```bash
cd /Users/tajnoah/Downloads/ai-desktop/flow-architect
touch .env
```

### Step 2: Add your credentials

Edit `.env` and add:

```bash
# GitHub Configuration
GITHUB_ACCESS_TOKEN="ghp_your_token_here"
GITHUB_OWNER="your-username"
GITHUB_REPO="your-repo-name"

# OpenAI Configuration
OPENAI_API_KEY="sk-proj-your_key_here"

# Slack Configuration
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Step 3: Verify the workflow file

Make sure `flows/github-pr-reviewer.flow` exists and is properly formatted.

### Step 4: Execute the workflow

**Option A: Via API**

```bash
curl -X POST http://localhost:3000/api/act/execute \
  -H "Content-Type: application/json" \
  -d '{
    "flowPath": "flows/github-pr-reviewer.flow"
  }'
```

**Option B: Via command line (if ACT CLI is available)**

```bash
act execute flows/github-pr-reviewer.flow
```

## What the AI Review Includes

The OpenAI review provides:

1. **Summary of changes** - High-level overview of what the PR does
2. **Potential issues or bugs** - Code that might cause problems
3. **Security concerns** - Security vulnerabilities or risks
4. **Code quality suggestions** - Best practices and improvements
5. **Overall recommendation** - Approve, request changes, or comment

## Slack Message Format

The Slack message includes:

- **Header** - PR number and title
- **Metadata** - Files changed count
- **AI Review** - Full review from OpenAI
- **Button** - Direct link to view PR on GitHub

## Example Output

When a PR is reviewed, you'll see a Slack message like:

```
🤖 AI PR Review #42

PR Title: Add user authentication feature
Files Changed: 5

AI Review:
Summary of changes:
- Implements JWT-based authentication
- Adds login/logout endpoints
- Creates User model and middleware

Potential issues:
- Password storage should use bcrypt with higher cost factor
- Missing input validation on email field

Security concerns:
- JWT secret should be stored in environment variables
- Consider adding rate limiting on login endpoint

Code quality:
- Good separation of concerns
- Tests are comprehensive
- Consider extracting middleware to separate file

Overall recommendation: Request changes
Address the security concerns before merging.

[View PR on GitHub] ← clickable button
```

## Customization

You can customize the workflow by editing `flows/github-pr-reviewer.flow`:

### Change AI Model

In the `ReviewWithOpenAI` node, change:
```toml
model = "gpt-4o"  # Can use "gpt-3.5-turbo" for cheaper reviews
```

### Adjust Review Length

Change `max_tokens`:
```toml
max_tokens = 1500  # Increase for longer reviews
```

### Filter PRs

Modify `FetchOpenPRs` to add filters:
```toml
params = {
    owner = "{{.Parameter.github_owner}}",
    repo = "{{.Parameter.github_repo}}",
    state = "open",
    base = "main"  # Only PRs targeting main branch
}
```

## Scheduling

To automatically review new PRs, you can:

### Option 1: Add a timer node

Add to the workflow:

```toml
[node:ScheduleReviews]
type = "timer"
label = "Check for new PRs every hour"
schedule = "0 * * * *"  # Every hour
mode = "cron"
timezone = "UTC"
handler = "FetchOpenPRs"
```

### Option 2: GitHub Webhook

Set up a webhook to trigger reviews when PRs are opened:
1. Go to your repo settings → Webhooks
2. Add webhook URL: `http://your-server:3000/api/webhooks/pr-opened`
3. Select events: Pull requests (opened, synchronized)

## Troubleshooting

### "No PRs found"

- Check that `GITHUB_OWNER` and `GITHUB_REPO` are correct
- Verify your GitHub token has `repo` scope
- Ensure there are actually open PRs in the repo

### "OpenAI API error"

- Verify your API key is correct
- Check you have credits: https://platform.openai.com/usage
- Ensure you have access to GPT-4 models

### "Slack webhook failed"

- Verify the webhook URL is correct
- Check the Slack app is installed in your workspace
- Ensure the channel still exists

### "Module build failed"

- This error is from the Next.js dev server, not the workflow
- The workflow execution API should still work
- Restart the server: `npm run dev`

## Cost Estimates

**OpenAI API costs (approximate):**
- Small PR (< 500 lines): $0.01 - 0.02
- Medium PR (500-2000 lines): $0.02 - 0.05
- Large PR (> 2000 lines): $0.05 - 0.15

**GitHub API:** Free (rate limit: 5,000 requests/hour with token)

**Slack:** Free

## Next Steps

1. **Test with a single PR** - Start with one PR to verify setup
2. **Add scheduling** - Automate reviews for new PRs
3. **Customize prompts** - Adjust the AI review criteria
4. **Add webhooks** - Trigger reviews on PR events
5. **Expand integrations** - Add Linear, Jira, or other tools

## Support

For issues or questions:
- Check the logs in the workflow execution response
- Verify all environment variables are set
- Test each API credential independently
