# Forking-paths ledger: every researcher degree of freedom in the scorer

**Status: audit artifact (methodology lens). Adds no claim, changes no published
number, touches no corpus or ground truth.** It names every unfixed choice in the
scoring instrument that can move a conclusion, records the verified harness output
for each, and pre-commits the choices a future round must freeze BEFORE seeing new
data. Written after the model-only results were already published, so it cannot
retroactively launder them; its job is to keep the next round honest.

The study already discloses, honestly, that H2 flips on the stemmed-matcher knob
and on the 29-vs-30 answer-key knob (RESULTS_model_only.md, docs/index.md). This
ledger's contribution is that those are not the only two knobs, and the published
wording ("a single scoring choice", "a single adjudication call") understates the
true dimensionality of the forking space.

## How to reproduce the numbers below

All numbers come from the existing tested harness, no new analysis code shipped:

```bash
python3 harness/align_report.py          # every cited line is live code
python3 harness/metrics.py               # strict (pre-registered) scoring
SCORE_STEM=1 python3 harness/metrics.py  # lenient sensitivity variant
```

The cross-knob sweep below was produced by driving the SAME `harness/score.py`
matcher with its three internal constants varied, no change to the scoring logic.

## The knobs

### Knob A: token stemming (`SCORE_STEM`) — DISCLOSED

`harness/score.py:18,46`. Off (strict, pre-registered) compares whole content
tokens; on (lenient) collapses to a 5-char prefix. Disclosed in the write-up.

- strict:  claude caught 23, gemini 27, codex 21
- lenient: claude caught 23, gemini 28, codex 23

### Knob B: which defects are in the answer key (29 vs 30) — DISCLOSED, but the decisive element is outcome-correlated

`11-d5` (`minconn > maxconn`, boundary/subtle) was added to the answer key in commit
`8e80876` — the SAME commit that reframed H2 as scoring-sensitive. It was caught by
**Claude and Codex but not Gemini** (verified: `grep -i minconn runs/full/11.*.txt`
returns Claude and Codex, Gemini empty). Crediting a Claude+Codex / not-Gemini
defect mechanically raises corr(claude,codex) and lowers corr(gemini,codex), which
is exactly the pair ordering H2 is about. So the single answer-key element that
flips H2 was adjudicated in after the reviews were visible.

Verified phi (reconstructed by dropping 11-d5 from the id list, real truth file
untouched):

| answer key | corr(cl,cx) | corr(gm,cx) | corr(cl,gm) | highest pair | H2 |
|------------|-------------|-------------|-------------|--------------|----|
| 29 defects | +0.318      | **+0.406**  | -0.154      | gemini-codex | refuted |
| 30 defects | **+0.327**  | +0.267      | -0.184      | claude-codex | holds   |

Amendment 1 (Change 1) did pre-register the *procedure* (unmatched flag -> candidate
-> human adjudicates -> if real, credited). What it did NOT freeze is a rule for the
adjudication itself, so "the human decides" is an unbounded degree of freedom sitting
directly on the hypothesis it decides. This is the sharpest forking path in the study.

### Knob C: line-overlap tolerance — UNDISCLOSED, and it also flips H2

`harness/score.py:74`, hard-coded `<= 1`. A flag's cited line must fall within this
many lines of a defect's recorded lines to count as a location match. ±1 is a choice;
±0 and ±2 are equally defensible. Verified sweep (strict matcher, 30 defects,
content threshold held at its default 2):

| line gap | corr(cl,cx) | corr(gm,cx) | highest pair | H2 |
|----------|-------------|-------------|--------------|----|
| 0        | +0.327      | +0.267      | claude-codex | holds   |
| 1 (live) | +0.327      | +0.267      | claude-codex | holds   |
| 2        | **+0.218**  | **+0.267**  | gemini-codex | refuted |

At ±2 the verdict flips to refuted. The published claim that the flip rides on "a
single scoring choice" is therefore an understatement: at least two independent,
undisclosed-or-disclosed knobs (B and C) each flip H2 on their own.

