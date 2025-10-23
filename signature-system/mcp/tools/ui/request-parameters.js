/**
 * RequestParameters MCP Tool
 *
 * Shows an interactive form in chat to collect parameters from the user.
 * This creates a special message that the chat UI will render as ParameterCollectionForm component.
 */

export default {
  name: 'request_parameters',
  description: 'Show interactive form in chat to collect parameters from user',
  inputSchema: {
    type: 'object',
    properties: {
      title: {
        type: 'string',
        description: 'Form title (e.g., "GitHub Repository Information")'
      },
      description: {
        type: 'string',
        description: 'Optional form description explaining what info is needed'
      },
      fields: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Field name/identifier'
            },
            type: {
              type: 'string',
              enum: ['text', 'number', 'email', 'password', 'url'],
              description: 'Input field type'
            },
            label: {
              type: 'string',
              description: 'Field label shown to user'
            },
            description: {
              type: 'string',
              description: 'Optional helper text below field'
            },
            required: {
              type: 'boolean',
              description: 'Whether field is required'
            },
            placeholder: {
              type: 'string',
              description: 'Placeholder text'
            },
            defaultValue: {
              type: 'string',
              description: 'Default value'
            }
          },
          required: ['name', 'type', 'label']
        },
        description: 'Array of form fields to collect'
      },
      submit_label: {
        type: 'string',
        description: 'Submit button label (default: "Submit")'
      }
    },
    required: ['title', 'fields']
  },

  async execute({ title, description, fields, submit_label }) {
    // Validate fields
    if (!Array.isArray(fields) || fields.length === 0) {
      throw new Error('At least one field is required');
    }

    // Return MCP format with UI component data
    const responseData = {
      success: true,
      ui_component: 'ParameterCollectionForm',
      data: {
        title,
        description,
        fields,
        submitLabel: submit_label || 'Submit'
      },
      message: `Interactive form shown with ${fields.length} field(s). User will fill and submit.`
    };

    return {
      content: [{
        type: 'text',
        text: JSON.stringify(responseData, null, 2)
      }]
    };
  }
};
