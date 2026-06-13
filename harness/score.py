#!/usr/bin/env python3
"""Score one snippet's rater outputs against its ground-truth answer key.

A reviewer "catches" a recorded defect if one of its flags matches that defect
by line overlap or by content (type + shared keywords). Per pre-registration
amendment 1, a flag matching NO recorded defect is a CANDIDATE for human
adjudication, not an automatic false positive.

Usage: python3 harness/score.py <snippet_id> [runs_dir]
Default runs_dir: runs/smoke
"""
from __future__ import annotations
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RATERS = ["claude", "codex", "gemini"]
STOP = set(("the a an of to in is are be it its and or that this with not no for "
            "if as on by from into via when can cannot will would could should "
            "may might code line lines function value values input output return "
            "instead being which because so does do has have").split())


def parse_flags(text: str) -> list[dict]:
    flags = []
    for raw in text.splitlines():
        if "|" not in raw:
            continue
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) < 3:
            continue
        loc, typ, desc = parts[0], parts[1].lower(), "|".join(parts[2:])
        lines = set(int(n) for n in re.findall(r"\b(\d{1,4})\b", loc))
        flags.append({"loc": loc, "type": typ, "desc": desc, "lines": lines})
    return flags


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{3,}", s.lower()) if w not in STOP}


def defect_keywords(d: dict) -> set[str]:
    kw = set(re.findall(r"[a-z]{3,}", (d.get("subtype", "") + " ").lower()))
    kw |= words(d.get("canonical", ""))
    return kw


def match(flag: dict, defects: list[dict]) -> str | None:
    # 1) line overlap (with +/-1 tolerance) wins
    for d in defects:
        dl = set(d.get("lines", []))
        if flag["lines"] and dl and any(min(abs(fl - x) for x in dl) <= 1 for fl in flag["lines"]):
            return d["id"]
    # 2) content overlap: same type-family and >= 3 shared content words
    for d in defects:
        shared = words(flag["desc"]) & defect_keywords(d)
        if len(shared) >= 3:
            return d["id"]
    return None


def score_snippet(sid: str, runs_dir: pathlib.Path) -> dict:
    truth = json.loads((ROOT / "corpus" / "truth" / f"{sid}.json").read_text())
    defects = truth["defects"]
    out = {}
    for r in RATERS:
        f = runs_dir / f"{sid}.{r}.txt"
        if not f.exists():
            continue
        flags = parse_flags(f.read_text())
        caught, candidates = set(), []
        for fl in flags:
            m = match(fl, defects)
            if m:
                caught.add(m)
            else:
                candidates.append(fl["loc"] + " :: " + fl["desc"][:70])
        out[r] = {
            "caught": sorted(caught),
            "missed": sorted(d["id"] for d in defects if d["id"] not in caught),
            "candidates": candidates,
        }
    return {"snippet": sid, "n_defects": len(defects), "raters": out}


if __name__ == "__main__":
    sid = sys.argv[1] if len(sys.argv) > 1 else "001"
    runs_dir = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "runs" / "smoke"
    res = score_snippet(sid, runs_dir)
    print(f"snippet {res['snippet']}: {res['n_defects']} recorded defects\n")
    for r, sc in res["raters"].items():
        print(f"  {r:7} caught {len(sc['caught'])}/{res['n_defects']}: {sc['caught']}")
        if sc["missed"]:
            print(f"          missed: {sc['missed']}")
        if sc["candidates"]:
            print(f"          candidates (human-adjudicate): {len(sc['candidates'])}")
            for c in sc["candidates"]:
                print(f"            ? {c}")
