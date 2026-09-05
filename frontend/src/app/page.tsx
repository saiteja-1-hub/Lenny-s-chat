"use client";

import { useState } from "react";
import { PanelRightClose, PanelRightOpen } from "lucide-react";
import { ChatPane } from "@/components/Chat/ChatPane";
import { ArtifactViewer } from "@/components/Artifact/ArtifactViewer";
import type { ArtifactData } from "@/lib/api";

export default function Home() {
  const [activeArtifact, setActiveArtifact] = useState<ArtifactData | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(true);

  function openArtifact(a: ArtifactData) {
    setActiveArtifact(a);
    setDrawerOpen(true);
  }

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-paper-50">
      <div className={`flex-1 min-w-0 ${drawerOpen ? "" : "mx-auto max-w-3xl"}`}>
        <ChatPane onOpenArtifact={openArtifact} />
      </div>

      <button
        onClick={() => setDrawerOpen((v) => !v)}
        className="flex w-8 flex-shrink-0 items-center justify-center border-l border-ink-700/10 bg-paper-100 text-ink-700/50 hover:text-ink-900"
        title={drawerOpen ? "Collapse panel" : "Expand panel"}
      >
        {drawerOpen ? <PanelRightClose size={14} /> : <PanelRightOpen size={14} />}
      </button>

      {drawerOpen && (
        <div className="w-[42%] min-w-[380px] max-w-[640px] flex-shrink-0">
          <ArtifactViewer artifact={activeArtifact} onClose={() => setActiveArtifact(null)} />
        </div>
      )}
    </main>
  );
}
