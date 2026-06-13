#!/usr/bin/env python3
"""Gemini clean-room REVIEW pass (a rater, not the auditor).

Each call is a fresh, stateless Gemini invocation given only the snippet and the
identical blind review prompt (protocol/review_prompt.txt). No ground truth, no
audit memory. Writes runs/full/NN.gemini.txt in LOCATION | TYPE | DESCRIPTION form.

Usage: python3 harness/run_gemini_reviews.py [snippet_id ...]   (default 01..20)
"""
from __future__ import annotations
import subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNIP = ROOT / "corpus" / "snippets"
OUT = ROOT / "runs" / "full"
PROMPT = (ROOT / "protocol" / "review_prompt.txt").read_text()
GEMINI = "/opt/homebrew/bin/gemini"


def keep(text: str) -> str:
    lines = [l for l in text.splitlines()
             if " | " in l or l.strip() == "NO DEFECTS FOUND"]
    return "\n".join(lines).strip() or "NO DEFECTS FOUND"


def review(sid: str) -> str:
    code = (SNIP / f"{sid}.py").read_text()
    prompt = PROMPT.replace("{{SNIPPET}}", code)
    try:
        r = subprocess.run([GEMINI, "-p", prompt], capture_output=True,
                           text=True, timeout=180)
    except subprocess.TimeoutExpired:
        (OUT / f"{sid}.gemini.txt").write_text("TIMEOUT")
        return f"{sid}: TIMEOUT"
    out = keep(r.stdout)
    (OUT / f"{sid}.gemini.txt").write_text(out + "\n")
    n = sum(1 for l in out.splitlines() if " | " in l)
    return f"{sid}: {n} defect line(s)"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ids = sys.argv[1:] or [f"{i:02d}" for i in range(1, 21)]
    for sid in ids:
        print(review(sid), flush=True)
    print("GEMINI REVIEWS COMPLETE")
