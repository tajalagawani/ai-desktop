'use client';

import { ChevronRightIcon } from 'lucide-react';
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemMedia,
  ItemTitle,
} from '@/components/action-builder/ui/item';

interface Topic {
  id: string;
  icon: string;
  name: string;
  context: string;
  description: string;
  example: string;
}

const TOPICS: Topic[] = [
  {
    id: 'math',
    icon: '📊',
    name: 'Math & Calculations',
    context: 'simple-calculation.md',
    description: 'Simple calculations and math operations',
    example: '"what is 5+5", "calculate 25% of 200"'
  },
  {
    id: 'random',
    icon: '🎲',
    name: 'Random & Games',
    context: 'random-generation.md',
    description: 'Generate random numbers, pick random choices',
    example: '"pick a number between 1 and 100", "guess a number"'
  },
  {
    id: 'fetch',
    icon: '🌐',
    name: 'Data Fetch',
    context: 'data-fetch.md',
    description: 'Fetch data from external APIs',
    example: '"get ISS location", "current weather in NYC"'
  },
  {
    id: 'scheduled',
    icon: '⏰',
    name: 'Scheduled Tasks',
    context: 'scheduled-task.md',
    description: 'Create cron jobs and scheduled workflows',
    example: '"check price every hour", "send report daily"'
  },
  {
    id: 'simple-api',
    icon: '🔧',
    name: 'Simple API',
    context: 'simple-api.md',
    description: 'Create REST APIs with 2-5 endpoints',
    example: '"create quotes API", "build notes API"'
  },
  {
    id: 'complex-api',
    icon: '🏗️',
    name: 'Complex API',
    context: 'complex-api.md',
    description: 'Create REST APIs with 6-15 endpoints',
    example: '"todo API with categories", "blog API with auth"'
  },
  {
    id: 'full-app',
    icon: '🏢',
    name: 'Full Application',
    context: 'full-application.md',
    description: 'Complete systems with 30+ endpoints',
    example: '"restaurant management system", "school LMS"'
  },
  {
    id: 'multi-service',
    icon: '🔗',
    name: 'Multi-Service',
    context: 'multi-service-integration.md',
    description: 'Workflows integrating multiple services',
    example: '"monitor and alert via Slack", "fetch and store in DB"'
  },
  {
    id: 'transform',
    icon: '📝',
    name: 'Data Transform',
    context: 'data-transform.md',
    description: 'Process and transform data',
    example: '"convert CSV to JSON", "process user data"'
  },
  {
    id: 'chat',
    icon: '💬',
    name: 'Conversation',
    context: 'conversation.md',
    description: 'General questions and conversation',
    example: '"hi", "what can you do", "thanks"'
  }
];

interface TopicSelectorProps {
  onSelectTopic: (topic: Topic) => void;
  onCancel: () => void;
  selectedTopicId?: string;
}

export default function TopicSelector({ onSelectTopic, onCancel, selectedTopicId }: TopicSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {TOPICS.map((topic) => {
        const isSelected = selectedTopicId === topic.id;
        return (
        <Item
          key={topic.id}
          variant="outline"
          className={`cursor-pointer hover:border-primary hover:bg-primary/5 transition-all ${
            isSelected ? 'border-primary bg-primary/10 ring-2 ring-primary/20' : ''
          }`}
          onClick={() => onSelectTopic(topic)}
        >
          <ItemMedia className="group-hover:scale-110 transition-transform">
            <span className="text-3xl">{topic.icon}</span>
          </ItemMedia>
          <ItemContent>
            <ItemTitle className="group-hover:text-primary transition-colors">
              {topic.name}
            </ItemTitle>
            <ItemDescription className="mb-1.5">
              {topic.description}
            </ItemDescription>
            <ItemDescription className="italic opacity-70">
              e.g., {topic.example}
            </ItemDescription>
          </ItemContent>
          <ItemActions>
            {isSelected ? (
              <span className="text-primary font-bold">✓</span>
            ) : (
              <ChevronRightIcon className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
            )}
          </ItemActions>
        </Item>
        );
      })}
    </div>
  );
}

// Export the topics list for use in other components
export { TOPICS };
export type { Topic };
