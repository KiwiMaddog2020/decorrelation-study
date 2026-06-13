# Research agenda: decorrelation, new senses, and the limits of verifiability

**One line.** Decorrelation within a single medium depreciates as model capability
fills in; the durable engine against a plateau is acquiring new media and senses; the
human is the first and clearest new medium; and the program is mapping where
verification still needs an outside view, and watching that frontier move.

This is the through-line behind the decorrelation study and the work around it. The
study is the first data point; this document is the bet the study sits inside.

## The problem: honest measurement, not capability, is the bottleneck

A system that improves itself has to grade its own work, and a grader is blind to
exactly the mistakes it would make itself. So the binding constraint on safe
self-improvement is not how smart the system is, it is whether it can tell, honestly,
that an improvement is real. And the measuring instruments have their own blind spots:
in this study the answer key I wrote had a security hole an outside model had to
catch, and the scoring rule quietly tried to flip the result toward the answer I
wanted. You cannot improve what you cannot honestly measure, and measuring honestly is
harder than it looks.

## The mechanism: decorrelated checks, and why they depreciate

The escape from a checker's blind spot is a *different* checker, one whose errors do
not line up with the thing being checked. That is what an ensemble buys, what a frozen
pre-registration buys, and what a second model family buys. It is real, and it is the
mechanism behind every honest verification.

But it depreciates. Inside a single medium, code review for example, the models
converge as their jagged competence fills in. The valleys that made them decorrelated
get smoothed by capability. The decorrelation study already shows this: combining
three models beat the best single by only about 1.1x, and the "which pair is most
alike" question could not be resolved at all, because the three are *already*
converging. The within-medium well is running dry now, not someday.

## The escape: new media, not more of the same

When decorrelation runs out inside a medium, you do not get it back by adding a fourth
model that reviews the same code. You get it back by moving to a medium the models do
not yet occupy, a sense they structurally lack. Progress stops being "better at the
same thing" and becomes "a new thing to be good at."

The human's lived experience of *using a product* is the first clear example. A model
can predict, increasingly well, what a person will feel using something; it cannot have
the experience. The human is upstream of the model's competence in that medium,
generating the ground-truth signal the model only learns secondhand, so at the frontier
of genuinely new products the human is always a step ahead of the model modeling them.
There will be other media. The bet is that the supply of new senses is what keeps the
whole loop from flattening.

## The umbrella: verifiability with the right context

All of this is one program: *almost anything is verifiable with the right decorrelated
context.* The verification shadow is what a checker cannot see from inside; the right
context is the outside view that can. The frontier insight is that "the right context"
increasingly means the right *medium*, not just a different model. The research is
mapping where verifiability-with-context reaches its limit: what stays hard to verify
even with the right outside check, and how much signal it takes before a model can
stand in for a human's sense on everything except the genuinely new.

## What progress looks like

Each study probes one boundary of verifiability-with-context and watches the frontier
move:

- **Result 1 (done):** within a single medium (code review), model decorrelation is
  already thin, and the durable finding is type-specific blindness, not raw coverage.
  The decorrelation study.
- **Result 2 (designed):** across media, a human evaluating real product flows catches
  what no model does, because that medium is one models cannot enter. See
  `docs/FOLLOWUP_human_product_decorrelation.md`.
- **Further out:** which media still need a decorrelated (often human) check, and does
  that set shrink as models acquire new senses faster, or hold because the frontier of
  "new" keeps moving.

## What would falsify this

- If within-medium decorrelation does *not* thin as models improve, the depreciation
  claim is wrong, and ensembles stay valuable on their own.
- If models acquire new media (embodiment, real interaction, lived signal) faster than
  humans can supply the check, the human-as-first-new-medium advantage closes and the
  plateau argument loses its escape hatch.
- If a single medium never actually fills in, never reaches uniform competence, then
  there is no plateau to escape and the new-senses engine is unnecessary.

These are real ways to be wrong, written down on purpose. The point of the agenda is
not to be right yet. It is to say, in advance, what would change my mind.
