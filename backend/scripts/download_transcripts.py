"""
Downloads Lenny's Podcast transcripts into ./data/transcripts.

By default this clones a git repo of transcripts (configure TRANSCRIPT_REPO_URL
below or via env var). If you don't have a transcript source yet, point this
at your own repo/export, or drop .md/.txt files directly into ./data/transcripts
and skip this script entirely.

Usage:
    python scripts/download_transcripts.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "transcripts"
TRANSCRIPT_REPO_URL = os.getenv(
    "TRANSCRIPT_REPO_URL",
    "",  # <-- set this to your transcript source repo, e.g. a git URL
)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not TRANSCRIPT_REPO_URL:
        print(
            "TRANSCRIPT_REPO_URL is not set.\n"
            f"Either export it before running this script, or manually place "
            f".md/.txt transcript files into: {DATA_DIR}\n"
            "Each file should ideally start with a short header like:\n"
            "  # Episode: <title>\n"
            "  Guest: <name>\n"
            "  Date: <YYYY-MM-DD>\n"
        )
        sys.exit(0)

    tmp_clone = DATA_DIR.parent / "_transcript_clone_tmp"
    if tmp_clone.exists():
        shutil.rmtree(tmp_clone)

    print(f"Cloning {TRANSCRIPT_REPO_URL} ...")
    subprocess.run(["git", "clone", "--depth", "1", TRANSCRIPT_REPO_URL, str(tmp_clone)], check=True)

    count = 0
    for path in tmp_clone.rglob("*"):
        if path.suffix.lower() in (".md", ".txt"):
            dest = DATA_DIR / path.name
            shutil.copy(path, dest)
            count += 1

    shutil.rmtree(tmp_clone)
    print(f"Copied {count} transcript files into {DATA_DIR}")


if __name__ == "__main__":
    main()
