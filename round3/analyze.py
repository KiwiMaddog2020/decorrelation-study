#!/usr/bin/env python3
"""Score round 3 and write round3/RESULTS.json and round3/RESULTS.md.

Usage: python3 round3/analyze.py [--root round3] [--boot 10000] [--seed 20261114]

Every rater in ROOT/runs/full is scored with the existing harness (score.py via
metrics.py, nothing re-implemented) in three modes: original, headers
(header-filtered, the primary mode) and headers_described. The report text is
generated from the numbers; nothing in it is written in advance.
"""
from __future__ import annotations
import argparse, importlib.util, itertools, json, pathlib, random, statistics, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location("r3_metrics", ROOT / "harness" / "metrics.py")
metrics = importlib.util.module_from_spec(spec); spec.loader.exec_module(metrics)
score = metrics.score

TIERS = ["haiku", "sonnet", "opus", "fable"]
REVIEWS = [1, 2]
THEN = "opus48_then"
MODES = {  # name -> (filter_headers, described)
    "original": (False, False),
    "headers": (True, False),
    "headers_described": (True, True),
}
PRIMARY = "headers"
# Pre-registered decision rule (round3/PRE_REGISTRATION_R3.md), in defects.
COVER_MIN_D = 1.0
SAME_MAX_CI_HIGH = 2.0


def rater(t, r):
    return f"{t}{r}"


def present_raters(runs_dir: pathlib.Path) -> tuple[list[str], dict[str, list[str]]]:
    wanted = [rater(t, r) for t in TIERS for r in REVIEWS] + [THEN]
    present, missing = [], {}
    for name in wanted:
        have = [sid for sid in metrics.IDS if (runs_dir / f"{sid}.{name}.txt").exists()]
        if have:
            present.append(name)
            if len(have) < len(metrics.IDS):
                missing[name] = [s for s in metrics.IDS if s not in have]
    return present, missing


def phi_or_none(x, y):
    if len(set(x)) < 2 or len(set(y)) < 2:
        return None  # undefined when one vector is constant
    return metrics.phi(x, y)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def pair_stats(vec, a, b):
    ua = sum(1 for x, y in zip(vec[a], vec[b]) if x or y)
    best = max(sum(vec[a]), sum(vec[b]))
    return {"a": a, "b": b, "union": ua, "best_single": best, "gain": ua - best,
            "phi": phi_or_none(vec[a], vec[b])}


def same_pairs(raters):
    return [(rater(t, 1), rater(t, 2)) for t in TIERS
            if rater(t, 1) in raters and rater(t, 2) in raters]


def cross_pairs(raters):
    out = []
    for t, u in itertools.combinations(TIERS, 2):
        for ra in REVIEWS:
            for rb in REVIEWS:
                a, b = rater(t, ra), rater(u, rb)
                if a in raters and b in raters:
                    out.append((a, b))
    return out


def gain_diff(vec, sp, cp, idx=None):
    """mean cross-tier pair gain minus mean same-tier pair gain, optionally on a
    resample idx of defect positions."""
    def g(a, b):
        xa = vec[a] if idx is None else [vec[a][i] for i in idx]
        xb = vec[b] if idx is None else [vec[b][i] for i in idx]
        return sum(1 for x, y in zip(xa, xb) if x or y) - max(sum(xa), sum(xb))
    return (statistics.fmean(g(a, b) for a, b in cp)
            - statistics.fmean(g(a, b) for a, b in sp))


def bootstrap(vec, sp, cp, n_def, boots, seed):
    if not sp or not cp or boots <= 0:
        return None
    rng = random.Random(seed)
    vals = sorted(gain_diff(vec, sp, cp, [rng.randrange(n_def) for _ in range(n_def)])
                  for _ in range(boots))
    lo, hi = vals[int(0.025 * boots)], vals[min(boots - 1, int(0.975 * boots))]
    return {"boots": boots, "seed": seed, "ci95": [lo, hi],
            "share_above_zero": sum(v > 0 for v in vals) / boots}


def verdict(d, ci):
    if d is None or ci is None:
        return "not computable (missing reviews)"
    if d >= COVER_MIN_D and ci[0] > 0:
        return "tiers cover each other"
    if d < COVER_MIN_D and ci[1] < SAME_MAX_CI_HIGH:
        return "a second look is just as good"
    return "inconclusive at this sample size"


