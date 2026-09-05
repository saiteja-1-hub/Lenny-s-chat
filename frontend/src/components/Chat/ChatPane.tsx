"use client";

import { useEffect, useRef, useState } from "react";
import { Plus, Send, Square } from "lucide-react";
import { MessageItem } from "./MessageItem";
import { ModelSelector } from "./ModelSelector";
import { useChatStream } from "@/hooks/useChatStream";
import { createSession, listSessions, getSession, SessionSummary, ArtifactData } from "@/lib/api";

interface ChatPaneProps {
  onOpenArtifact: (artifact: ArtifactData) => void;
}

export function ChatPane({ onOpenArtifact }: ChatPaneProps) {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState<"ollama" | "claude">("ollama");
  const [mode, setMode] = useState<"default" | "ship30">("default");
  const scrollRef = useRef<HTMLDivElement>(null);

  const { messages, sendMessage, isStreaming, error, stopStreaming, loadMessages } = useChatStream({
    sessionId,
    mode,
    provider,
  });

  useEffect(() => {
    refreshSessions();
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function refreshSessions() {
    try {
      const list = await listSessions();
      setSessions(list);
      if (!sessionId && list.length > 0) {
        selectSession(list[0].id);
      } else if (list.length === 0) {
        handleNewSession();
      }
    } catch {
      // Backend not reachable yet — leave the empty state showing.
    }
  }

  async function handleNewSession() {
    const session = await createSession("New Chat");
    setSessions((prev) => [session, ...prev]);
    setSessionId(session.id);
    loadMessages([]);
  }

  async function selectSession(id: string) {
    setSessionId(id);
    try {
      const detail = await getSession(id);
      loadMessages(
        detail.messages.map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          sources: m.sources || [],
          artifacts: m.artifacts || [],
        }))
      );
    } catch {
      loadMessages([]);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    sendMessage(input);
    setInput("");
  }

  return (
    <div className="flex h-full flex-col bg-paper-50">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-ink-700/10 px-5 py-3">
        <div className="flex items-center gap-2">
          <h1 className="font-serif text-lg text-ink-950">Lenny Growth Assistant</h1>
        </div>
        <ModelSelector
          provider={provider}
          mode={mode}
          onProviderChange={setProvider}
          onModeChange={setMode}
        />
      </div>

      {/* Session tabs */}
      <div className="flex items-center gap-2 overflow-x-auto border-b border-ink-700/10 px-5 py-2">
        <button
          onClick={handleNewSession}
          className="flex flex-shrink-0 items-center gap-1 rounded-full border border-dashed border-ink-700/25 px-3 py-1 text-xs text-ink-700 hover:border-growth-600 hover:text-growth-700"
        >
          <Plus size={12} /> New
        </button>
        {sessions.map((s) => (
          <button
            key={s.id}
            onClick={() => selectSession(s.id)}
            className={`flex-shrink-0 truncate rounded-full px-3 py-1 text-xs ${
              s.id === sessionId
                ? "bg-ink-900 text-paper-50"
                : "bg-paper-100 text-ink-700 hover:bg-ink-700/10"
            }`}
            style={{ maxWidth: 160 }}
          >
            {s.title}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 space-y-5 overflow-y-auto px-5 py-6">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center text-ink-700/50">
            <p className="font-serif text-xl text-ink-800">Ask something grounded in the archive.</p>
            <p className="mt-1 text-sm">e.g. &ldquo;How do I improve activation?&rdquo;</p>
          </div>
        )}
        {messages.map((m) => (
          <MessageItem key={m.id} message={m} onOpenArtifact={onOpenArtifact} />
        ))}
        {error && (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">{error}</p>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t border-ink-700/10 p-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={mode === "ship30" ? "Give me a topic to turn into an essay..." : "Ask a question..."}
          className="flex-1 rounded-full border border-ink-700/15 bg-white px-4 py-2.5 text-sm text-ink-900 outline-none focus:border-growth-600"
          disabled={!sessionId}
        />
        {isStreaming ? (
          <button
            type="button"
            onClick={stopStreaming}
            className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-red-500 text-white"
          >
            <Square size={14} />
          </button>
        ) : (
          <button
            type="submit"
            disabled={!input.trim() || !sessionId}
            className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-growth-600 text-white disabled:opacity-30"
          >
            <Send size={14} />
          </button>
        )}
      </form>
    </div>
  );
}
