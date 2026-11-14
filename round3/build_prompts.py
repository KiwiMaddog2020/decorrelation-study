#!/usr/bin/env python3
"""Build the round 3 review prompts and the call manifest.

Usage: python3 round3/build_prompts.py --out DIR [--seed 20261114]

Writes DIR/prompts/r{1,2}-b{1..4}.txt, DIR/files/snippet-NN.txt and
DIR/manifest.json. Each prompt holds the per-snippet instructions from
protocol/review_prompt.txt verbatim and a short batch wrapper that points at
five snippet files. Each snippet file is the snippet exactly as it is in
corpus/snippets, on its own, so the line numbers a file viewer shows are the
snippet's own line numbers (see the amendment in PRE_REGISTRATION_R3.md).
Nothing here calls a model. Stdlib only.
"""
from __future__ import annotations
import argparse, json, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
IDS = [f"{i:02d}" for i in range(1, 21)]
BATCH_SIZE = 5
REVIEWS = (1, 2)
DEFAULT_SEED = 20261114
# Rater tier name -> requested model id.
TIERS = {
    "haiku": "claude-haiku-5-5",
    "sonnet": "claude-sonnet-5-5",
    "opus": "claude-opus-5-5",
    "fable": "claude-fable-5-2",
}
MARKER = "--- SNIPPET ---"

WRAPPER = """\

This task has {n} independent snippets instead of one. Each snippet is in its
own file, listed below. Apply the instructions above to each snippet on its own:
- Read each listed file once. Review each snippet separately. They are
  unrelated to each other.
- Line numbers restart at 1 for each snippet: line 1 is the first line of its
  file.
- Answer from the text only. Do not run code and do not use any tools other
  than reading the listed files.
- Reply with exactly one section per snippet, in any order. Each section starts
  with a line of the form `=== SNIPPET <ID> ===`, followed either by defect lines
  in the form `LOCATION | TYPE | DESCRIPTION` or by the exact line
  `NO DEFECTS FOUND`. Write nothing else.

The snippets are:
{files}
"""


def instructions() -> str:
    text = (ROOT / "protocol" / "review_prompt.txt").read_text()
    if MARKER not in text:
        sys.exit(f"protocol/review_prompt.txt has no {MARKER!r} line")
    return text.split(MARKER, 1)[0]


def partitions(seed: int) -> dict[int, list[list[str]]]:
    """Seeded random partition of the 20 snippets into 4 batches of 5, one
    partition per review, the two partitions different."""
    rng = random.Random(seed)
    out: dict[int, list[list[str]]] = {}
    seen: set = set()
    for rev in REVIEWS:
        while True:
            ids = IDS[:]
            rng.shuffle(ids)
            batches = [ids[i:i + BATCH_SIZE] for i in range(0, len(ids), BATCH_SIZE)]
            key = frozenset(frozenset(b) for b in batches)
            if key not in seen:
                seen.add(key)
                out[rev] = batches
                break
    return out


def snippet_rel(sid: str) -> str:
    return f"files/snippet-{sid}.txt"


def build_prompt(batch: list[str], out: pathlib.Path) -> str:
    files = "\n".join(f"- SNIPPET {sid}: {(out / snippet_rel(sid)).resolve()}" for sid in batch)
    return instructions().rstrip("\n") + "\n" + WRAPPER.format(n=len(batch), files=files)


def build(out: pathlib.Path, seed: int = DEFAULT_SEED) -> dict:
    (out / "prompts").mkdir(parents=True, exist_ok=True)
    (out / "raw").mkdir(parents=True, exist_ok=True)
    (out / "files").mkdir(parents=True, exist_ok=True)
    for sid in IDS:
        code = (ROOT / "corpus" / "snippets" / f"{sid}.py").read_text()
        (out / snippet_rel(sid)).write_text(code)
    calls, prompts = [], []
    for rev, batches in partitions(seed).items():
        for b, batch in enumerate(batches, 1):
            call_id = f"r{rev}-b{b}"
            rel = f"prompts/{call_id}.txt"
            text = build_prompt(batch, out)
            (out / rel).write_text(text)
            prompts.append({"call_id": call_id, "review": rev, "batch": b,
                            "prompt_path": rel, "snippet_ids": batch,
                            "snippet_paths": [snippet_rel(x) for x in batch]})
    for tier, model in TIERS.items():
        for p in prompts:
            calls.append({
                "call_id": p["call_id"], "tier": tier, "requested_model": model,
                "review": p["review"], "rater": f"{tier}{p['review']}",
                "prompt_path": p["prompt_path"],
                "answer_path": f"raw/{tier}__{p['call_id']}.txt",
                "snippet_ids": p["snippet_ids"],
            })
    manifest = {
        "seed": seed, "batch_size": BATCH_SIZE, "tiers": TIERS,
        "paths_are_relative_to": "the run directory given to --out",
        "prompts": prompts, "calls": calls,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    a = ap.parse_args(argv)
    m = build(a.out, a.seed)
    print(f"wrote {len(m['prompts'])} prompts and {len(m['calls'])} calls to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
