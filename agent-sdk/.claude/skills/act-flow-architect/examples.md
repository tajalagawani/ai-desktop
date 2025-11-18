# ACT Flow Examples

## Example 1: Simple API

```toml
[workflow]
name = "Hello World API"
start_node = "HelloAPI"

[node.HelloAPI]
type = "py"
operation = "execute"
code = """
def hello(**kwargs):
    return {
        'result': {
            'message': 'Hello World!',
            'status': 'success'
        }
    }
"""
function = "hello"

[edges]
HelloAPI = []

[configuration]
agent_enabled = true
agent_port = 9000
```

## Example 2: GitHub to Slack Integration

```toml
[workflow]
name = "GitHub Issues to Slack"
start_node = "FetchIssues"

[parameters]
github_token = { type = "secret", required = true }
repo_owner = { type = "string", required = true }
repo_name = { type = "string", required = true }

[node.FetchIssues]
type = "github"
operation = "list_issues"
owner = "{{.Parameter.repo_owner}}"
repo = "{{.Parameter.repo_name}}"
token = "{{.Parameter.github_token}}"
state = "open"

[node.FormatMessage]
type = "py"
operation = "execute"
code = """
def format(**kwargs):
    issues = kwargs.get('FetchIssues', {}).get('result', [])
    message = f"Found {len(issues)} open issues:\\n"
    for issue in issues[:5]:
        message += f"- #{issue['number']}: {issue['title']}\\n"
    return {'result': message}
"""
function = "format"

[node.PostToSlack]
type = "slack"
operation = "post_message"
channel = "#github-updates"
text = "{{FormatMessage.result}}"

[edges]
FetchIssues = "FormatMessage"
FormatMessage = "PostToSlack"
```

## Example 3: Scheduled Data Sync

```toml
[workflow]
name = "Daily Database Backup"
start_node = "Schedule"

[parameters]
database_url = { type = "secret", required = true }
s3_bucket = { type = "string", required = true }

[node.Schedule]
type = "timer"
schedule = "0 2 * * *"  # 2 AM daily
mode = "cron"
timezone = "UTC"
handler = "BackupDatabase"

[node.BackupDatabase]
type = "neon"
operation = "backup"
connection_string = "{{.Parameter.database_url}}"

[node.UploadToS3]
type = "s3"
operation = "upload"
bucket = "{{.Parameter.s3_bucket}}"
key = "backup-{{timestamp}}.sql"
file = "{{BackupDatabase.result.backup_file}}"

[node.NotifySuccess]
type = "slack"
operation = "post_message"
channel = "#alerts"
text = "Database backup completed successfully"

[edges]
Schedule = []
BackupDatabase = "UploadToS3"
UploadToS3 = "NotifySuccess"
```

## Example 4: ETL Pipeline

```toml
[workflow]
name = "API to Database ETL"
start_node = "ExtractData"

[node.ExtractData]
type = "py"
operation = "execute"
code = """
import requests

def extract(**kwargs):
    response = requests.get('https://api.example.com/data', timeout=30)
    response.raise_for_status()
    return {'result': response.json()}
"""
function = "extract"

[node.TransformData]
type = "py"
operation = "execute"
code = """
def transform(**kwargs):
    raw_data = kwargs.get('ExtractData', {}).get('result', [])
    transformed = []
    for item in raw_data:
        transformed.append({
            'id': item['id'],
            'name': item['name'].upper(),
            'value': float(item['value'])
        })
    return {'result': transformed}
"""
function = "transform"

[node.LoadToDatabase]
type = "neon"
operation = "bulk_insert"
connection_string = "{{.Parameter.database_url}}"
table = "processed_data"
data = "{{TransformData.result}}"

[edges]
ExtractData = "TransformData"
TransformData = "LoadToDatabase"
```
