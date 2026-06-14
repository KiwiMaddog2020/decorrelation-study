# Probe 01 score (SEALED)

**Do not open until your human pass is logged.** This sheet contains the three model
predictions. `human_pass.md` is the only file you open before or during your run.

Three independent clean-room model passes (Claude, Gemini, Codex) versus one lived human
pass (Kevin). Valence shorthand: F = friction, N = neutral, D = delight. Fill the Human
column and the class columns after your run.

| Step | Claude | Gemini | Codex | Human | Per-model class | Consensus miss? |
|---|---|---|---|---|---|---|
| 1 Find tool | F | N | F | ___ | ___ | ___ |
| 2 Open Seed Map | N | D | N | ___ | ___ | ___ |
| 3 Platform/version | F | F | F | ___ | ___ | ___ |
| 4 Find seed | F | F | F | ___ | ___ | ___ |
| 5 Find villages | F | D | N | ___ | ___ | ___ |
| 6 Read coords | N | N | D | ___ | ___ | ___ |
| 7 Navigate | F | F | F | ___ | ___ | ___ |
| off-spine | (none) | (none) | (none) | ___ | ___ | ___ |

Predicted worst step: Claude 4, Gemini 3, Codex 4.

Classes (per model, per step): agree-friction / agree-smooth / model-false-alarm /
model-miss / valence-flip. Split each model-miss: visible-in-UI vs lived-knowledge.
**Consensus miss** = all three models missed a friction you actually hit (the strongest
residue signal).

## The H-C test (the one that matters)

All three models flagged step 3 as friction, but framed it as a *visible act*: notice
the toggle, match the version, pick from the list. None named the **version-lag**
residue: the map being subtly wrong even when the version is set correctly. The H-C
question: does your real friction at step 3 (or off-spine) come from version lag /
stale-data wrongness that none of the three named? If yes, it is a consensus
lived-knowledge miss and H-C is confirmed strongly. If your friction is only "I had to
notice the toggle," the models caught it and H-C is weaker.

## Tally

- consensus misses (all three): ___ (visible-in-UI: ___, lived-knowledge: ___)
- per-model misses: Claude ___, Gemini ___, Codex ___
- model false-alarms: Claude ___, Gemini ___, Codex ___
- valence flips: ___
- **residue number (consensus lived-knowledge misses / total friction points): ___**

## Inter-model note (free side-result)

Where the three models disagree with each other (step 1, 2, 5, 6 here) is its own
decorrelation data: the models are not even converged on predicting experience. Worth a
line in the residue map.

## Hypotheses outcome

- H-A (false alarm exists): ___
- H-B (miss exists): ___
- H-C (consensus miss on lived-knowledge, especially version-lag): ___

## One-line finding

___
