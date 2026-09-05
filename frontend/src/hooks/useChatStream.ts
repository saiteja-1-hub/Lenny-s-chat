import { useCallback, useRef, useState } from "react";
import { chatStreamUrl, ArtifactData, SourceRef } from "@/lib/api";

export interface StreamMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceRef[];
  artifacts?: ArtifactData[];
  isStreaming?: boolean;
}

interface UseChatStreamOptions {
  sessionId: string | null;
  mode?: "default" | "ship30";
  provider?: "ollama" | "claude";
}

export function useChatStream({ sessionId, mode = "default", provider = "ollama" }: UseChatStreamOptions) {
  const [messages, setMessages] = useState<StreamMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!sessionId || !text.trim()) return;
      setError(null);

      const userMsg: StreamMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: text,
      };
      const assistantId = `assistant-${Date.now()}`;
      const assistantMsg: StreamMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        sources: [],
        artifacts: [],
        isStreaming: true,
      };
      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setIsStreaming(true);

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const res = await fetch(chatStreamUrl(), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId, message: text, mode, provider }),
          signal: controller.signal,
        });

        if (!res.ok || !res.body) {
          throw new Error(`Chat request failed: ${res.status}`);
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          const events = buffer.split("\n\n");
          buffer = events.pop() || ""; // keep incomplete trailing chunk

          for (const rawEvent of events) {
            const line = rawEvent.trim();
            if (!line.startsWith("data:")) continue;
            const payload = line.slice(5).trim();
            if (payload === "[DONE]") continue;

            let parsed: { type: string; content: unknown };
            try {
              parsed = JSON.parse(payload);
            } catch {
              continue;
            }

            setMessages((prev) =>
              prev.map((m) => {
                if (m.id !== assistantId) return m;
                if (parsed.type === "token") {
                  return { ...m, content: m.content + (parsed.content as string) };
                }
                if (parsed.type === "sources") {
                  return { ...m, sources: parsed.content as SourceRef[] };
                }
                if (parsed.type === "artifacts") {
                  return { ...m, artifacts: parsed.content as ArtifactData[] };
                }
                return m;
              })
            );
          }
        }
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          setError((err as Error).message || "Something went wrong while streaming the response.");
        }
      } finally {
        setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, isStreaming: false } : m)));
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [sessionId, mode, provider]
  );

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const loadMessages = useCallback((initial: StreamMessage[]) => {
    setMessages(initial);
  }, []);

  return { messages, sendMessage, isStreaming, error, stopStreaming, loadMessages };
}
