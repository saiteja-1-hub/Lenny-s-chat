"use client";

import { useMemo } from "react";
import DOMPurify from "dompurify";

interface SandboxedIframeProps {
  content: string;
  title: string;
}

export function SandboxedIframe({ content, title }: SandboxedIframeProps) {
  const cleanHtml = useMemo(() => {
    return DOMPurify.sanitize(content, {
      WHOLE_DOCUMENT: true,
      ADD_TAGS: ["style", "link"],
      ADD_ATTR: ["target"],
    });
  }, [content]);

  return (
    <iframe
      title={title}
      srcDoc={cleanHtml}
      // Deliberately omit allow-same-origin: this blocks the iframe's script from
      // reading the parent page's cookies, localStorage, or DOM — only allow-scripts
      // is granted, so content can still be interactive without being able to escape
      // its sandbox.
      sandbox="allow-scripts"
      className="h-full w-full border-none bg-white"
    />
  );
}
