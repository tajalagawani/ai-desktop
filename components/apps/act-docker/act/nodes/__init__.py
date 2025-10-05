# Import base node first
from .base_node import BaseNode

import logging
logger = logging.getLogger(__name__)

# Core working nodes - prioritize stability over comprehensive coverage
core_imports = [
    # Essential nodes that we know work
    ("PyNode", "PyNode"),
    ("LogMessageNode", "LogMessageNode"), 
    ("OpenaiNode", "OpenAINode"),
    ("IfNode", "IfNode"),
    ("gemini_node", "GeminiNode"),
    ("data_node", "DataNode"),
    ("set_node", "SetNode"),
    ("switch_node", "SwitchNode"),
    ("AggregateNode", "AggregateNode"),
    ("FilterNode", "FilterNode"),
    ("ListNode", "ListNode"),
    ("StartNode", "StartNode"),
]

# Additional nodes to try (may have dependencies)
additional_imports = [
    ("ActionNetworkNode", "ActionNetworkNode"),
    ("ActiveCampaignNode", "ActiveCampaignNode"),
    ("AcuitySchedulingNode", "AcuitySchedulingNode"),
    ("AirtableNode", "AirtableNode"),
    ("AnthropicNode", "AnthropicNode"),
    ("AsanaNode", "AsanaNode"),
    ("Auth0Node", "Auth0Node"),
    ("AwsNode", "AwsNode"),
    ("ClaudeNode", "ClaudeNode"),
    ("ClickUpNode", "ClickUpNode"),
    # ("CodeNode", "CodeNode"),  # Empty file - disabled
    ("CommandNode", "CommandNode"),
    ("DataformatterNode", "DataformatterNode"),
    ("DateTimeNode", "DateTimeNode"),
    ("DiscordNode", "DiscordNode"),
    ("EmailNode", "EmailNode"),
    ("GitHubNode", "GitHubNode"),
    ("GoogleSheetsNode", "GoogleSheetsNode"),
    ("HubSpotNode", "HubSpotNode"),
    ("JiraNode", "JiraNode"),
    ("LinearNode", "LinearNode"),
    ("MongoDBNode", "MongoDBNode"),
    ("NotionNode", "NotionNode"),
    ("PostgreSQLNode", "PostgreSQLNode"),
    ("RedisNode", "RedisNode"),
    ("RequestNode", "RequestNode"),
    ("S3Node", "S3Node"),
    ("SalesforceNode", "SalesforceNode"),
    ("SlackNode", "SlackNode"),
    ("StripeNode", "StripeNode"),
    ("ZoomNode", "ZoomNode"),
]

# Import nodes safely
imported_nodes = {}

def safe_import(module_name, class_name):
    """Safely import a node class"""
    try:
        # Try importing using importlib for better error handling
        import importlib
        if module_name.endswith("_node"):
            # Special nodes with snake_case naming
            module = importlib.import_module(f".{module_name}", package=__name__)
        else:
            # Standard nodes
            module = importlib.import_module(f".{module_name}", package=__name__)
        
        node_class = getattr(module, class_name)
        imported_nodes[class_name] = node_class
        logger.debug(f"✅ Successfully imported {class_name} from {module_name}")
        return node_class
    except Exception as e:
        logger.debug(f"❌ Could not import {class_name} from {module_name}: {e}")
        return None

# Import core nodes first
logger.debug("Importing core ACT nodes...")
for module_name, class_name in core_imports:
    safe_import(module_name, class_name)

# Import additional nodes (may fail)
logger.debug("Importing additional ACT nodes...")
for module_name, class_name in additional_imports:
    safe_import(module_name, class_name)

# Create comprehensive node registry
NODES = {
    "base": BaseNode,
}

# Register core nodes with multiple aliases
if 'PyNode' in imported_nodes:
    NODES["py"] = imported_nodes['PyNode']
    NODES["python"] = imported_nodes['PyNode']

if 'LogMessageNode' in imported_nodes:
    NODES["log_message"] = imported_nodes['LogMessageNode']
    NODES["log"] = imported_nodes['LogMessageNode']

if 'OpenAINode' in imported_nodes:
    NODES["openai"] = imported_nodes['OpenAINode']

if 'IfNode' in imported_nodes:
    NODES["if"] = imported_nodes['IfNode']

if 'GeminiNode' in imported_nodes:
    NODES["gemini"] = imported_nodes['GeminiNode']

if 'DataNode' in imported_nodes:
    NODES["data"] = imported_nodes['DataNode']

