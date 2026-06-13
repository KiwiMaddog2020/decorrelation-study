# Pre-registration: do independent rater families catch complementary defects?

**Status: PRE-REGISTERED. Written before any review data is collected.**
Date frozen: 2026-06-13. Author: Kevin Madson. Analysis collaborator: Claude (Opus 4.8).

This file is the honesty anchor. The hypotheses, the metrics, the scoring rules,
and the sample size are fixed here, in advance, so that no result can be selected
after the fact to flatter a conclusion. If the data contradicts a prediction
below, that contradiction ships. The same anti-inflation discipline the rest of
this work argues for, pointed at this study.

## The question

When several reviewers with different "training" each look at the same code,
does the diversity of their blind spots produce complementary coverage that no
single reviewer matches? And is a human the most decorrelated reviewer of all,
not because they are the strongest, but because evolution and gradient descent
are the two most different training regimes available?

Reviewer families in this study: **Claude, Codex (OpenAI), Gemini (Google), and
one human (Kevin).** Each is treated as a "trained estimator" with its own error
distribution.

## Hypotheses (fixed, falsifiable)

Confirmatory:
- **H1 (coverage payoff).** The union of all four reviewers catches strictly more
  true defects than the single best reviewer. Pre-registered effect size of
  interest: union catches at least 1.2x the best single reviewer's count.
- **H2 (correlation structure).** Error correlation between the two most similar
  models is the highest pairwise model-model correlation. Specifically, predicted
  ordering: corr(Claude, Codex) > corr(Claude, Gemini) and > corr(Codex, Gemini).
  (Direction predicted; magnitude not.)
- **H3 (human independence).** The human's error vector is less correlated with
  every model than any model pair is with each other. Predicted:
  max over models of corr(human, model) < min model-model pairwise correlation.

Exploratory (declared exploratory in advance because the pilot n is small and
these are likely underpowered):
- **H4 (unanimity is a blind-spot signal).** When all three models agree on a
  defect call, they are wrong more often than when they split:
  P(all-models wrong | unanimous) > P(wrong | split). Likely few unanimous cases
  at n=20; reported as exploratory regardless of outcome.
- **H5 (type-specific blindness).** Per-defect-type catch rates differ across
  families (e.g., one family systematically owns security, another logic). The
  per-type breakdown is the qualitative payoff even if H1-H3 are weak.

## Design

- **Corpus.** ~20 snippets of real, realistic code. Each snippet carries 0 to N
  *planted* defects with exact, pre-recorded ground truth (location, type,
  canonical description, severity). Defects are balanced across seven types:
  logic, security, concurrency, boundary/off-by-one, api-misuse, performance,
  spec-violation. Some snippets are clean (zero defects) to measure false-positive
  rates honestly.
- **Blind independent review.** Each reviewer sees only the snippet and an
  identical review prompt (protocol/review_prompt.txt). No reviewer sees any
  other reviewer's output. Models are invoked clean-room (fresh context, no
  conversation history). The human reviews a random subset (~12 of the 20).
- **Scoring.** A reviewer "catches" a planted defect if they identify its
  location AND name the actual problem (not merely flag the region). Matching a
  free-text flag to a planted defect is mechanical (location overlap + type
  agreement); the human adjudicates only genuinely ambiguous matches, and every
  adjudication is logged. A flag that matches no planted defect is a false
  positive. From this, each reviewer gets a binary caught/missed vector over all
  defect instances, plus a false-positive count.
- **Metrics.**
  - Pairwise error correlation: phi / Matthews coefficient over the caught/missed
    vectors, all six reviewer pairs.
  - Coverage payoff: |defects caught by at least one reviewer| / |defects caught
    by the best single reviewer|.
  - Unanimity calibration: error rate when all models agree vs when they split.
  - Per-type catch rate by family.

## Known limitations (declared up front, not discovered later)

1. **n = 1 human.** Any human result speaks to *this operator*, never to humans in
   general. The human family has a sample size of one person.
2. **The planter is also a rater family.** Claude plants the defects and Claude is
   a reviewer. Mitigation: clean-room Claude reviewers never see the planting
   context, AND the full planted set is audited by Gemini (the most decorrelated
   model from Claude) for realism, fairness, and unambiguous typing before any
   review runs; unfair or ambiguous items are fixed or dropped. The residual risk
   (Claude unconsciously planting Claude-friendly bugs) is real and is reported,
   not hidden.
3. **Planted is not wild.** Injected defects may be unrepresentative of defects
   found in the wild. The host code is real to reduce this; the defects are not.
4. **Small n, exploratory tails.** At n=20 snippets, H4 and H5 are exploratory and
   may be underpowered. This is a pilot; a positive directional signal justifies
   scaling, a null does not get rescued by post-hoc slicing.
5. **Possible host-code familiarity.** Models may recognize the host open-source
   code from training. Contamination of the *defects* is low (planted), but
   familiarity with the surrounding code is possible and noted.

## Decision rule

This is a pilot. If H1 and H2 hold directionally, scale the corpus and, optionally,
add human raters beyond n=1. If they do not, that null result is the finding and
ships as such. No outcome here is failure; a clean null is as publishable as a
clean positive, and a system that can only report success is the exact thing this
study exists to argue against.
