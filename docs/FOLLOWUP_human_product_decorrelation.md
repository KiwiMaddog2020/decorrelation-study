# Follow-up design: measuring human decorrelation where it actually lives

This study's H3 asked whether a human is the most decorrelated reviewer of all. It
posed that as code review, which was the wrong test: it measures whether a person
can read source for subtle bugs (a programming skill), not whether their judgment is
*different* from a model's. A non-coder comes out looking weak, and "not a
programmer" gets silently relabeled "not decorrelated." Those are not the same.

The fix is a better question, not a better human. A person's judgment is genuinely
uncorrelated with a model's not when reading the code, but when **using the thing
the code becomes**. A human knows what it feels like to be on the other end of an
interface: where it is confusing, where it fights how you want to move, what is
missing that no spec lists. A model reading source or a screenshot has no lived
access to that. So the human's decorrelated value lives in product and UX, a
different *modality*, and a corpus of code defects is blind to it. This is the
experiment that would test the real hypothesis.

## Hypothesis (to be pre-registered before any data)

- **H-P1 (modality coverage).** On a set of real product tasks, the human catches
  experience problems that no model catches, at a rate strictly higher than any
  model catches problems the human misses. The complementary set is asymmetric
  toward the human.
- **H-P2 (category split).** The human and the models own different *categories* of
  problem. Models own the checkable ones (broken states, contract/spec mismatches,
  accessibility rules, dead ends). The human owns the felt ones (confusion,
  friction, wrong-for-the-goal, "this is not how I would expect it to work").
- **H-P3 (decorrelation is real, not just skill).** The human's catches are not a
  subset of any model's; the error vectors are genuinely decorrelated, not the human
  being uniformly worse or uniformly better.

## Design

- **Corpus.** 15-25 real product *flows or tasks* (sign-up, an export, a settings
  change, a first-run), each with a stated user goal. Some carry planted or known
  UX problems; some are clean. Difficulty calibrated toward the *subtle* (a flow
  that works but feels wrong), not the broken (a 500 error any tool catches).
- **The human rater** actually performs the task in the live product and reports
  every problem they hit, in their own words, against the goal. This is the modality
  the human is competent in and the models are not.
- **The model raters** evaluate the same flow from what a model can actually be
  given: a screen recording or screenshot sequence, the DOM/spec, and the same goal
  statement. They report problems in the same format. They are blind to the human's
  report and to each other.
- **Scoring.** Each reported problem is matched to a reconciled ground-truth list of
  real issues (built the same disciplined way: planted + an independent audit +
  human adjudication of candidates, because the answer key will have a verification
  shadow here too). Per rater: caught / missed over the issue set, plus
  false-positives (problems reported that are not real). Then the same metrics:
  pairwise correlation, coverage payoff, and the per-category split that is the
  point.

## Why this is the honest version

The code study put the human in a seat where the human is weak, so it could only
measure weakness. This puts each rater in the seat where they are strong and asks
whether their strengths *differ*. That is what "decorrelated" was always supposed to
mean: not who is better, but who is unlike.

## Hard parts (declare up front)

1. **Asymmetric access.** The human *uses*; the models *describe* from a recording.
   That is not a flaw to hide, it is the finding: the lived channel is the human's
   decorrelated sense. But it must be stated, and the models given the fairest
   non-lived input possible (full recording + DOM + goal), so a model loss is about
   modality, not starvation.
2. **Defining a UX "defect."** Felt problems are softer than a null-pointer. The
   ground truth needs a written rubric and human adjudication, and the rubric is
   frozen before data.
3. **n = 1 human, again.** Same limitation as before; any result speaks to this
   operator, not to humans in general. A positive directional signal justifies more
   human raters; it does not get rescued by post-hoc slicing.
4. **The verification shadow does not go away.** Whoever builds the issue list is
   blind to the issues they introduced or missed. An independent audit (a model, a
   second human) of the ground truth is mandatory, exactly as it was here, and is the
   most likely place this design fails first.

## Connection to the thesis

This is the same argument the code study makes, pushed one modality further. A
self-improving system grades its own work and is blind to its own kind of mistake.
The escape is a *different* checker. "Different" can be a different model family, a
different frozen rule, or a human placed in the one channel a model structurally
lacks: the lived experience of being the user. That last one is not a weaker version
of code review. It is the thing models cannot do at all, which is exactly why it is
worth measuring.