### Knob D: content-match threshold — UNDISCLOSED

`harness/score.py:79`, hard-coded `best_score = 2` (a no-line-overlap flag needs
strictly more than 2 shared content words to match). Moving it 2->3 changes catch
counts (e.g. strict gemini 27->25 at gap 0) and shifts every correlation. It does not
flip H2's top pair on its own in the cells swept, but it is a live, undisclosed knob
that interacts with B and C and changes the H1 payoff (1.11x -> 1.16x at gap 0,
threshold 3, strict).

### Knob E: affinity tie-break — UNDISCLOSED, low impact here but a real choice

`harness/score.py:55-64,77`. When several defects sit on the same lines, credit goes
to the one with the best type+content affinity, not the first listed. Sound design,
but it is an unstated rule that decides multi-defect snippets (04, 09, 11). Not shown
to flip a headline in this corpus; flagged so the next round pre-commits it.

## What survives the whole knob space (genuinely robust)

Swept across line-gap {0,1,2} x threshold {2,3} x stem {off,on} = 12 cells:

- **Claude-Gemini is the most decorrelated (lowest-phi) model pair: 12/12 cells.**
  Robust. This published claim holds.
- **Claude-Gemini errors are *strictly anti-correlated* (negative phi): 11/12 cells.**
  At gap 2 / threshold 3 / strict it is +0.079. So the weaker "lowest pair" claim is
  robust; the stronger "anti-correlated / negative in every variant" wording is true
  for the four variants reported but not for the full knob space. Minor overclaim.
- **Codex caught 0/4 performance defects: matcher-INDEPENDENT.** Verified by reading
  the reviews, not the scorer: Codex emits the `performance` type exactly once in all
  20 reviews (snippet 05, which has no performance defect) and names no perf issue on
  any of 01/08/11/15. This is the study's strongest result and it does not depend on
  any knob.
- **H1 payoff < 1.20x: 12/12 cells** (range 1.07x-1.16x). The pre-registered
  effect-size null is robust.

## Reproducibility hazard (not a forking path, but a provenance bug)

`runs/RESULTS.json` is git-tracked AND regenerated by `metrics.py`. The README lists
`SCORE_STEM=1 python3 harness/metrics.py` as a reproduce step; running it overwrites
the committed canonical (strict) results file with the lenient variant and dirties
the tree, and the file records no flag for which variant produced it. A reader
following the README as written ends with the non-canonical numbers in the canonical
file. Recommend: write the variant name into RESULTS.json (and/or emit the lenient
run to a separate path), or stop tracking the generated file.

## Pre-commitments the NEXT round must freeze before any new data

A future round (the divergence probes in `probes/PROTOCOL.md`, or a scaled corpus)
must, before collecting data, freeze:

1. **The matcher constants** A-E as named values in the pre-registration: stem on/off,
   line-gap, content threshold, affinity rule. Pick one canonical setting and commit
   it; report the others only as a declared sensitivity grid, never as a choice made
   after seeing which way it cuts.
2. **The answer-key completion rule.** "The human adjudicates candidates" is not a
   rule. Freeze the criterion (e.g. a candidate is credited iff >=2 independent raters
   flag it AND an external model confirms it real), and freeze it before the reviews
   are read, so no single decisive defect can be adjudicated toward a hypothesis.
3. **The primary-vs-sensitivity split.** Name ONE pre-registered primary scoring before
   data; everything else is explicitly secondary. The current study's honesty move
   ("report the sensitivity, claim nothing") is the right call given the knobs were not
   pre-frozen, but the next round should not need that escape hatch — it should have a
   primary that stands.
4. **The alignment/matching step for the probes.** `probes/PROTOCOL.md` step 5 says
   "match steps and classify" with no matching rule. That is the same unfrozen knob
   that bit this study; freeze it before the probe runs.
5. **A pre-declared n and stopping rule.** At n=30 every gap of interest is inside the
   scoring noise. Pre-register the corpus size that would move H2 out of noise, and do
   not read the correlation until that n is reached.
