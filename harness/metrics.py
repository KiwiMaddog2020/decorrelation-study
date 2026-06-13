#!/usr/bin/env python3
"""Compute the pre-registered metrics from the scored reviews.

Loads every rater's review (runs/full/NN.<rater>.txt), scores each against
ground truth via the shared score.py matcher, and reports:
  - per-rater catch count and false-positive count (flags on clean controls)
  - pairwise phi / Matthews correlation over the caught/missed vectors (H2)
  - coverage payoff: union caught / best single (H1)
  - per-type catch rate by family (H5)
  - unanimity structure (H4, exploratory)

The human family (Kevin) is included automatically once runs/full/NN.human.txt
files exist; until then this is the model-only result.
"""
from __future__ import annotations
import importlib.util, json, math, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("score", ROOT / "harness" / "score.py")
score = importlib.util.module_from_spec(spec); spec.loader.exec_module(score)

IDS = [f"{i:02d}" for i in range(1, 21)]
CLEAN = {"16", "17", "18", "19"}
BASE_RATERS = ["claude", "gemini", "codex"]


def load_truth():
    defects = []  # (id, type, difficulty, sid)
    for sid in IDS:
        t = json.loads((ROOT / "corpus" / "truth" / f"{sid}.json").read_text())
        for d in t.get("defects", []):
            defects.append((d["id"], d["type"], d.get("difficulty"), sid))
    return defects


def phi(x, y):
    n11 = sum(a and b for a, b in zip(x, y))
    n00 = sum((not a) and (not b) for a, b in zip(x, y))
    n10 = sum(a and (not b) for a, b in zip(x, y))
    n01 = sum((not a) and b for a, b in zip(x, y))
    denom = math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
    return (n11 * n00 - n10 * n01) / denom if denom else 0.0


def main():
    defects = load_truth()
    all_ids = [d[0] for d in defects]
    type_of = {d[0]: d[1] for d in defects}
    # which raters are present
    raters = [r for r in BASE_RATERS + ["human"]
              if any((ROOT / "runs" / "full" / f"{sid}.{r}.txt").exists() for sid in IDS)]

    caught = {r: set() for r in raters}
    fp = {r: 0 for r in raters}
    cand = {r: [] for r in raters}
    for sid in IDS:
        res = score.score_snippet(sid, ROOT / "runs" / "full")
        for r in raters:
            sc = res["raters"].get(r)
            if not sc:
                continue
            caught[r].update(sc["caught"])
            if sid in CLEAN:
                fp[r] += len(sc["candidates"])
            else:
                cand[r].extend(f"{sid}: {c}" for c in sc["candidates"])

    vec = {r: [1 if did in caught[r] else 0 for did in all_ids] for r in raters}
    N = len(all_ids)

    print(f"=== rater performance (over {N} planted defects, 4 clean controls) ===")
    for r in raters:
        print(f"  {r:7} caught {len(caught[r]):2}/{N}  "
              f"false-positives {fp[r]:2}  candidates(defective) {len(cand[r])}")

    print("\n=== pairwise error correlation (phi over caught/missed) [H2] ===")
    pairs = [(a, b) for i, a in enumerate(raters) for b in raters[i + 1:]]
    corrs = {}
    for a, b in pairs:
        c = phi(vec[a], vec[b])
        corrs[(a, b)] = c
        print(f"  corr({a}, {b}) = {c:+.3f}")

    print("\n=== coverage payoff [H1] ===")
    union = set().union(*[caught[r] for r in raters]) if raters else set()
    best = max((len(caught[r]) for r in raters), default=0)
    payoff = len(union) / best if best else 0
    print(f"  union caught {len(union)}/{N}, best single {best}  ->  payoff {payoff:.2f}x "
          f"(pre-reg interest: >= 1.20x)")

    print("\n=== per-type catch rate by family [H5] ===")
    by_type = collections.defaultdict(list)
    for did, typ in type_of.items():
        by_type[typ].append(did)
    hdr = "  type            " + "".join(f"{r[:6]:>8}" for r in raters)
    print(hdr)
    for typ in sorted(by_type):
        ids = by_type[typ]
        row = f"  {typ:14} ({len(ids):2})"
        for r in raters:
            hit = sum(1 for d in ids if d in caught[r])
            row += f"{hit}/{len(ids):>5}"
        print(row)

    print("\n=== unanimity structure [H4, exploratory] ===")
    model_raters = [r for r in raters if r != "human"]
    allc = sum(1 for did in all_ids if all(did in caught[r] for r in model_raters))
    allm = sum(1 for did in all_ids if all(did not in caught[r] for r in model_raters))
    print(f"  all models caught: {allc}   all models missed: {allm}   split: {N - allc - allm}")

    (ROOT / "runs" / "RESULTS.json").write_text(json.dumps({
        "raters": raters, "n_defects": N,
        "caught": {r: sorted(caught[r]) for r in raters},
        "false_positives": fp,
        "correlations": {f"{a}|{b}": round(v, 3) for (a, b), v in corrs.items()},
        "coverage_payoff": round(payoff, 3),
        "union_caught": len(union), "best_single": best,
    }, indent=2) + "\n")
    print("\nwrote runs/RESULTS.json")


if __name__ == "__main__":
    main()
