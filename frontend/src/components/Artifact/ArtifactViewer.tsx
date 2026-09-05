"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { X, Download, FileText, Code2 } from "lucide-react";
import { SandboxedIframe } from "./SandboxedIframe";
import type { ArtifactData } from "@/lib/api";

interface ArtifactViewerProps {
  artifact: ArtifactData | null;
  onClose: () => void;
}

export function ArtifactViewer({ artifact, onClose }: ArtifactViewerProps) {
  if (!artifact) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 border-l border-ink-700/10 bg-paper-100 text-center text-ink-700/40">
        <Code2 size={28} strokeWidth={1.5} />
        <p className="max-w-[200px] text-sm">Generated essays and pages will open here.</p>
      </div>
    );
  }

  function handleDownload() {
    if (!artifact) return;
    const ext = artifact.artifact_type === "html" ? "html" : "md";
    const blob = new Blob([artifact.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${artifact.title.replace(/\s+/g, "_")}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex h-full flex-col border-l border-ink-700/10 bg-white">
      <div className="flex items-center justify-between border-b border-ink-700/10 px-4 py-3">
        <div className="flex min-w-0 items-center gap-2">
          <FileText size={14} className="flex-shrink-0 text-growth-600" />
          <span className="truncate text-sm font-medium text-ink-900">{artifact.title}</span>
          <span className="flex-shrink-0 rounded-full bg-growth-600/10 px-2 py-0.5 text-[10px] uppercase text-growth-700">
            {artifact.artifact_type}
          </span>
        </div>
        <div className="flex flex-shrink-0 items-center gap-1">
          <button
            onClick={handleDownload}
            className="rounded-md p-1.5 text-ink-700 hover:bg-paper-100"
            title="Download"
          >
            <Download size={14} />
          </button>
          <button onClick={onClose} className="rounded-md p-1.5 text-ink-700 hover:bg-paper-100" title="Close">
            <X size={14} />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {artifact.artifact_type === "html" ? (
          <SandboxedIframe content={artifact.content} title={artifact.title} />
        ) : (
          <div className="prose prose-sm max-w-none px-6 py-5 prose-headings:font-serif prose-headings:text-ink-950">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
