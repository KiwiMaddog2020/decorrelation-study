#!/usr/bin/env python3
"""Codex (OpenAI) clean-room REVIEW pass (a rater).

Each call is a fresh `codex exec` given only the snippet and the identical blind
review prompt, piped on STDIN. Codex runs at high reasoning and is slow, so the
timeout is generous and the transcript is filtered down to the defect lines.
Writes runs/full/NN.codex.txt (+ NN.codex.raw for the full transcript).

Usage: python3 harness/run_codex_reviews.py [snippet_id ...]   (default 01..20)
"""
from __future__ import annotations
import os, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNIP = ROOT / os.environ.get("CORPUS_DIR", "corpus/snippets")
OUT = ROOT / os.environ.get("OUT_DIR", "runs/full")
PROMPT = (ROOT / "protocol" / "review_prompt.txt").read_text()
CODEX = "/Applications/Codex.app/Contents/Resources/codex"
ARGS = [CODEX, "exec", "--skip-git-repo-check", "--enable", "fast_mode",
        "-c", "service_tier=priority"]


def keep(text: str) -> str:
    lines = [l for l in text.splitlines()
             if " | " in l or l.strip() == "NO DEFECTS FOUND"]
    return "\n".join(lines).strip() or "NO DEFECTS FOUND"


def review(sid: str) -> str:
    code = (SNIP / f"{sid}.py").read_text()
    prompt = PROMPT.replace("{{SNIPPET}}", code)
    try:
        r = subprocess.run(ARGS, input=prompt, capture_output=True,
                           text=True, timeout=600)
    except subprocess.TimeoutExpired:
        (OUT / f"{sid}.codex.txt").write_text("TIMEOUT")
        return f"{sid}: TIMEOUT"
    (OUT / f"{sid}.codex.raw").write_text(r.stdout + "\n--- STDERR ---\n" + r.stderr)
    out = keep(r.stdout)
    (OUT / f"{sid}.codex.txt").write_text(out + "\n")
    n = sum(1 for l in out.splitlines() if " | " in l)
    return f"{sid}: {n} defect line(s)"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ids = sys.argv[1:] or [f"{i:02d}" for i in range(1, 21)]
    for sid in ids:
        print(review(sid), flush=True)
    print("CODEX REVIEWS COMPLETE")
