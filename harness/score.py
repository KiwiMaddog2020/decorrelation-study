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
import json, os, re, sys, pathlib

# Strict (pre-registered) matcher by default. SCORE_STEM=1 enables a lenient
# 5-char-prefix stemming variant, used only to report the result's sensitivity
# to the matching rule -- never as the canonical scorer.
_STEM = os.environ.get("SCORE_STEM", "0") == "1"

# Opt-in stricter modes, off by default so the published numbers reproduce.
# SCORE_HEADERS=1: drop rows that are not defect flags (an echoed
#   "LOCATION | TYPE | DESCRIPTION" header, a markdown table separator, or a
#   row with neither an allowed TYPE nor a line number in LOCATION).
# SCORE_DESCRIBED=1: a line-overlap match only counts when the flag also has
#   some affinity with the defect (type token or a shared content word);
#   otherwise the flag falls through to the content matcher.
_HEADERS = os.environ.get("SCORE_HEADERS", "0") == "1"
_DESCRIBED = os.environ.get("SCORE_DESCRIBED", "0") == "1"

# The eight TYPE values allowed by protocol/review_prompt.txt.
ALLOWED_TYPES = ("logic", "security", "concurrency", "boundary", "api-misuse",
                 "performance", "spec-violation", "other")

ROOT = pathlib.Path(__file__).resolve().parent.parent
RATERS = ["claude", "codex", "gemini"]
STOP = set(("the a an of to in is are be it its and or that this with not no for "
            "if as on by from into via when can cannot will would could should "
            "may might code line lines function value values input output return "
            "instead being which because so does do has have").split())


def normalize_type(field: str) -> str:
    """Strip case, surrounding markdown (backticks, asterisks, underscores) and
    an optional "TYPE:" label from a TYPE field, e.g. "**Logic**" -> "logic"."""
    t = field.strip().strip("`*_ ").lower()
    t = re.sub(r"^type\s*:\s*", "", t)
    return t.strip("`*_ ")


def _is_separator(parts: list[str]) -> bool:
    return all(re.fullmatch(r"[\s:\-=+]*", p) for p in parts)


def parse_flags(text: str, filter_headers: bool | None = None) -> list[dict]:
    """Parse "LOCATION | TYPE | DESCRIPTION" rows into flags.

    Default (filter_headers False, or SCORE_HEADERS unset): any line with two or
    more pipes is a flag, exactly as pre-registered. With filter_headers True,
    outer table pipes are stripped and header rows, separator rows and rows with
    neither an allowed TYPE nor a line number are dropped. Matching is unchanged either way.
    """
    if filter_headers is None:
        filter_headers = _HEADERS
    flags = []
    for raw in text.splitlines():
        if "|" not in raw:
            continue
        if filter_headers:
            row = raw.strip()
            if row.startswith("|"):
                row = row[1:]
            if row.endswith("|"):
                row = row[:-1]
            parts = [p.strip() for p in row.split("|")]
            if len(parts) < 3 or _is_separator(parts):
                continue
            if normalize_type(parts[1]) not in ALLOWED_TYPES:
                # An off-list type on a row that still points at a line number
                # is a real flag with a sloppy label (e.g. "contract"); keep it
                # so false positives are not under-counted. Rows with neither an
                # allowed type nor a line number are headers or prose.
                if normalize_type(parts[1]) == "type" or not re.search(r"\d", parts[0]):
                    continue
        else:
            parts = [p.strip() for p in raw.split("|")]
        if len(parts) < 3:
            continue
        loc, typ, desc = parts[0], parts[1].lower(), "|".join(parts[2:])
        lines = set(int(n) for n in re.findall(r"\b(\d{1,4})\b", loc))
        flags.append({"loc": loc, "type": typ, "desc": desc, "lines": lines})
    return flags


def words(s: str) -> set[str]:
    toks = [w for w in re.findall(r"[a-z]{3,}", s.lower()) if w not in STOP]
    # Lenient variant collapses tokens to a 5-char prefix so terse rater wording
    # matches the answer key across inflections (recency~recently). Off = strict.
    return {w[:5] for w in toks} if _STEM else set(toks)


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


def match(flag: dict, defects: list[dict], described: bool | None = None) -> str | None:
    if described is None:
        described = _DESCRIBED
    # 1) line overlap (+/-1). Among overlapping defects prefer the one whose
    #    type/content best fits the flag, so two different-typed defects on the
    #    same lines are not both auto-credited to the first one.
    hits = [
        d for d in defects
        if flag["lines"] and set(d.get("lines", []))
        and any(min(abs(fl - x) for x in d["lines"]) <= 1 for fl in flag["lines"])
    ]
    if described:
        # Opt-in: being near a defect is not enough, the flag must also say
        # something about it. Unrelated nearby flags fall through to step 2.
        hits = [d for d in hits if _affinity(flag, d) > 0]
    if hits:
        return max(hits, key=lambda d: _affinity(flag, d))["id"]
    # 2) no line overlap: best content match (>= 3 shared words), not just first.
    best, best_score = None, 2
    for d in defects:
        s = len(words(flag["desc"]) & defect_keywords(d))
        if s > best_score:
            best, best_score = d["id"], s
    return best


def score_snippet(sid: str, runs_dir: pathlib.Path, raters: list[str] | None = None,
                  filter_headers: bool | None = None,
                  described: bool | None = None) -> dict:
    """Score one snippet. raters defaults to RATERS; the two mode switches
    default to the SCORE_HEADERS / SCORE_DESCRIBED environment variables."""
    truth = json.loads((ROOT / "corpus" / "truth" / f"{sid}.json").read_text())
    defects = truth["defects"]
    out = {}
    for r in (RATERS if raters is None else raters):
        f = runs_dir / f"{sid}.{r}.txt"
        if not f.exists():
            continue
        flags = parse_flags(f.read_text(), filter_headers)
        caught, candidates = set(), []
        for fl in flags:
            m = match(fl, defects, described)
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
