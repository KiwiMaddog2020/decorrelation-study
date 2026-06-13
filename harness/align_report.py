#!/usr/bin/env python3
"""Ground-truth alignment report.

For every truth/NN.json defect, print the code that actually sits at the
claimed line numbers. A defect is well-anchored when the cited lines contain
the construct its canonical description names. This is the human-readable
check behind the reconciliation gate: a reviewer reads each block and
confirms the cited lines are the defect, not blank lines or innocent code.

Usage: python3 harness/align_report.py [snippet_id ...]   (default: all)
"""
from __future__ import annotations
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNIP = ROOT / "corpus" / "snippets"
TRUTH = ROOT / "corpus" / "truth"


def report(sid: str) -> list[str]:
    """Return warning strings; empty means clean alignment."""
    warns = []
    tf = TRUTH / f"{sid}.json"
    sf = SNIP / f"{sid}.py"
    if not tf.exists() or not sf.exists():
        return [f"{sid}: MISSING file(s)"]
    truth = json.loads(tf.read_text())
    code = sf.read_text().splitlines()
    n = len(code)
    clean = truth.get("is_clean")
    defects = truth.get("defects", [])
    print(f"\n=== {sid}  ({truth.get('domain','?')})  "
          f"{'CLEAN' if clean else str(len(defects)) + ' defect(s)'} | {n} lines ===")
    if clean and not defects:
        print("  (clean control: no planted defects)")
    for d in defects:
        lines = d.get("lines", [])
        print(f"  {d['id']} [{d['type']}/{d.get('difficulty','?')}] lines={lines}")
        print(f"     canonical: {d['canonical']}")
        for ln in lines:
            if ln < 1 or ln > n:
                print(f"     L{ln}: <OUT OF RANGE, file has {n} lines>")
                warns.append(f"{sid}/{d['id']}: line {ln} out of range (1..{n})")
                continue
            text = code[ln - 1]
            blank = "  <<BLANK>>" if not text.strip() else ""
            print(f"     L{ln}: {text}{blank}")
            if not text.strip():
                warns.append(f"{sid}/{d['id']}: line {ln} is blank")
    return warns


if __name__ == "__main__":
    ids = sys.argv[1:] or sorted(p.stem for p in TRUTH.glob("*.json"))
    allwarn = []
    for sid in ids:
        allwarn = allwarn if False else allwarn
        allwarn.extend(report(sid))
    print("\n" + "=" * 60)
    if allwarn:
        print(f"ALIGNMENT WARNINGS ({len(allwarn)}):")
        for w in allwarn:
            print("  ! " + w)
    else:
        print("All cited lines are non-blank and in range.")
