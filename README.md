# Decorrelation study: do AI code reviewers have complementary blind spots?

A small, pre-registered experiment. Three AI models (Claude, Codex, Gemini) and
one human review the same 20 code snippets with planted defects, blind, and we ask
whether their blind spots line up or cover for each other.

It is the measured follow-up to a practitioner observation: in a real multi-model
review system, half the defects in one batch were caught by a single model family,
and the *weakest* model made the most unique catches. That was n=12, one run. This
study is the attempt to measure it honestly. The question matters beyond code
review: any system that improves itself has to grade its own work, and a grader is
blind to the mistakes it would make itself. The escape is a checker whose errors
are not correlated with the thing being checked.

**Read the write-up:** [Do AI code reviewers have complementary blind spots?](https://kiwimaddog2020.github.io/decorrelation-study/)

**The research program it sits inside:** [`docs/RESEARCH_AGENDA.md`](docs/RESEARCH_AGENDA.md) — decorrelation depreciates within a medium; the durable engine is acquiring new senses, and the human is the first new medium.

## What's here

- [`PRE_REGISTRATION.md`](PRE_REGISTRATION.md) — hypotheses, metrics, scoring rules,
  and limitations, frozen in git before any review was collected. The honesty anchor.
- [`PRE_REGISTRATION_AMENDMENT.md`](PRE_REGISTRATION_AMENDMENT.md) — procedure fixes
  logged transparently, before data, after a smoke test.
- `corpus/` — 20 hand-written Python snippets (`snippets/`) with their exact ground
  truth (`truth/`). 16 defective + 4 clean controls, 30 planted defects across seven
  types. [`corpus/MANIFEST.md`](corpus/MANIFEST.md) describes the set.
- `runs/gemini_audit/` — the blind external audit that found defects in my own
  "clean" controls, and the [reconciliation](runs/gemini_audit/RECONCILIATION.md).
- `runs/full/` — every reviewer's blind review, one file per (snippet, rater).
- `harness/` — the scoring code (`score.py`), metrics (`metrics.py`), and the
  generation, audit, and review runners.
- [`runs/RESULTS_model_only.md`](runs/RESULTS_model_only.md) — the current results.

## Headline findings (model-only; H3 was the wrong test, see below)

- **Combining models helps, but modestly.** The three together caught all 30
  defects; the best single model caught 27. A real but small gain (about 1.1x),
  below the threshold I pre-registered as interesting.
- **The correlation prediction could not be resolved.** Whether the most-similar
  pair of models is Claude-Codex or Gemini-Codex flips on a single scoring choice,
  with gaps that are noise at n=30. So it is reported as unresolved, not confirmed.
  The scoring instrument has a blind spot too, and it pointed at the answer I wanted.
- **What held up across every analysis:** Claude and Gemini are the most
  decorrelated pair (their errors are anti-correlated), and **Codex caught 0/4
  performance defects** while Gemini caught all four. Models are blind to different
  *kinds* of bug. That is the durable result.

## Reproduce

```bash
python3 harness/align_report.py          # every cited defect line is live code
python3 harness/metrics.py               # strict (pre-registered) scoring
SCORE_STEM=1 python3 harness/metrics.py  # the lenient sensitivity variant
```

The audit and review runners call the Gemini and Codex CLIs; the corpus, ground
truth, and recorded reviews are all in the repo, so the scoring and metrics
reproduce offline.

## The discipline

Planted defects were audited by Gemini for fairness and completeness before any
review ran. Model reviewers ran clean-room (no planting context, no answer key).
A clean null result is as publishable as a clean positive; the study is built so it
can fail honestly, and where it could not support a prediction, it says so.

## Status

H3, the human-decorrelation centerpiece, was posed as code review, which turned out
to measure code-reading skill rather than decorrelation for a non-coding operator.
Rather than fake it, the study reframes H3 as a measurement lesson and a better
experiment, where a human and the models evaluate real product flows, designed in
[`docs/FOLLOWUP_human_product_decorrelation.md`](docs/FOLLOWUP_human_product_decorrelation.md).
The model-only results (H1/H2/H5) stand as the pilot.
