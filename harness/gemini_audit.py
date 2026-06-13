#!/usr/bin/env python3
"""External completeness audit of the corpus by Gemini (the most decorrelated
model from the Claude planter), per pre-registration limitation #2 / amendment 2.

BLIND: Gemini sees only the snippet code, never the ground truth. It is asked to
find ALL defects (planted and unintended), judge realism, and flag any textbook/
obvious bug. We then reconcile its findings against corpus/truth:
  - did it find each planted defect?        (findability)
  - did it find a defect NOT in ground truth? (candidate for human adjudication)
  - did it call a 'subtle' defect obvious / the code contrived? (fairness)

Stateless CLI calls: this audit invocation shares no memory with the later
clean-room Gemini *rater* invocations, so it does not contaminate the study.

Usage: python3 harness/gemini_audit.py [snippet_id ...]   (default: 01..20)
Writes runs/gemini_audit/NN.json (+ NN.raw on parse failure).
"""
from __future__ import annotations
import json, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNIP = ROOT / "corpus" / "snippets"
OUT = ROOT / "runs" / "gemini_audit"
GEMINI = "/opt/homebrew/bin/gemini"

PROMPT_HEAD = (
    "You are a meticulous senior code reviewer. Review this Python for ALL "
    "defects: correctness, security, concurrency, boundary/off-by-one, API "
    "misuse, performance, and any violation of the documented contract "
    "(docstring). Find every defect, obvious or subtle. Then judge if it reads "
    "like realistic production code, and flag any textbook/obvious bug.\n\n"
    "Output ONLY a JSON object (no markdown fences):\n"
    '{"defects":[{"lines":[1],"type":"category","severity":"low|medium|high",'
    '"description":"what is wrong"}],"realism":"realistic|contrived",'
    '"obvious_bugs":["desc"],"notes":"..."}\n\nCODE:\n'
)


def extract_json(text: str):
    i = text.find("{")
    if i < 0:
        return None
    # try progressively shorter tails ending at each '}' from the last
    for j in range(len(text), i, -1):
        if text[j - 1] != "}":
            continue
        try:
            return json.loads(text[i:j])
        except json.JSONDecodeError:
            continue
    return None


def audit(sid: str) -> str:
    code = (SNIP / f"{sid}.py").read_text()
    prompt = PROMPT_HEAD + code
    try:
        r = subprocess.run([GEMINI, "-p", prompt], capture_output=True,
                           text=True, timeout=180)
    except subprocess.TimeoutExpired:
        (OUT / f"{sid}.raw").write_text("TIMEOUT")
        return f"{sid}: TIMEOUT"
    obj = extract_json(r.stdout)
    if obj is None:
        (OUT / f"{sid}.raw").write_text(r.stdout + "\n--- STDERR ---\n" + r.stderr)
        return f"{sid}: NO JSON (raw saved)"
    obj["_snippet"] = sid
    (OUT / f"{sid}.json").write_text(json.dumps(obj, indent=2) + "\n")
    nd = len(obj.get("defects", []))
    return f"{sid}: ok ({nd} defects found, realism={obj.get('realism','?')})"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ids = sys.argv[1:] or [f"{i:02d}" for i in range(1, 21)]
    for sid in ids:
        print(audit(sid), flush=True)
    print("AUDIT COMPLETE")