if 'SetNode' in imported_nodes:
    NODES["set"] = imported_nodes['SetNode']

if 'SwitchNode' in imported_nodes:
    NODES["switch"] = imported_nodes['SwitchNode']

# Register additional nodes
if 'AggregateNode' in imported_nodes:
    NODES["aggregate"] = imported_nodes['AggregateNode']

if 'FilterNode' in imported_nodes:
    NODES["filter"] = imported_nodes['FilterNode']

if 'ListNode' in imported_nodes:
    NODES["list"] = imported_nodes['ListNode']

if 'StartNode' in imported_nodes:
    NODES["start"] = imported_nodes['StartNode']

if 'ActionNetworkNode' in imported_nodes:
    NODES["action_network"] = imported_nodes['ActionNetworkNode']

if 'ActiveCampaignNode' in imported_nodes:
    NODES["active_campaign"] = imported_nodes['ActiveCampaignNode']

if 'AcuitySchedulingNode' in imported_nodes:
    NODES["acuity_scheduling"] = imported_nodes['AcuitySchedulingNode']

if 'AirtableNode' in imported_nodes:
    NODES["airtable"] = imported_nodes['AirtableNode']

if 'ClaudeNode' in imported_nodes:
    NODES["anthropic"] = imported_nodes['ClaudeNode']
    NODES["claude"] = imported_nodes['ClaudeNode']

if 'AsanaNode' in imported_nodes:
    NODES["asana"] = imported_nodes['AsanaNode']

if 'Auth0Node' in imported_nodes:
    NODES["auth0"] = imported_nodes['Auth0Node']

if 'AwsNode' in imported_nodes:
    NODES["aws"] = imported_nodes['AwsNode']

if 'ClaudeNode' in imported_nodes:
    NODES["claude_node"] = imported_nodes['ClaudeNode']

if 'ClickUpNode' in imported_nodes:
    NODES["clickup"] = imported_nodes['ClickUpNode']

# if 'CodeNode' in imported_nodes:
#     NODES["code"] = imported_nodes['CodeNode']

if 'CommandNode' in imported_nodes:
    NODES["command"] = imported_nodes['CommandNode']

if 'DataformatterNode' in imported_nodes:
    NODES["dataformatter"] = imported_nodes['DataformatterNode']

if 'DateTimeNode' in imported_nodes:
    NODES["datetime"] = imported_nodes['DateTimeNode']

if 'DiscordNode' in imported_nodes:
    NODES["discord"] = imported_nodes['DiscordNode']

if 'EmailNode' in imported_nodes:
    NODES["email"] = imported_nodes['EmailNode']

if 'GitHubNode' in imported_nodes:
    NODES["github"] = imported_nodes['GitHubNode']

if 'GoogleSheetsNode' in imported_nodes:
    NODES["google_sheets"] = imported_nodes['GoogleSheetsNode']

if 'HubSpotNode' in imported_nodes:
    NODES["hubspot"] = imported_nodes['HubSpotNode']

if 'JiraNode' in imported_nodes:
    NODES["jira"] = imported_nodes['JiraNode']

if 'LinearNode' in imported_nodes:
    NODES["linear"] = imported_nodes['LinearNode']

if 'MongoDBNode' in imported_nodes:
    NODES["mongodb"] = imported_nodes['MongoDBNode']

if 'NotionNode' in imported_nodes:
    NODES["notion"] = imported_nodes['NotionNode']

if 'PostgreSQLNode' in imported_nodes:
    NODES["postgresql"] = imported_nodes['PostgreSQLNode']

if 'RedisNode' in imported_nodes:
    NODES["redis"] = imported_nodes['RedisNode']

if 'RequestNode' in imported_nodes:
    NODES["request"] = imported_nodes['RequestNode']

if 'S3Node' in imported_nodes:
    NODES["s3"] = imported_nodes['S3Node']

if 'SalesforceNode' in imported_nodes:
    NODES["salesforce"] = imported_nodes['SalesforceNode']

if 'SlackNode' in imported_nodes:
    NODES["slack"] = imported_nodes['SlackNode']

if 'StripeNode' in imported_nodes:
    NODES["stripe"] = imported_nodes['StripeNode']

if 'ZoomNode' in imported_nodes:
    NODES["zoom"] = imported_nodes['ZoomNode']

# Log successful registrations
logger.debug(f"Successfully registered {len(NODES)} node types: {list(NODES.keys())}")

# Export the complete registry
__all__ = ['NODES', 'BaseNode'] + list(imported_nodes.keys())