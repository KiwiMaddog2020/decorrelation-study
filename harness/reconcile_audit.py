#!/usr/bin/env python3
"""Reconcile the Gemini external audit against the ground truth.

For each snippet: which planted defects did the blind Gemini audit independently
find, which Gemini findings match no planted defect (candidates for human
adjudication), and what realism / obvious-bug flags did it raise. Clean controls
are highlighted: any real finding there means the control is not actually clean.

Usage: python3 harness/reconcile_audit.py
"""
from __future__ import annotations
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TRUTH = ROOT / "corpus" / "truth"
AUDIT = ROOT / "runs" / "gemini_audit"
STOP = set(("the a an of to in is are be it its and or that this with not no for if "
            "as on by from into via when can could should may might will would code "
            "line lines value values method function does do has have which because "
            "so but only without instead at each more than less use used uses").split())


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{3,}", (s or "").lower()) if w not in STOP}


def g_lines(d: dict) -> set[int]:
    out = set()
    for x in d.get("lines", []) or []:
        try:
            out.add(int(x))
        except (TypeError, ValueError):
            pass
    return out


def matches(planted: dict, gd: dict) -> bool:
    pl, gl = set(planted.get("lines", [])), g_lines(gd)
    if pl and gl and any(min(abs(a - b) for b in gl) <= 2 for a in pl):
        return True
    shared = words(planted.get("canonical", "")) & words(gd.get("description", ""))
    return len(shared) >= 3


def main():
    found = missed = candidates = 0
    clean_hits = []
    lines = []
    for i in range(1, 21):
        sid = f"{i:02d}"
        t = json.loads((TRUTH / f"{sid}.json").read_text())
        a = json.loads((AUDIT / f"{sid}.json").read_text())
        planted = t.get("defects", [])
        gdefs = a.get("defects", []) or []
        is_clean = t.get("is_clean") or not planted
        matched_g = set()
        lines.append(f"\n=== {sid} {'[CLEAN]' if is_clean else ''}  "
                     f"realism={a.get('realism','?')} ===")
        for p in planted:
            hit = [j for j, gd in enumerate(gdefs) if matches(p, gd)]
            matched_g.update(hit)
            if hit:
                found += 1
                lines.append(f"  FOUND   {p['id']} [{p['type']}/{p.get('difficulty')}]")
            else:
                missed += 1
                lines.append(f"  MISSED  {p['id']} [{p['type']}/{p.get('difficulty')}] "
                             f":: {p['canonical'][:70]}")
        for j, gd in enumerate(gdefs):
            if j in matched_g:
                continue
            candidates += 1
            sev = gd.get("severity", "?")
            desc = (gd.get("description", "") or "")[:90]
            tag = "  CAND  "
            if is_clean:
                clean_hits.append((sid, sev, gd.get("type", "?"), desc))
                tag = "  !CLEAN"
            lines.append(f"{tag} g[{gd.get('type','?')}/{sev}] L{sorted(g_lines(gd))} :: {desc}")
        ob = a.get("obvious_bugs") or []
        if ob:
            lines.append(f"  gemini-obvious: {ob}")
    print("\n".join(lines))
    print("\n" + "=" * 64)
    print(f"PLANTED: {found} found by Gemini, {missed} missed  (of {found+missed})")
    print(f"CANDIDATES (Gemini findings not in ground truth): {candidates}")
    print(f"  of which on CLEAN controls: {len(clean_hits)}")
    if clean_hits:
        print("\nCLEAN-CONTROL FINDINGS (adjudicate: real bug => control not clean):")
        for sid, sev, typ, desc in clean_hits:
            print(f"  {sid} [{typ}/{sev}] {desc}")


if __name__ == "__main__":
    main()
