'use client';

import React, { useState, useRef, useEffect, useCallback } from "react";
import { FloatingDock } from "@/components/ui/floating-dock";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import {
  Store,
  Folder,
  Workflow,
  TerminalIcon,
  Activity,
  PaperclipIcon,
  ArrowUpIcon,
  X,
} from "lucide-react";
import { Github, Brain, Slack } from "lucide-react";

interface FloatingDockDemoProps {
  openWindow: (id: string, title: string, component: React.ReactNode) => void;
  openWindows: string[];
  dockApps: { id: string; name: string; icon: string }[];
  onDrop: (app: { id: string; name: string; icon: string }) => void;
  onChatActivate?: () => void;
}

export function FloatingDockDemo({ openWindow, openWindows, dockApps, onDrop, onChatActivate }: FloatingDockDemoProps) {
  const [chatMessage, setChatMessage] = useState("");
  const [isChatMode, setIsChatMode] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight + 2}px`;
    }
  }, []);

  const resetHeight = useCallback(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = '98px';
    }
  }, []);

  useEffect(() => {
    if (textareaRef.current && isChatMode) {
      adjustHeight();
      textareaRef.current.focus();
    }
  }, [isChatMode, adjustHeight]);

  const handleInput = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setChatMessage(event.target.value);
    adjustHeight();
  }, [adjustHeight]);

  const submitForm = useCallback(() => {
    if (chatMessage.trim()) {
      console.log("Sending message:", chatMessage);
      setChatMessage("");
      resetHeight();
      setIsChatMode(false);
    }
  }, [chatMessage, resetHeight]);

  const handleChatClick = useCallback(() => {
    setIsChatMode(true);
    if (onChatActivate) {
      onChatActivate();
    }
  }, [onChatActivate]);

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
      onClick: () => {
        if (app.name === "ChatGPT" || app.id === "chatgpt") {
          handleChatClick();
        } else {
          openWindow(app.id, app.name, null);
        }
      },
    };
  });

  if (isChatMode) {
    return (
      <motion.div
        initial={{ scale: 1, opacity: 0.8 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 1, opacity: 0.8 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
        className="flex flex-col items-center justify-center space-y-2"
      >
        <div className="relative w-full max-w-6xl">
          <Textarea
            ref={textareaRef}
            placeholder="Ask a follow-up..."
            value={chatMessage}
            onChange={handleInput}
            className="min-h-[160px] max-h-[calc(75dvh)] overflow-hidden resize-none rounded-2xl text-sm bg-[#f4f4f5] dark:bg-[#161616] pb-8 border-[0.5px] border-zinc-200 dark:border-[#27282d] text-neutral-700 dark:text-neutral-300 placeholder:text-neutral-500 py-8 px-6"
            rows={8}
            autoFocus
            onKeyDown={(event) => {
              if (
                event.key === 'Enter' &&
                !event.shiftKey &&
                !event.nativeEvent.isComposing
              ) {
                event.preventDefault();
                submitForm();
              } else if (event.key === 'Escape') {
                setChatMessage("");
                resetHeight();
                setIsChatMode(false);
              }
            }}
          />

          <div className="absolute bottom-0 p-1 w-fit flex flex-row justify-start">
            <Button
              className="rounded-md rounded-bl-lg p-1 h-fit dark:border-zinc-700 hover:dark:bg-zinc-900 hover:bg-zinc-200 text-neutral-500 dark:text-neutral-400"
              variant="ghost"
            >
              <PaperclipIcon size={12} />
            </Button>
          </div>

          <div className="absolute bottom-0 right-0 p-1 w-fit flex flex-row items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800 h-5 w-5 p-0 rounded-lg"
            >
              <svg className="h-2.5 w-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              className="text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800 h-5 w-5 p-0 rounded-lg"
            >
              <svg className="h-2.5 w-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </Button>
            
            <Button
              variant="ghost"
              size="sm" 
              className="text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800 h-5 w-5 p-0 rounded-lg"
            >
              <svg className="h-2.5 w-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3l14 9-14 9V3z" />
              </svg>
            </Button>
            
            <span className="text-neutral-400 text-xs font-medium">Design</span>
            
            <Button
              className="rounded-full p-1 h-fit border dark:border-zinc-600"
              onClick={submitForm}
              disabled={chatMessage.length === 0}
            >
              <ArrowUpIcon size={12} />
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setChatMessage("");
                resetHeight();
                setIsChatMode(false);
              }}
              className="text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800 h-5 w-5 p-0 rounded-lg ml-1"
            >
              <svg className="h-2.5 w-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
            </Button>
          </div>
        </div>
        
        <div className="bg-neutral-900 rounded-xl border border-neutral-700 px-2 py-1 flex items-center justify-between w-full max-w-6xl">
          <span className="text-neutral-400" style={{ fontSize: '10px' }}>
            Upgrade to Team to unlock all of v0's features and more credits
          </span>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="text-teal-400 hover:text-teal-300 hover:bg-neutral-800 font-medium h-5 px-1"
              style={{ fontSize: '10px' }}
            >
              Upgrade Plan
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800 h-4 w-4 p-0"
            >
              <X className="h-2.5 w-2.5" />
            </Button>
          </div>
        </div>
      </motion.div>
    );
  }

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