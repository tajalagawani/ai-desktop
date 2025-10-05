# === File: act/nodes/google_docs_node.py ===

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Union

import httpx

# Assuming base_node.py is in the same directory or accessible via the package structure
try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    class NodeValidationError(Exception): pass
    class NodeExecutionError(Exception): pass
    class NodeParameterType: ANY="any"; STRING="string"; BOOLEAN="boolean"; NUMBER="number"; ARRAY="array"; OBJECT="object"; SECRET="secret"
    class NodeParameter:
        def __init__(self, name, type, description, required=True, default=None, enum=None):
            self.name = name; self.type = type; self.description = description; self.required = required; self.default = default; self.enum = enum
    class NodeSchema:
        def __init__(self, node_type, version, description, parameters, outputs, tags=None, author=None):
            self.node_type=node_type; self.version=version; self.description=description; self.parameters=parameters; self.outputs=outputs; self.tags=tags; self.author=author
    class BaseNode:
        def get_schema(self): raise NotImplementedError
        async def execute(self, data): raise NotImplementedError
        def validate_schema(self, data): return data.get("params", {})
        def handle_error(self, error, context=""):
             logger = logging.getLogger(__name__)
             logger.error(f"Error in {context}: {error}", exc_info=True)
             return {"status": "error", "message": f"Error in {context}: {error}", "error_type": type(error).__name__}

# --- Node Logger ---
logger = logging.getLogger(__name__)

class GoogleDocsOperation:
    """Operations available for the Google Docs API."""
    CREATE_DOCUMENT = "documents.create"
    GET_DOCUMENT = "documents.get"
    BATCH_UPDATE_DOCUMENT = "documents.batchUpdate"

