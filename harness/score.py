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


def _affinity(flag: dict, d: dict) -> int:
    """Heuristic affinity between a rater flag and a defect: a type-token match
    plus shared content words. Used to break ties when several defects sit on
    the same lines, so a co-located defect is credited to the rater flag that
    actually describes IT, not just to whichever defect is listed first."""
    score = 0
    ft, dt = flag.get("type", ""), d.get("type", "")
    if dt and (dt in ft or ft in dt):
        score += 2
    return score + len(words(flag["desc"]) & defect_keywords(d))


def match(flag: dict, defects: list[dict]) -> str | None:
    # 1) line overlap (+/-1). Among overlapping defects prefer the one whose
    #    type/content best fits the flag, so two different-typed defects on the
    #    same lines are not both auto-credited to the first one.
    hits = [
        d for d in defects
        if flag["lines"] and set(d.get("lines", []))
        and any(min(abs(fl - x) for x in d["lines"]) <= 1 for fl in flag["lines"])
    ]
    if hits:
        return max(hits, key=lambda d: _affinity(flag, d))["id"]
    # 2) no line overlap: best content match (>= 3 shared words), not just first.
    best, best_score = None, 2
    for d in defects:
        s = len(words(flag["desc"]) & defect_keywords(d))
        if s > best_score:
            best, best_score = d["id"], s
    return best


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
