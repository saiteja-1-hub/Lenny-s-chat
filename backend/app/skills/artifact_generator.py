import re
from dataclasses import dataclass

_ARTIFACT_RE = re.compile(
    r'<artifact\s+type="(?P<type>markdown|html)"\s+title="(?P<title>[^"]*)"\s*>'
    r"(?P<content>.*?)"
    r"</artifact>",
    re.DOTALL | re.IGNORECASE,
)


@dataclass
class ParsedArtifact:
    artifact_type: str
    title: str
    content: str


def extract_artifacts(raw_text: str) -> tuple[str, list[ParsedArtifact]]:
    """
    Split the model's raw output into (visible_chat_text, artifacts).
    The <artifact> block is stripped out of the chat text and returned separately
    so the frontend can render it in the side-panel viewer instead of inline.
    """
    artifacts: list[ParsedArtifact] = []

    def _capture(match: re.Match) -> str:
        artifacts.append(
            ParsedArtifact(
                artifact_type=match.group("type"),
                title=match.group("title") or "Artifact",
                content=match.group("content").strip(),
            )
        )
        return ""  # remove the artifact block from the visible reply

    visible_text = _ARTIFACT_RE.sub(_capture, raw_text).strip()
    return visible_text, artifacts


GROUNDED_SYSTEM_PROMPT = """You are the Lenny Growth Assistant, an expert on product management and growth \
sourced exclusively from Lenny's Podcast transcripts.

Rules:
1. Answer ONLY using the transcript context provided below. Do not use outside knowledge.
2. Every claim must cite its source inline using the format [Episode: Guest Name, Timestamp/Topic].
3. If the provided context does not contain enough information to answer, reply exactly:
   "I do not have sufficient information in Lenny's podcast archive to answer this."
4. Keep answers concise and directly actionable for a product/growth leader.

Transcript Context:
{context_data}
"""


def build_grounded_system_prompt(retrieved_chunks: list[dict]) -> str:
    if not retrieved_chunks:
        context_data = "(No relevant transcript chunks were found for this query.)"
    else:
        context_data = "\n\n".join(
            f"[Episode: {c['guest']}, {c.get('timestamp') or c['episode']}]\n{c['text']}"
            for c in retrieved_chunks
        )
    return GROUNDED_SYSTEM_PROMPT.format(context_data=context_data)
