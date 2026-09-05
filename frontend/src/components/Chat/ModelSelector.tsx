"use client";

import { Cpu, Cloud, FileText, MessageSquare } from "lucide-react";

interface ModelSelectorProps {
  provider: "ollama" | "claude";
  mode: "default" | "ship30";
  onProviderChange: (p: "ollama" | "claude") => void;
  onModeChange: (m: "default" | "ship30") => void;
}

export function ModelSelector({ provider, mode, onProviderChange, onModeChange }: ModelSelectorProps) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <div className="flex items-center rounded-full border border-ink-700/20 bg-paper-100 p-0.5">
        <button
          onClick={() => onProviderChange("ollama")}
          className={`flex items-center gap-1 rounded-full px-2.5 py-1 transition-colors ${
            provider === "ollama" ? "bg-ink-900 text-paper-50" : "text-ink-700 hover:text-ink-900"
          }`}
        >
          <Cpu size={12} /> Local
        </button>
        <button
          onClick={() => onProviderChange("claude")}
          className={`flex items-center gap-1 rounded-full px-2.5 py-1 transition-colors ${
            provider === "claude" ? "bg-ink-900 text-paper-50" : "text-ink-700 hover:text-ink-900"
          }`}
        >
          <Cloud size={12} /> Cloud
        </button>
      </div>

      <div className="flex items-center rounded-full border border-ink-700/20 bg-paper-100 p-0.5">
        <button
          onClick={() => onModeChange("default")}
          className={`flex items-center gap-1 rounded-full px-2.5 py-1 transition-colors ${
            mode === "default" ? "bg-growth-600 text-paper-50" : "text-ink-700 hover:text-ink-900"
          }`}
        >
          <MessageSquare size={12} /> Answer
        </button>
        <button
          onClick={() => onModeChange("ship30")}
          className={`flex items-center gap-1 rounded-full px-2.5 py-1 transition-colors ${
            mode === "ship30" ? "bg-growth-600 text-paper-50" : "text-ink-700 hover:text-ink-900"
          }`}
        >
          <FileText size={12} /> Ship 30 Essay
        </button>
      </div>
    </div>
  );
}