def analyze_mode(runs_dir, raters, fh, de, boots, seed):
    c = metrics.compute(runs_dir, raters, fh, de)
    ids, vec, caught, type_of = c["all_ids"], c["vec"], c["caught"], c["type_of"]
    types = sorted(set(type_of.values()))
    per = {}
    for r in raters:
        per[r] = {
            "caught": len(caught[r]), "caught_ids": sorted(caught[r]),
            "false_positives_clean": c["fp"][r],
            "candidates_defective": len(c["cand"][r]),
            "by_type": {t: sum(1 for d in ids if type_of[d] == t and d in caught[r])
                        for t in types},
        }
    sp, cp = same_pairs(raters), cross_pairs(raters)
    same = [pair_stats(vec, a, b) for a, b in sp]
    cross = [pair_stats(vec, a, b) for a, b in cp]
    summary = {
        "same_tier": {"n_pairs": len(same),
                      "mean_union": mean([p["union"] for p in same]),
                      "mean_gain": mean([p["gain"] for p in same]),
                      "mean_phi": mean([p["phi"] for p in same])},
        "cross_tier": {"n_pairs": len(cross),
                       "mean_union": mean([p["union"] for p in cross]),
                       "mean_gain": mean([p["gain"] for p in cross]),
                       "mean_phi": mean([p["phi"] for p in cross])},
    }
    d = gain_diff(vec, sp, cp) if sp and cp else None
    boot = bootstrap(vec, sp, cp, len(ids), boots, seed)
    # union of all four tiers, one review each, every choice of review
    combos = []
    if all(rater(t, r) in raters for t in TIERS for r in REVIEWS):
        for choice in itertools.product(REVIEWS, repeat=len(TIERS)):
            members = [rater(t, r) for t, r in zip(TIERS, choice)]
            u = sum(1 for i in range(len(ids)) if any(vec[m][i] for m in members))
            best = max(sum(vec[m]) for m in members)
            combos.append({"members": members, "union": u, "best_single": best,
                           "gain": u - best, "payoff": round(u / best, 3) if best else None})
    r3 = [r for r in raters if r != THEN]
    missed_all = [d_ for i, d_ in enumerate(ids) if r3 and not any(vec[r][i] for r in r3)]
    then = None
    if THEN in raters:
        then = {"caught": len(caught[THEN]), "vs": {}}
        for r in REVIEWS:
            o = rater("opus", r)
            if o in raters:
                then["vs"][o] = {"both": len(caught[THEN] & caught[o]),
                                 "then_only": sorted(caught[THEN] - caught[o]),
                                 "now_only": sorted(caught[o] - caught[THEN]),
                                 "phi": phi_or_none(vec[THEN], vec[o])}
        then["missed_by_all_round3_caught_then"] = sorted(set(missed_all) & caught[THEN])
    return {
        "n_defects": len(ids), "raters": per, "same_tier_pairs": same,
        "cross_tier_pairs": cross, "summary": summary,
        "gain_difference_cross_minus_same": d, "bootstrap": boot,
        "verdict_by_preregistered_rule": verdict(d, boot["ci95"] if boot else None),
        "four_tier_unions": combos, "missed_by_every_round3_review": missed_all,
        "then_row": then, "defect_types": {t: sum(1 for x in type_of.values() if x == t)
                                           for t in types},
    }


