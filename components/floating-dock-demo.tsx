import React from "react";
import { FloatingDock } from "@/components/ui/floating-dock";
import {
  Store,
  Folder,
  Workflow,
  TerminalIcon,
  Activity,
} from "lucide-react";

import { Github, Brain, Slack } from "lucide-react";

interface FloatingDockDemoProps {
  openWindow: (id: string, title: string, component: React.ReactNode) => void;
  openWindows: string[];
  dockApps: { id: string; name: string; icon: string }[];
  onDrop: (app: { id: string; name: string; icon: string }) => void;
}

export function FloatingDockDemo({ openWindow, openWindows, dockApps, onDrop }: FloatingDockDemoProps) {
  const getIconComponent = (iconName: string) => {
    switch (iconName) {
      case "Store": return Store;
      case "Folder": return Folder;
      case "Workflow": return Workflow;
      case "TerminalIcon": return TerminalIcon;
      case "Activity": return Activity;
      case "Github": return Github;
      case "Brain": return Brain;
      case "Slack": return Slack;
      default: return Store;
    }
  };

  const links = (dockApps || []).map((app) => {
    const IconComponent = getIconComponent(app.icon);
    return {
      title: app.name,
      icon: (
        <IconComponent className={`h-full w-full ${openWindows.includes(app.id) ? "text-blue-500" : "text-neutral-500 dark:text-neutral-300"}`} />
      ),
      href: "#",
      onClick: () => openWindow(app.id, app.name, null),
    };
  });
  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "copy";
      }}
      onDrop={(e) => {
        e.preventDefault();
        const appData = e.dataTransfer.getData("application/json");
        if (appData) {
          const app = JSON.parse(appData);
          onDrop(app);
        }
      }}
    >
      <FloatingDock
        mobileClassName="translate-y-0"
        items={links} 
      />
    </div>
  );
}