class GoogleDocsNode(BaseNode):
    _BASE_API_URL = "https://docs.googleapis.com/v1"

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            node_type="google_docs",
            version="1.0.0",
            description="Interacts with the Google Docs API to create, read, and update documents.",
            parameters=[
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 Access Token for Google Docs API.",
                    required=True
                ),
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="The Google Docs API method to call.",
                    required=True,
                    enum=[op for op in dir(GoogleDocsOperation) if not op.startswith('_')]
                ),
                NodeParameter(
                    name="document_id",
                    type=NodeParameterType.STRING,
                    description="The ID of the Google Document. Required for 'get' and 'batchUpdate'.",
                    required=False
                ),
                NodeParameter(
                    name="title",
                    type=NodeParameterType.STRING,
                    description="The title of the document. Used when creating a new document.",
                    required=False
                ),
                NodeParameter(
                    name="body_content", # For create: directly the 'body' object of a Document
                    type=NodeParameterType.OBJECT,
                    description="The body of the document (Document.body structure). Used when creating a new document.",
                    required=False
                ),
                NodeParameter(
                    name="requests", # For batchUpdate: list of Request objects
                    type=NodeParameterType.ARRAY,
                    description="A JSON-serialized list of UpdateRequests to apply to the document. Used for 'documents.batchUpdate'.",
                    required=False
                ),
                NodeParameter( # For get
                    name="fields",
                    type=NodeParameterType.STRING,
                    description="A mask specifying which fields to return in a 'get' request (e.g., 'documentId,title,body.content'). Use '*' for all fields.",
                    required=False
                ),
                NodeParameter( # For batchUpdate
                    name="write_control",
                    type=NodeParameterType.OBJECT,
                    description="Provides control over how write requests are executed (e.g., {\"requiredRevisionId\": \"id\"}). Used for 'documents.batchUpdate'.",
                    required=False
                ),
                NodeParameter( # For get
                    name="suggestions_view_mode",
                    type=NodeParameterType.STRING,
                    description="The suggestions view mode for 'documents.get'.",
                    enum=["DEFAULT_FOR_DRIVE", "SUGGESTIONS_INLINE", "PREVIEW_SUGGESTIONS_ACCEPTED", "PREVIEW_WITHOUT_SUGGESTIONS"],
                    required=False
                ),
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "document_id_out": NodeParameterType.STRING,
                "response_headers": NodeParameterType.OBJECT,
                "error_message": NodeParameterType.STRING
            },
            tags=["google", "docs", "document", "editor", "productivity", "office"],
            author="ACT Framework"
        )

    async def _send_request(
        self,
        access_token: str,
        http_method: str,
        endpoint: str,
        query_params: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        if json_payload and http_method.upper() != "GET":
            headers["Content-Type"] = "application/json"

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                logger.debug(f"Sending {http_method} request to {self._BASE_API_URL}{endpoint} with params: {query_params}, payload: {json.dumps(json_payload)[:200] if json_payload else None}")
                response = await client.request(
                    method=http_method.upper(),
                    url=f"{self._BASE_API_URL}{endpoint}",
                    params=query_params,
                    json=json_payload,
                    headers=headers
                )
                return self._format_google_response(response)
            except httpx.RequestError as e:
                logger.error(f"HTTPX RequestError for {endpoint}: {e}", exc_info=True)
                return {"status": "error", "result": None, "document_id_out": None, "response_headers": {}, "error_message": f"HTTP request failed: {e}"}
            except Exception as e:
                logger.error(f"Unexpected error during Google Docs request for {endpoint}: {e}", exc_info=True)
                return {"status": "error", "result": None, "document_id_out": None, "response_headers": {}, "error_message": f"Internal error: {e}"}

    def _format_google_response(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            response_json = response.json() if response.content else {}
            is_success = 200 <= response.status_code < 300
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON response from Google. Status: {response.status_code}, Content: {response.text[:500]}")
            return {
                "status": "error",
                "result": None,
                "document_id_out": None,
                "response_headers": dict(response.headers),
                "error_message": f"Invalid JSON response from Google (Status: {response.status_code}). Content: {response.text[:200]}"
            }

        output = {
            "status": "success" if is_success else "error",
            "result": response_json,
            "document_id_out": response_json.get("documentId") if is_success and isinstance(response_json, dict) else None,
            "response_headers": dict(response.headers),
            "error_message": None
        }

        if not is_success:
            error_details = response_json.get("error", {}) if isinstance(response_json, dict) else {}
            output["error_message"] = error_details.get("message", f"Google API Error (Status: {response.status_code}, Message: {response.text[:200]})")
            logger.error(f"Google Docs API Error: Status={response.status_code}, Message={output['error_message']}, Details={error_details}")
        return output

    async def validate_custom(self, params: Dict[str, Any]) -> None:
        operation = params.get("operation")
        if not operation:
            raise NodeValidationError("Parameter 'operation' is required.")
        if not params.get("access_token"):
            raise NodeValidationError("Parameter 'access_token' is required.")

        if operation == GoogleDocsOperation.CREATE_DOCUMENT:
            # title is optional, body_content is optional for an empty doc
            pass
        elif operation == GoogleDocsOperation.GET_DOCUMENT:
            if not params.get("document_id"):
                raise NodeValidationError(f"Parameter 'document_id' is required for operation '{operation}'.")
        elif operation == GoogleDocsOperation.BATCH_UPDATE_DOCUMENT:
            if not params.get("document_id"):
                raise NodeValidationError(f"Parameter 'document_id' is required for operation '{operation}'.")
            if not params.get("requests") or not isinstance(params.get("requests"), list):
                raise NodeValidationError(f"Parameter 'requests' (a list of update operations) is required for operation '{operation}'.")
        else:
            raise NodeValidationError(f"Unsupported operation: {operation}")

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        params = node_data.get("params", {})
        node_name = node_data.get('__node_name', 'GoogleDocsNode')
        logger.debug(f"Executing {node_name} with operation: {params.get('operation')}")

        try:
            await self.validate_custom(params)
            access_token = params.get("access_token")
            operation = params.get("operation")

            if operation == GoogleDocsOperation.CREATE_DOCUMENT:
                title = params.get("title")
                body_content = params.get("body_content") # This is the Document.body structure
                payload = {}
                if title:
                    payload["title"] = title
                if body_content: # If user provides the 'body' object part of Document resource
                    payload["body"] = body_content
                # If neither title nor body_content is provided, an empty document is created by default by API
                return await self._send_request(access_token, "POST", "/documents", json_payload=payload)

            elif operation == GoogleDocsOperation.GET_DOCUMENT:
                document_id = params.get("document_id")
                query_params = {}
                if params.get("fields"):
                    query_params["fields"] = params.get("fields")
                if params.get("suggestions_view_mode"):
                    query_params["suggestionsViewMode"] = params.get("suggestions_view_mode")
                return await self._send_request(access_token, "GET", f"/documents/{document_id}", query_params=query_params)

            elif operation == GoogleDocsOperation.BATCH_UPDATE_DOCUMENT:
                document_id = params.get("document_id")
                requests_payload = params.get("requests") # This is a list of Request objects
                write_control = params.get("write_control")
                payload = {"requests": requests_payload}
                if write_control:
                    payload["writeControl"] = write_control
                return await self._send_request(access_token, "POST", f"/documents/{document_id}:batchUpdate", json_payload=payload)

            else:
                return self.handle_error(NodeExecutionError(f"Operation '{operation}' is not implemented."), context=node_name)

        except NodeValidationError as e:
            logger.error(f"Validation Error in {node_name}: {e}")
            return self.handle_error(e, context=f"{node_name} Validation")
        except Exception as e:
            logger.error(f"Unexpected Error in {node_name}: {e}", exc_info=True)
            return self.handle_error(e, context=f"{node_name} Execution")


# --- Main Block for Standalone Testing (Illustrative) ---
if __name__ == "__main__":
    import os
    import urllib.parse

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s')

    # --- OAuth 2.0 Configuration - Use Environment Variables ---
    # 1. Client ID and Client Secret for your OAuth 2.0 application
    #    (You can create these in Google Cloud Console: APIs & Services > Credentials)
    #    For testing, the Google OAuth Playground often uses a pre-configured client.
    #    If using the playground's default client for generating the auth code:
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_PLAYGROUND_CLIENT_ID", "407408718192.apps.googleusercontent.com") # Playground's default
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_PLAYGROUND_CLIENT_SECRET", "YOUR_PLAYGROUND_CLIENT_SECRET_IF_APPLICABLE") # Playground's default often doesn't need this for token exchange if using its own proxy

    # 2. Redirect URI - Must match one configured for your client ID
    REDIRECT_URI = "https://developers.google.com/oauthplayground" # For OAuth Playground

    # 3. Authorization Code - THIS YOU NEED TO GET MANUALLY FOR EACH TEST RUN
    #    - Construct the authorization URL (see get_authorization_url function below)
    #    - Visit it in your browser, sign in, grant consent.
    #    - Google will redirect you to your REDIRECT_URI with a `code` parameter in the URL.
    #    - Copy that `code` value here.
    AUTHORIZATION_CODE = os.environ.get("GOOGLE_AUTH_CODE")

    # --- Helper to construct authorization URL (for manual step) ---
    def get_authorization_url(client_id, redirect_uri, scopes):
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",  # Request a refresh token
            "prompt": "consent"      # Force consent screen to ensure refresh token
        }
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
        return auth_url

    # --- Function to Exchange Authorization Code for Tokens ---
    async def get_access_token(auth_code, client_id, client_secret, redirect_uri) -> Optional[str]:
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": auth_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(token_url, data=payload, headers=headers)
                response.raise_for_status() # Raise an exception for bad status codes
                token_data = response.json()
                logger.info(f"Successfully obtained access token. Expires in: {token_data.get('expires_in')}s")
                if "refresh_token" in token_data:
                    logger.info(f"Obtained refresh token (store securely for future use): {token_data['refresh_token']}")
                else:
                    logger.warning("Refresh token not received. This might happen if 'access_type=offline' and 'prompt=consent' were not used, or if it's not the first time authorizing this client for these scopes.")
                return token_data.get("access_token")
            except httpx.HTTPStatusError as e:
                logger.error(f"Error exchanging auth code for token: {e.response.status_code} - {e.response.text}")
                return None
            except Exception as e:
                logger.error(f"Exception during token exchange: {e}")
                return None

    async def main_test_flow():
        node = GoogleDocsNode()
        created_doc_id = None
        print("\n--- Testing GoogleDocsNode with Programmatic Token Fetch ---")

        if not AUTHORIZATION_CODE:
            scopes_needed = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive.file"] # drive.file might be needed by playground for creation in some contexts
            auth_url_to_visit = get_authorization_url(GOOGLE_CLIENT_ID, REDIRECT_URI, scopes_needed)
            print("ERROR: GOOGLE_AUTH_CODE environment variable is not set.")
            print("Please obtain an authorization code by visiting the following URL in your browser:")
            print(auth_url_to_visit)
            print("After authorizing, Google will redirect you. Copy the 'code' value from the redirect URL's query parameters.")
            print("Then set it as the GOOGLE_AUTH_CODE environment variable and re-run.")
            return

        print("1. Attempting to get access token...")
        # Note: For the playground's default client, the client_secret might not be strictly required
        # if the token exchange is proxied through the playground itself.
        # If you use your own client ID, client_secret is essential.
        # For simplicity with playground, if GOOGLE_CLIENT_SECRET is not set, we might still proceed.
        # However, the provided CURL example *does* show a client_secret.
        # Let's assume it's needed for a direct POST to oauth2.googleapis.com.
        if GOOGLE_CLIENT_ID == "407408718192.apps.googleusercontent.com" and not os.environ.get("GOOGLE_OAUTH_PLAYGROUND_CLIENT_SECRET"):
             logger.warning("GOOGLE_OAUTH_PLAYGROUND_CLIENT_SECRET not set. Token exchange might fail if directly calling Google's token endpoint with the playground client ID without its secret.")
             # The provided curl uses "************" which implies it's a placeholder and the actual secret is used.
             # If you're truly using the playground client ID without its secret, this step will likely fail.
             # You might need to perform the token exchange via the OAuth Playground UI itself first if you don't have the secret.

        TEST_ACCESS_TOKEN = await get_access_token(
            AUTHORIZATION_CODE,
            GOOGLE_CLIENT_ID,
            GOOGLE_CLIENT_SECRET, # This should be the actual secret if using your own client or playground's if known
            REDIRECT_URI
        )

        if not TEST_ACCESS_TOKEN:
            print("Failed to obtain access token. Aborting tests.")
            return

        print("Access token obtained successfully.")

        # Test 2: Create Document
        print("\n2. Testing CREATE_DOCUMENT...")
        create_payload = {
            "params": {
                "access_token": TEST_ACCESS_TOKEN,
                "operation": GoogleDocsOperation.CREATE_DOCUMENT,
                "title": "My ACT Auto-Token Test Document",
                "body_content": {
                    "content": [
                        {"paragraph": {"elements": [{"textRun": {"content": "Token fetched programmatically!\n"}}]}},
                        {"paragraph": {"elements": [{"textRun": {"content": "Second Paragraph."}}], "paragraphStyle": {"namedStyleType": "HEADING_2"}}}
                    ]
                }
            }
        }
        create_result = await node.execute(create_payload)
        print(f"Create Document Result: {json.dumps(create_result, indent=2)}")
        if create_result["status"] == "success":
            created_doc_id = create_result.get("result", {}).get("documentId")
            assert created_doc_id is not None
            print(f"Created Document ID: {created_doc_id}")
        else:
            print(f"Document creation failed: {create_result.get('error_message')}")


        if created_doc_id:
            # Test 3: Get Document
            print("\n3. Testing GET_DOCUMENT...")
            await asyncio.sleep(2)
            get_payload = {
                "params": {
                    "access_token": TEST_ACCESS_TOKEN,
                    "operation": GoogleDocsOperation.GET_DOCUMENT,
                    "document_id": created_doc_id,
                    "fields": "documentId,title,body.content.paragraph.elements.textRun.content"
                }
            }
            get_result = await node.execute(get_payload)
            print(f"Get Document Result: {json.dumps(get_result, indent=2)}")
            assert get_result["status"] == "success"
            assert get_result.get("result", {}).get("title") == "My ACT Auto-Token Test Document"


            # Test 4: Batch Update Document
            print("\n4. Testing BATCH_UPDATE_DOCUMENT...")
            batch_update_payload = {
                "params": {
                    "access_token": TEST_ACCESS_TOKEN,
                    "operation": GoogleDocsOperation.BATCH_UPDATE_DOCUMENT,
                    "document_id": created_doc_id,
                    "requests": [
                        {"insertText": {"location": {"index": 1}, "text": "BATCH UPDATE TEST: "}}
                    ]
                }
            }
            batch_result = await node.execute(batch_update_payload)
            print(f"Batch Update Result: {json.dumps(batch_result, indent=2)}")
            assert batch_result["status"] == "success"
            assert batch_result.get("result", {}).get("documentId") == created_doc_id


            # Verify update by getting again
            print("\n5. Verifying BATCH_UPDATE_DOCUMENT by GET...")
            await asyncio.sleep(2)
            get_updated_result = await node.execute(get_payload)
            print(f"Get Updated Document Result: {json.dumps(get_updated_result, indent=2)}")
            assert get_updated_result["status"] == "success"
            assert "BATCH UPDATE TEST: Token fetched programmatically!" in json.dumps(get_updated_result.get("result", {}).get("body"))

            print(f"\n--- IMPORTANT: Manually delete the test document '{created_doc_id}' from your Google Drive if needed. ---")
        else:
            print("Skipping further tests as document creation failed or was skipped.")

        print("\n✅ GoogleDocsNode tests with programmatic token fetch completed.")

    asyncio.run(main_test_flow())