def fmt(x, nd=2):
    if x is None:
        return "n/a"
    return f"{x:+.{nd}f}" if isinstance(x, float) and x < 0 else (
        f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def render_md(res: dict) -> str:
    L = ["# Round 3 results", "",
         "Generated by `round3/analyze.py` from the scored reviews. Do not edit by hand.",
         "Pre-registration: `round3/PRE_REGISTRATION_R3.md`.", ""]
    if res["incomplete_raters"]:
        L += ["**Incomplete reviews:** " + "; ".join(
            f"{r} missing {', '.join(s)}" for r, s in res["incomplete_raters"].items()), ""]
    for mode, m in res["modes"].items():
        tag = " (primary)" if mode == PRIMARY else ""
        N = m["n_defects"]
        L += [f"## Mode: {mode}{tag}", "", "### Per rater", "",
              f"| rater | caught of {N} | false positives on 4 clean | candidates on defective | "
              + " | ".join(f"{t} ({n})" for t, n in m["defect_types"].items()) + " |",
              "|---" * (4 + len(m["defect_types"])) + "|"]
        for r, p in m["raters"].items():
            L.append(f"| {r} | {p['caught']} | {p['false_positives_clean']} | "
                     f"{p['candidates_defective']} | "
                     + " | ".join(str(v) for v in p["by_type"].values()) + " |")
        s = m["summary"]
        L += ["", "### Pairs of reviews", "",
              "| pairs | n | mean union caught | mean gain over better single | mean phi |",
              "|---|---|---|---|---|",
              f"| same tier (review 1 + review 2) | {s['same_tier']['n_pairs']} | "
              f"{fmt(s['same_tier']['mean_union'])} | {fmt(s['same_tier']['mean_gain'])} | "
              f"{fmt(s['same_tier']['mean_phi'], 3)} |",
              f"| cross tier (all combinations) | {s['cross_tier']['n_pairs']} | "
              f"{fmt(s['cross_tier']['mean_union'])} | {fmt(s['cross_tier']['mean_gain'])} | "
              f"{fmt(s['cross_tier']['mean_phi'], 3)} |", "",
              "Same-tier pairs: " + ", ".join(
                  f"{p['a']}+{p['b']} union {p['union']}, gain {p['gain']}, phi {fmt(p['phi'], 3)}"
                  for p in m["same_tier_pairs"]) + ".", ""]
        b = m["bootstrap"]
        L.append(f"Gain difference (mean cross-tier gain minus mean same-tier gain): "
                 f"{fmt(m['gain_difference_cross_minus_same'])} defects.")
        if b:
            L.append(f"Bootstrap over the {N} defects ({b['boots']} resamples, seed "
                     f"{b['seed']}): 95% interval {fmt(b['ci95'][0])} to {fmt(b['ci95'][1])}; "
                     f"share of resamples above zero {b['share_above_zero']:.3f}.")
        L += [f"Outcome under the pre-registered rule: **{m['verdict_by_preregistered_rule']}**.", ""]
        if m["four_tier_unions"]:
            us = m["four_tier_unions"]
            L += ["### All four tiers together (one review each)", "",
                  "| reviews | union caught | best single | gain | payoff |", "|---|---|---|---|---|"]
            for cmb in us:
                if len({x[-1] for x in cmb["members"]}) == 1:
                    L.append(f"| all review {cmb['members'][0][-1]} | {cmb['union']} | "
                             f"{cmb['best_single']} | {cmb['gain']} | {fmt(cmb['payoff'], 3)} |")
            L += ["", f"Over all {len(us)} ways to pick one review per tier: union "
                  f"{min(c['union'] for c in us)} to {max(c['union'] for c in us)}, "
                  f"gain {min(c['gain'] for c in us)} to {max(c['gain'] for c in us)}.", ""]
        mi = m["missed_by_every_round3_review"]
        L += [f"Defects missed by every round 3 review ({len(mi)}): "
              + (", ".join(mi) if mi else "none") + ".", ""]
        t = m["then_row"]
        if t:
            L.append(f"Then row: the July review ({THEN}) caught {t['caught']} of {N}.")
            for o, v in t["vs"].items():
                L.append(f"Against {o}: both caught {v['both']}, July only "
                         f"{', '.join(v['then_only']) or 'none'}, {o} only "
                         f"{', '.join(v['now_only']) or 'none'}, phi {fmt(v['phi'], 3)}.")
            L.append("")
    L += ["## What this sample can and cannot support", "",
          f"- There are {res['n_defects']} planted defects, two reviews per tier and one model "
          "family. One defect is about 3 percentage points, so small differences are noise.",
          "- The bootstrap resamples defects only. It does not capture run to run variation "
          "beyond the two reviews per tier, so its interval is optimistic.",
          "- Pairs share members, so the pair counts are not independent observations.",
          "- Results speak to this corpus and these model versions only. They cannot show "
          "that tiers differ in general, or say anything about other model families.",
          "- The July review was one snippet per call; round 3 batches five per call, so the "
          "then row mixes a model change with a format change.", ""]
    return "\n".join(L)


def run(root: pathlib.Path, boots: int, seed: int) -> dict:
    if score._STEM:
        sys.exit("SCORE_STEM=1 is set; round 3 uses the strict word matcher. Unset it.")
    runs_dir = root / "runs" / "full"
    raters, missing = present_raters(runs_dir)
    if not raters:
        sys.exit(f"no round 3 reviews found in {runs_dir}")
    res = {"n_defects": None, "raters": raters, "incomplete_raters": missing,
           "primary_mode": PRIMARY, "modes": {}}
    for mode, (fh, de) in MODES.items():
        res["modes"][mode] = analyze_mode(runs_dir, raters, fh, de, boots, seed)
    res["n_defects"] = res["modes"][PRIMARY]["n_defects"]
    (root / "RESULTS.json").write_text(json.dumps(res, indent=2) + "\n")
    (root / "RESULTS.md").write_text(render_md(res))
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=pathlib.Path, default=HERE)
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20261114)
    a = ap.parse_args(argv)
    res = run(a.root, a.boot, a.seed)
    m = res["modes"][PRIMARY]
    print(f"raters: {', '.join(res['raters'])}")
    print(f"primary ({PRIMARY}) gain difference {fmt(m['gain_difference_cross_minus_same'])}: "
          f"{m['verdict_by_preregistered_rule']}")
    print(f"wrote {a.root / 'RESULTS.json'} and {a.root / 'RESULTS.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
