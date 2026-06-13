# decorrelation-study

A small, pre-registered controlled study testing one question: when reviewers
with different "training" (Claude, Codex, Gemini, and one human) each review the
same code blind, do their different blind spots produce complementary coverage no
single reviewer matches, and is the human the most decorrelated reviewer?

It is the measured follow-up to a practitioner observation: in a real multi-model
review system, half the defects in one batch were caught by a single model
family, and the weakest model made the most unique catches. That was n=12, one
run. This study is the attempt to measure it honestly.

## Status

Pilot, pre-registered. **Read [`PRE_REGISTRATION.md`](PRE_REGISTRATION.md) first**:
the hypotheses, metrics, scoring rules, sample size, and known limitations are
fixed there before any data is collected, so no result can be selected after the
fact to flatter a conclusion.

## Layout

- `PRE_REGISTRATION.md` — the honesty anchor (frozen before data).
- `corpus/snippets/NNN.py` — the code each reviewer sees. Contains planted defects,
  no markers.
- `corpus/truth/NNN.json` — the answer key (planted defects with exact location,
  type, canonical description). Never shown to any reviewer.
- `protocol/review_prompt.txt` — the identical blind-review prompt every reviewer
  receives.
- `harness/` — (to come) runs each reviewer over each snippet, captures structured
  flags, scores against ground truth, computes the metrics.

## The discipline

Planted defects are audited by Gemini for fairness before any review runs. Claude
reviewers run clean-room (no planting context). A clean null result is as
publishable as a clean positive; the study is built so it can fail honestly.
