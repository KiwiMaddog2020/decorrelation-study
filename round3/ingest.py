#!/usr/bin/env python3
"""Split round 3 raw answers into one review file per (snippet, rater).

Usage: python3 round3/ingest.py --run DIR [--dest round3] [--allow-partial]

Reads DIR/manifest.json and DIR/raw/<tier>__<call_id>.txt, splits each answer
on its `=== SNIPPET <ID> ===` lines and checks that every expected snippet is
present exactly once. Then writes, under --dest (default: this folder):
  runs/full/NN.<rater>.txt     rater = tier + review number, e.g. sonnet2
  runs/full/NN.opus48_then.txt copy of the July review runs/full/NN.claude.txt
  raw/<tier>__<call_id>.txt    copy of each raw answer
  manifest.json                copy of the run manifest
Exits non-zero on any problem unless --allow-partial, in which case the valid
sections are still written. Never overwrites a file with different content.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).resolve().parent
IDS = [f"{i:02d}" for i in range(1, 21)]
THEN_RATER = "opus48_then"
HEADER = re.compile(r"^[\s#*>`]*=+\s*SNIPPET\s+(\d{1,3})\s*=+[\s*`]*$", re.I)
FENCE = re.compile(r"^\s*```[\w-]*\s*$")
NO_DEFECTS = "NO DEFECTS FOUND"


def split_sections(text: str):
    """Return (sections, stray). sections is a list of (snippet_id, body);
    stray is any non-blank text before the first section header."""
    sections, stray, cur, body = [], [], None, []
    for line in text.splitlines():
        if FENCE.match(line):
            continue
        m = HEADER.match(line)
        if m:
            if cur is not None:
                sections.append((cur, body))
            cur, body = f"{int(m.group(1)):02d}", []
        elif cur is None:
            if line.strip():
                stray.append(line)
        else:
            body.append(line)
    if cur is not None:
        sections.append((cur, body))
    out = []
    for sid, lines in sections:
        while lines and not lines[0].strip():
            lines = lines[1:]
        while lines and not lines[-1].strip():
            lines = lines[:-1]
        out.append((sid, "\n".join(l.rstrip() for l in lines)))
    return out, stray


def check_body(body: str) -> tuple[str | None, str | None]:
    """(problem, warning) for one section. A problem makes the section unusable;
    a warning is kept and scored as written (the scorer modes decide what an
    odd line is worth)."""
    if not body.strip():
        return "empty section", None
    lines = [l for l in body.splitlines() if l.strip()]
    if any(l.strip().strip("`*").rstrip(".").upper() == NO_DEFECTS for l in lines):
        if len(lines) > 1:
            return None, "NO DEFECTS FOUND mixed with other lines"
        return None, None
    if not any(l.count("|") >= 2 for l in lines):
        return "neither NO DEFECTS FOUND nor a LOCATION | TYPE | DESCRIPTION line", None
    return None, None


def plan(run: pathlib.Path, dest: pathlib.Path):
    """Work out every file to write without writing anything.
    Returns (writes: dict[path, text], problems: list[str], warnings)."""
    problems, warnings = [], []
    man_path = run / "manifest.json"
    if not man_path.exists():
        return {}, [f"missing {man_path}"], []
    manifest_text = man_path.read_text()
    manifest = json.loads(manifest_text)
    writes: dict[pathlib.Path, str] = {dest / "manifest.json": manifest_text}
    seen: dict[tuple[str, str], str] = {}
    for call in manifest["calls"]:
        raw_path = run / call["answer_path"]
        tag = f"{call['tier']}__{call['call_id']}"
        if not raw_path.exists():
            problems.append(f"{tag}: missing answer file {call['answer_path']}")
            continue
        text = raw_path.read_text()
        writes[dest / "raw" / raw_path.name] = text
        sections, stray = split_sections(text)
        if stray:
            warnings.append(f"{tag}: ignored {len(stray)} line(s) before the first section")
        expected = list(call["snippet_ids"])
        got = [sid for sid, _ in sections]
        for sid in sorted(set(got)):
            if got.count(sid) > 1:
                problems.append(f"{tag}: snippet {sid} appears {got.count(sid)} times")
            if sid not in expected:
                problems.append(f"{tag}: unexpected snippet {sid}")
        for sid in expected:
            if sid not in got:
                problems.append(f"{tag}: snippet {sid} missing")
        for sid, body in sections:
            if sid not in expected or got.count(sid) != 1:
                continue
            bad, odd = check_body(body)
            if odd:
                warnings.append(f"{tag}: snippet {sid}: {odd}")
            if bad:
                problems.append(f"{tag}: snippet {sid}: {bad}")
                continue
            key = (sid, call["rater"])
            if key in seen:
                problems.append(f"{tag}: snippet {sid} already answered for "
                                f"{call['rater']} by {seen[key]}")
                continue
            seen[key] = tag
            writes[dest / "runs" / "full" / f"{sid}.{call['rater']}.txt"] = body + "\n"
    for sid in IDS:
        src = ROOT / "runs" / "full" / f"{sid}.claude.txt"
        if src.exists():
            writes[dest / "runs" / "full" / f"{sid}.{THEN_RATER}.txt"] = src.read_text()
        else:
            problems.append(f"then row: missing {src.relative_to(ROOT)}")
    return writes, problems, warnings


def conflicts(writes: dict[pathlib.Path, str]) -> list[str]:
    return [str(p) for p, t in writes.items() if p.exists() and p.read_text() != t]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True, type=pathlib.Path)
    ap.add_argument("--dest", type=pathlib.Path, default=HERE)
    ap.add_argument("--allow-partial", action="store_true")
    a = ap.parse_args(argv)
    writes, problems, warnings = plan(a.run, a.dest)
    for w in warnings:
        print(f"warning: {w}")
    for p in problems:
        print(f"problem: {p}")
    if problems and not a.allow_partial:
        print(f"{len(problems)} problem(s); nothing written (use --allow-partial to "
              "write the valid sections anyway)")
        return 1
    clash = conflicts(writes)
    if clash:
        for c in clash:
            print(f"refusing to overwrite (different content): {c}")
        return 2
    new = 0
    for path, text in writes.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        new += 1
    print(f"wrote {new} new file(s), {len(writes) - new} already identical, "
          f"{len(problems)} problem(s)")
    return 1 if problems and not a.allow_partial else 0


if __name__ == "__main__":
    sys.exit(main())
