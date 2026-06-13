# Smoke test on snippet 001: what the pipeline taught us before we scaled

Date: 2026-06-13. One snippet, three model raters (Claude clean-room, Gemini CLI,
Codex CLI). Goal: prove the review-capture-score loop works end to end. It does,
for two of three raters, and it surfaced three issues that would have corrupted
the full study. A smoke test working as intended.

## Raw results on snippet 001 (planted: d1 SQL-injection, d2 dict-collision)

- **Claude:** flagged d1 (SQLi), d2 (dict collision), a restatement of d2 (dict
  cannot preserve order/ties), AND an unplanted real defect: the connection leaks
  if execute/fetchall raises (no try/finally).
- **Gemini:** flagged d1 (SQLi), d2 (dict collision), AND the same unplanted
  connection-leak defect.
- **Codex:** no output. Timed out at 150s under xhigh reasoning effort before
  emitting anything.

## Finding 1: ground truth was incomplete (the planter's verification shadow)

Two independent model families, from different training, both flagged a real
defect (the unclosed connection on exception) that I planted by accident and never
recorded in the answer key. A naive scorer would have counted both raters'
genuine catch as a false positive and penalized them for being right.

This is the doer-never-rates-its-own-work problem landing on the experiment's own
design: I wrote the code and I wrote the answer key, so I am blind to the defects
I introduced without meaning to. The answer key cannot be trusted to be complete
just because its author says so. Independent review revealed the hole, exactly as
the thesis predicts for any bounded checker.

Fix: every planted snippet gets an independent completeness audit (Gemini, the
most decorrelated model from the planter) that hunts for ALL defects, planted and
unintended, before any review runs. And the scoring rule changes: a flag that
matches no recorded defect is "unscored / candidate," adjudicated by the human,
not an automatic false positive. Logged as a pre-registration amendment, dated,
before the 20-snippet data.

## Finding 2: the defects were too obvious to show decorrelation

Both working raters agreed completely: both caught all three real defects,
identical. That is high correlation, not decorrelation, and it is the expected
result on obvious defects. Models do not have divergent blind spots on a textbook
SQL injection. The decorrelation the study is built to measure lives in SUBTLE,
type-specific defects, the ones one family's training makes it see and another's
makes it miss.

Fix: the corpus must be calibrated for difficulty. Obvious defects are useless as
signal. The 20 snippets need subtle, type-varied defects pitched in the band where
families actually diverge, or the study measures agreement on easy things and
concludes nothing.

## Finding 3: the Codex harness needs work

Codex exec runs at xhigh reasoning and is slow; 150s was not enough and it
produced nothing. Its stdout also carries a transcript wrapper that the parser
must strip. Fix: raise the timeout substantially (the orchestrator uses up to 30
min for real Codex work), capture stdout robustly, and parse the transcript for
the defect lines.

## Net

The loop works (Claude + Gemini, blind, clean-room, captured, scorable). Before
scaling, three things change: an independent completeness audit of every snippet,
a difficulty-calibrated defect set, and a fixed Codex harness. None is a blocker;
each is the difference between a real measurement and a flattering fake one.
