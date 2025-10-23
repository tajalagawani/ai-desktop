'use client';

import ReactMarkdown from 'react-markdown';
import { NodeAuthRequest } from './NodeAuthRequest';
import { ParameterCollectionForm } from './ParameterCollectionForm';

interface InteractiveMarkdownProps {
  content: string;
  isDarkMode?: boolean;
}

/**
 * Parses markdown and renders interactive components for special patterns
 *
 * Patterns:
 * 1. [🛡️ Authenticate NodeName →] → Renders NodeAuthRequest
 * 2. 📝 FORM: {...} → Renders ParameterCollectionForm
 */
export function InteractiveMarkdown({ content, isDarkMode = false }: InteractiveMarkdownProps) {
  // Check if content contains auth button pattern
  const authButtonPattern = /\[🛡️ Authenticate (.*?) →\]/g;
  const authMatch = authButtonPattern.exec(content);

  if (authMatch) {
    const nodeName = authMatch[1];
    const nodeType = nodeName.toLowerCase();

    // Extract required auth from markdown if present
    const requiredAuthPattern = /- `(.*?)` -/g;
    const requiredAuth: string[] = [];
    let match;
    while ((match = requiredAuthPattern.exec(content)) !== null) {
      requiredAuth.push(match[1]);
    }

    // Render the content before the button + the interactive component
    const contentBeforeButton = content.substring(0, authMatch.index);
    const contentAfterButton = content.substring(authMatch.index + authMatch[0].length);

    return (
      <div>
        <ReactMarkdown>{contentBeforeButton}</ReactMarkdown>
        <NodeAuthRequest
          nodeType={nodeType}
          nodeName={nodeName}
          requiredAuth={requiredAuth}
          reason={`${nodeName} authentication is required to continue`}
        />
        <ReactMarkdown>{contentAfterButton}</ReactMarkdown>
      </div>
    );
  }

  // Check if content contains form pattern
  const formPattern = /📝 FORM: (\{[\s\S]*?\})/;
  const formMatch = formPattern.exec(content);

  if (formMatch) {
    try {
      const formConfig = JSON.parse(formMatch[1]);

      return (
        <div>
          <ReactMarkdown>{content.substring(0, formMatch.index)}</ReactMarkdown>
          <ParameterCollectionForm
            title={formConfig.title || 'Information Required'}
            description={formConfig.description}
            fields={formConfig.fields || []}
            onSubmit={(values) => {
              console.log('Form submitted:', values);
              window.dispatchEvent(new CustomEvent('parameter-submitted', {
                detail: { values }
              }));
            }}
            submitLabel={formConfig.submitLabel || 'Submit'}
          />
          <ReactMarkdown>{content.substring(formMatch.index + formMatch[0].length)}</ReactMarkdown>
        </div>
      );
    } catch (error) {
      console.error('Failed to parse form config:', error);
    }
  }

  // No special patterns, render normal markdown
  return <ReactMarkdown>{content}</ReactMarkdown>;
}
