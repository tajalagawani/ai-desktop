/**
 * RequestNodeAuth MCP Tool
 *
 * Shows an interactive authentication button in chat when a node needs auth.
 * This creates a special message that the chat UI will render as NodeAuthRequest component.
 */

export default {
  name: 'request_node_auth',
  description: 'Show interactive authentication button in chat for a node that requires authentication',
  inputSchema: {
    type: 'object',
    properties: {
      node_type: {
        type: 'string',
        description: 'Node type identifier (e.g., "github", "slack", "openai")'
      },
      node_name: {
        type: 'string',
        description: 'Human-readable node name (e.g., "GitHub", "Slack", "OpenAI")'
      },
      required_auth: {
        type: 'array',
        items: { type: 'string' },
        description: 'List of required authentication fields (e.g., ["access_token", "api_key"])'
      },
      reason: {
        type: 'string',
        description: 'Why authentication is needed (shown to user)'
      }
    },
    required: ['node_type', 'node_name']
  },

  async execute({ node_type, node_name, required_auth = [], reason }) {
    // Simple text message for terminal/CLI mode
    const authFieldsText = required_auth.length > 0
      ? `\n\nRequired fields:\n${required_auth.map(f => `  • ${f}`).join('\n')}`
      : '';

    const textMessage = `🔐 ${node_name} Authentication Required\n\n${reason || `${node_name} authentication is required to continue.`}${authFieldsText}\n\nPlease open Security Center to add your ${node_name} authentication.`;

    return {
      content: [{
        type: 'text',
        text: textMessage
      }]
    };
  }
};
