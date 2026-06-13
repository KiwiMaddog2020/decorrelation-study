# Results (model-only; human family pending)

60 clean-room model reviews (Claude, Gemini, Codex x 20 snippets) scored against
the reconciled ground truth. The human family (Kevin) is not yet in, so H3 is
open. Canonical numbers use the **pre-registered strict matcher**; the lenient
(stemmed) matcher is a sensitivity variant (`SCORE_STEM=1`). Machine-readable
copy in `runs/RESULTS.json`. **Pre-registered: the contradictions and the
non-results below ship as findings.**

Ground truth: **30 planted defects** (29 + 11-d5 `minconn>maxconn`, added during
reconciliation because Claude and Codex independently flagged it), 4 clean controls.

## Rater performance (strict matcher, 30 defects)

| rater  | caught | false positives | operating point |
|--------|--------|-----------------|-----------------|
| gemini | 27/30  | 3               | high recall     |
| claude | 23/30  | 1               | balanced        |
| codex  | 21/30  | 0               | high precision  |

Three genuinely different operating points: Gemini sweeps widest (and pays in
false positives), Codex is the most conservative (zero FPs on the clean
controls), Claude sits between.

## H1 coverage payoff: directional YES, effect-size NO (robust)

Union catches **30/30**; best single (Gemini) catches 27. The ensemble strictly
beats the best single reviewer, but the ratio is **1.11x** (strict) / 1.07x
(lenient), under the pre-registered 1.20x bar in every variant. Combining helps,
modestly. The pre-registered effect size was not met; that ships.

## H2 correlation structure: NOT ROBUSTLY RESOLVED (the key methodological finding)

H2 predicted corr(Claude, Codex) is the highest model-model pair. The verdict
**flips on a single adjudication call**:

| variant | corr(claude,codex) | corr(gemini,codex) | corr(claude,gemini) | H2 |
|---------|--------------------|--------------------|---------------------|----|
| 29 defects, strict  | +0.318 | **+0.406** | -0.154 | refuted |
| 30 defects, strict  | **+0.327** | +0.267 | -0.184 | holds |
| 30 defects, lenient | **+0.441** | +0.169 | -0.147 | holds |

The phi gaps between the top two pairs are 0.06-0.09 -- pure sampling noise at
n=30. The ordering changes depending on whether one terse rater catch is credited
(the matcher's stemming) and whether one multi-rater candidate is added to the
answer key. **So we do not claim H2 confirmed or refuted.** The honest result is
that the confirmatory correlation ordering is within the noise of the scoring
rule. This is the anti-inflation point the study exists to make, turned on the
study's own instrument: the matcher has a verification shadow too.

## What IS robust across every variant

- **Claude and Gemini are the most decorrelated model pair** -- their error
  vectors are *anti-correlated* (negative phi in all four variants). Where one
  misses, the other tends to catch.
- **Codex catches 0/4 performance defects** (verified by reading its reviews of
  01, 08, 11, 15: it flags the correctness/security/logic issue every time and
  never the performance one). Gemini catches 4/4. Claude is weakest on boundary.
  Families genuinely own and miss different defect *types* [H5]. This is the
  durable, matcher-independent finding.

## Per-type catch rate (strict, 30 defects) [H5]

| type           | n | claude | gemini | codex |
|----------------|---|--------|--------|-------|
| api-misuse     | 4 | 3      | 3      | 3     |
| boundary       | 5 | 3      | 4      | 4     |
| concurrency    | 3 | 3      | 3      | 3     |
| logic          | 6 | 5      | 5      | 5     |
| performance    | 4 | 2      | **4**  | **0** |
| security       | 5 | 4      | 5      | 4     |
| spec-violation | 3 | 3      | 3      | 2     |

## Honest headline

The big coverage intuition got a *modest* yes (H1). The specific correlation
prediction (H2) is *unresolvable at this n* -- it flips with the scoring rule, so
we report the sensitivity instead of a verdict. The durable, matcher-independent
results are type-specific blindness (Codex blind to performance) and that the
most decorrelated model pair is Claude-Gemini. The centerpiece, whether the human
is the most decorrelated reviewer of all (H3), is still open and needs the human
reviews. A pre-registered study that refuses to claim a result its instrument
cannot robustly support is the exact discipline this work argues for.
