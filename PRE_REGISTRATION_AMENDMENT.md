# Pre-registration amendment 1

Date: 2026-06-13. Logged BEFORE the 20-snippet confirmatory data is collected.

The smoke test on snippet 001 (runs/smoke/SMOKE_TEST_001.md) exposed three flaws
in the procedure. This amendment fixes the **procedure and data quality only**.
The hypotheses (H1-H5) are unchanged; no prediction has been altered to fit any
result, and no confirmatory data exists yet. Amending transparently before data,
never after, is the discipline.

## Change 1: an unmatched flag is a CANDIDATE, not an automatic false positive

The smoke test proved the answer key can be incomplete: two independent models
caught a real defect the planter never recorded. Under the original scoring, that
genuine catch would have counted as a false positive and penalized a correct
reviewer. So: a flag that matches no recorded defect is logged as a *candidate*
and adjudicated by the human (Kevin). If the human confirms it is a real defect,
it is added to the ground truth and credited as a catch; only flags the human
judges spurious count as false positives.

## Change 2: an independent completeness audit of every snippet

Because the planter is structurally blind to the defects they introduce by
accident, every snippet is audited before any review by Gemini (the most
decorrelated model from the Claude planter), tasked to find ALL defects, planted
and unintended. The human reconciles the audit with the planted set, and the
reconciled list is the ground truth of record. The planter's word alone is never
the answer key.

## Change 3: difficulty calibration

The smoke-test defects were obvious, and both working raters agreed completely,
which is correlation, not the decorrelation the study measures. Obvious defects
carry no signal. The 20-snippet corpus is calibrated toward subtle, type-specific
defects in the band where model families plausibly diverge, balanced across the
seven types, with some clean snippets to measure false-positive rates. Difficulty
is a logged property of each snippet so the analysis can report results by
difficulty band.

## Unchanged

Hypotheses H1-H5, the metric definitions, the reviewer set, the blind independent
protocol, the n=1-human limitation, and the decision rule all stand exactly as
pre-registered.
