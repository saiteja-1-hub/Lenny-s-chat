"""
Ingests transcript files from ./data/transcripts into the transcript_chunks table.

Usage:
    python scripts/ingest.py
"""
import asyncio
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))  # allow `import app.*`

from app.database import AsyncSessionLocal, init_db  # noqa: E402
from app.models.db_models import TranscriptChunk  # noqa: E402
from app.rag.embeddings import get_embedding  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "transcripts"

# Target ~500-800 tokens/chunk. Approximating 4 chars/token.
CHUNK_SIZE_CHARS = 2800
CHUNK_OVERLAP_CHARS = 400
SEPARATORS = ["\n\n", "\n", ". ", " "]


def recursive_split(text: str, chunk_size: int, overlap: int, separators: list[str]) -> list[str]:
    """Simple recursive character splitter (mirrors LangChain's approach without the dependency)."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    sep = separators[0] if separators else ""
    remaining_seps = separators[1:]

    parts = text.split(sep) if sep else list(text)
    chunks: list[str] = []
    current = ""

    for part in parts:
        candidate = current + (sep if current else "") + part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(part) > chunk_size and remaining_seps:
                chunks.extend(recursive_split(part, chunk_size, overlap, remaining_seps))
                current = ""
            else:
                current = part

    if current.strip():
        chunks.append(current)

    # apply overlap by prepending the tail of the previous chunk
    overlapped = []
    for i, c in enumerate(chunks):
        if i == 0:
            overlapped.append(c)
        else:
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append(prev_tail + c)
    return overlapped


def parse_metadata(raw_text: str, filename: str) -> dict:
    episode_title = filename
    guest_name = "Unknown"
    publication_date = None

    title_match = re.search(r"^#?\s*Episode:\s*(.+)$", raw_text, re.MULTILINE | re.IGNORECASE)
    guest_match = re.search(r"^Guest:\s*(.+)$", raw_text, re.MULTILINE | re.IGNORECASE)
    date_match = re.search(r"^Date:\s*(.+)$", raw_text, re.MULTILINE | re.IGNORECASE)

    if title_match:
        episode_title = title_match.group(1).strip()
    if guest_match:
        guest_name = guest_match.group(1).strip()
    if date_match:
        publication_date = date_match.group(1).strip()

    return {
        "episode_title": episode_title,
        "guest_name": guest_name,
        "publication_date": publication_date,
    }


async def ingest_file(path: Path) -> int:
    raw_text = path.read_text(encoding="utf-8", errors="ignore")
    meta = parse_metadata(raw_text, path.stem)
    body = re.sub(r"^(#?\s*Episode:.*|Guest:.*|Date:.*)$", "", raw_text, flags=re.MULTILINE | re.IGNORECASE)

    chunks = recursive_split(body, CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS, SEPARATORS)

    inserted = 0
    async with AsyncSessionLocal() as session:
        for i, chunk_text in enumerate(chunks):
            embedding = await get_embedding(chunk_text)
            row = TranscriptChunk(
                episode_title=meta["episode_title"],
                guest_name=meta["guest_name"],
                publication_date=meta["publication_date"],
                timestamp_ref=f"chunk {i + 1}/{len(chunks)}",
                chunk_text=chunk_text.strip(),
                embedding=embedding,
            )
            session.add(row)
            inserted += 1
        await session.commit()
    return inserted


async def main() -> None:
    await init_db()

    if not DATA_DIR.exists():
        print(f"No transcripts found at {DATA_DIR}. Run download_transcripts.py first, "
              f"or place .md/.txt files there manually.")
        return

    files = [p for p in DATA_DIR.iterdir() if p.suffix.lower() in (".md", ".txt")]
    if not files:
        print(f"No .md/.txt files in {DATA_DIR}.")
        return

    total = 0
    for path in files:
        n = await ingest_file(path)
        print(f"Ingested {n} chunks from {path.name}")
        total += n

    print(f"Done. Total chunks indexed: {total}")


if __name__ == "__main__":
    asyncio.run(main())
