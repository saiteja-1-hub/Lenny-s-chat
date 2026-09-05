const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SessionSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ArtifactData {
  id?: string;
  artifact_type: "markdown" | "html";
  title: string;
  content: string;
}

export interface SourceRef {
  episode: string;
  guest: string;
  timestamp: string | null;
  score: number;
  text?: string;
}

export interface MessageData {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceRef[] | null;
  artifacts?: ArtifactData[];
  created_at: string;
}

export interface SessionDetail extends SessionSummary {
  messages: MessageData[];
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

export async function createSession(title = "New Chat"): Promise<SessionSummary> {
  const res = await fetch(`${API_URL}/api/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  return handle<SessionSummary>(res);
}

export async function listSessions(): Promise<SessionSummary[]> {
  const res = await fetch(`${API_URL}/api/sessions`);
  return handle<SessionSummary[]>(res);
}

export async function getSession(sessionId: string): Promise<SessionDetail> {
  const res = await fetch(`${API_URL}/api/sessions/${sessionId}`);
  return handle<SessionDetail>(res);
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/sessions/${sessionId}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204) {
    throw new Error(`Failed to delete session: ${res.status}`);
  }
}

export function chatStreamUrl(): string {
  return `${API_URL}/api/chat`;
}

export { API_URL };