[signature]
version = "1.0.0"
created_at = "2025-10-22T19:56:29.212Z"
updated_at = "2025-10-22T19:56:30.585374Z"

[metadata]
authenticated_nodes = 1
last_updated = "2025-10-22T19:56:30.585370Z"

["node:github"]
type = "github"
enabled = true
authenticated = true
display_name = "Github"
description = "Pure config-driven GitHub node with embedded configuration."
added_at = "2025-10-22T19:56:29.212Z"

["node:github.auth"]
access_token = "{{.env.GITHUB_ACCESS_TOKEN}}"

["node:github.operations".list_repos]
description = "List Repositories operation"
category = "read"

["node:github.operations".get_user]
description = "Get User operation"
category = "read"
