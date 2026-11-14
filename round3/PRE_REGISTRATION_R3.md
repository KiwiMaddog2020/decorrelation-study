# Round 3 pre-registration: do Claude tiers cover each other's blind spots?

Date: 2026-11-14. Written before any round 3 model call. No round 3
review existed when this file was written.

## Question

Two reviews are better than one. Is it better if the second review comes from a
different Claude tier, or is a second independent look from the same model just
as good?

## Reviewers

Four tiers, each reviewing all 20 snippets twice, in independent fresh sessions
(review 1 and review 2):

| tier | requested model id | raters |
|---|---|---|
| haiku | claude-haiku-5-5 | haiku1, haiku2 |
| sonnet | claude-sonnet-5-5 | sonnet1, sonnet2 |
| opus | claude-opus-5-5 | opus1, opus2 |
| fable | claude-fable-5-2 | fable1, fable2 |

The model that actually answered each call is recorded where the platform reports
it. The July round 1 Claude review (`runs/full/NN.claude.txt`, most likely Opus
4.8, not verified) is copied in unchanged as rater `opus48_then`, for a then
versus now row. It is not part of the primary comparison.

## Materials

The same 20 snippets (16 with 30 planted defects, 4 clean controls) and the same
answer key as rounds 1 and 2, unchanged. The per-snippet instructions are
`protocol/review_prompt.txt` verbatim.

## Deviation from the original procedure

Round 1 sent one snippet per call. Round 3 sends five snippets per call to keep
the run small: 4 calls per review, 8 per tier, 32 in all. The batches are a
seeded random partition (seed 20261114), different for review 1 and review 2,
and the same for every tier. A short wrapper tells the reviewer the snippets are
independent, that line numbers restart for each one, to answer from the text
only, and to reply with one `=== SNIPPET <ID> ===` section per snippet.
Batching may change what a reviewer notices; this affects every tier the same
way, but it makes the then row a mix of a model change and a format change.

## Metrics

Computed by `round3/analyze.py` with the existing scorer (`harness/score.py`).
For each rater: defects caught of 30, false positives on the 4 clean snippets,
candidate flags on defective snippets, and catches per defect type.

For pairs of reviews:

- Same-tier pairs: tierX review 1 with tierX review 2 (4 pairs).
- Cross-tier pairs: tierX review a with tierY review b, every tier pair and every
  review choice (24 pairs).
- For each pair: union caught, and gain = union minus the better single review
  in the pair. Mean union and mean gain for each group.
- Phi correlation of catch vectors, mean within tier versus mean across tiers.
- Union of all four tiers with one review each, for every choice of review,
  against the best single review in that set.
- Defects missed by every round 3 review, and the then row.

## Primary comparison and decision rule

D = mean cross-tier pair gain minus mean same-tier pair gain, in defects, in the
primary scoring mode. Uncertainty: a seeded bootstrap (10,000 resamples, seed
20261114) over the 30 defects, 95% percentile interval.

- **Tiers cover each other** if D is at least 1.0 defect and the interval's lower
  end is above 0.
- **A second look is just as good** if D is below 1.0 defect and the interval's
  upper end is below 2.0.
- Otherwise: **inconclusive at this sample size**.

Why 1.0 defect: it is the smallest difference that is a whole extra catch per
pair, about 3 percentage points of the 30 defects. Round 1 found that three
different model families together beat the best single model by 3 defects, so a
tier effect much smaller than 1 defect would not matter in practice. The upper
bound of 2.0 stops a noisy, wide interval from being read as "no difference".

## Scoring modes

1. **headers (primary):** header rows, table separator rows, and rows that have
   neither one of the eight allowed types nor a line number are ignored. A row
   with an off-list type that still points at a line is kept as a real flag.
   This fixes a parsing bug (an echoed header row counted as a false positive)
   without changing matching.
2. **original:** the pre-registered round 1 scorer, unchanged, for continuity.
3. **headers plus described:** a flag near a defect only counts when its type or
   wording also fits the defect. A sensitivity check on generous line matching.

If the outcome differs between modes, all three are reported and the primary
mode decides.

## Known limits

- The answer key has been public on GitHub since June 2026, so newer models may
  have seen it during training. This would raise catch rates for all tiers and
  could shrink differences between them.
- One model family only. Nothing here speaks to other families.
- n = 30 defects and 2 reviews per tier. Pairs share members and are not
  independent. Run to run variation is only sampled twice per tier.
- The session that orchestrates the run has seen the answer key. To keep that
  out of the data, prompts are built by script (`round3/build_prompts.py`) and
  all scoring is by script (`round3/analyze.py`). Helper sessions that run the
  reviews are told not to use tools, and their transcripts are audited for tool
  use; any review with tool use is reported and rerun in a fresh session.
- Model ids are as requested; the served model may differ and is recorded when
  known.

## Amendment 1 (2026-11-14, before any scored data)

The first three calls (one tier, three batches of review 1) showed a harness
problem, not a model result. Helper sessions read the prompt from a file, and
the file viewer numbers lines from the top of the file, so reviewers reported
locations such as "line 143" for a snippet that was pasted partway down the
prompt. The scorer matches on line numbers, so this would have depressed every
score for a reason unrelated to review quality.

Fix: each snippet now sits alone in its own file, byte for byte as in the
corpus, and the prompt lists the five files. Line 1 of the file is line 1 of the
snippet. Everything else is unchanged: same batches, same seed, same
instructions, same reply format.

The three pilot answers were set aside unscored (kept under `round3/pilot/` for
the record) and those calls are rerun in fresh sessions with the fixed prompts.
No answer was scored before this amendment. One consequence to keep in mind for
the then row: in round 1 the reviewer counted lines itself, while here the file
viewer shows them, so line locations may be more exact now than then.
