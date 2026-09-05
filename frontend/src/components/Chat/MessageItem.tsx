"use client";

import { FileCode, Sparkles, User } from "lucide-react";
import type { StreamMessage } from "@/hooks/useChatStream";
import type { ArtifactData } from "@/lib/api";

interface MessageItemProps {
  message: StreamMessage;
  onOpenArtifact: (artifact: ArtifactData) => void;
}

export function MessageItem({ message, onOpenArtifact }: MessageItemProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full ${
          isUser ? "bg-ink-900 text-paper-50" : "bg-growth-600 text-paper-50"
        }`}
      >
        {isUser ? <User size={14} /> : <Sparkles size={14} />}
      </div>

      <div className={`max-w-[75%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-2`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? "rounded-tr-sm bg-ink-900 text-paper-50"
              : "rounded-tl-sm border border-ink-700/10 bg-white text-ink-900"
          }`}
        >
          {message.content || (message.isStreaming ? <TypingDots /> : "")}
          {message.isStreaming && message.content && <span className="animate-pulse">▍</span>}
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {message.sources.map((s, i) => (
              <span
                key={i}
                title={s.text as unknown as string}
                className="rounded-full border border-growth-600/30 bg-growth-600/5 px-2 py-0.5 text-[11px] text-growth-700"
              >
                {s.guest} · {s.timestamp || s.episode}
              </span>
            ))}
          </div>
        )}

        {!isUser && message.artifacts && message.artifacts.length > 0 && (
          <div className="flex flex-col gap-1.5">
            {message.artifacts.map((a, i) => (
              <button
                key={i}
                onClick={() => onOpenArtifact(a)}
                className="flex items-center gap-2 rounded-lg border border-ink-700/15 bg-paper-100 px-3 py-2 text-left text-xs text-ink-800 transition-colors hover:border-growth-600/40 hover:bg-growth-600/5"
              >
                <FileCode size={14} className="text-growth-600" />
                <span className="truncate">{a.title}</span>
                <span className="ml-auto text-[10px] uppercase text-ink-700/50">{a.artifact_type}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TypingDots() {
  return (
    <span className="flex gap-1 py-1">
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-700/40 [animation-delay:-0.3s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-700/40 [animation-delay:-0.15s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-700/40" />
    </span>
  );
}
