# Divergence probes: measuring the verification residue with a lived human pass

A divergence probe is the cheapest experiment in the
[research agenda](../docs/RESEARCH_AGENDA.md) and the first bridge in
[VERIFICATION_RESIDUE.md](../docs/VERIFICATION_RESIDUE.md). It measures one thing:
where a model's *prediction* of how a product feels to use comes apart from how it
*actually* feels to a human using it. Each place they come apart is a residue data
point, a friction that lives in the experience rather than in anything a model can read.

## The shape (one probe)

Two independent, blind passes over the same product flow, each frozen before either
sees the other, then aligned and scored. This mirrors the decorrelation study:
independent blind reviews, then alignment. The decorrelation here is between
*predicted* experience and *lived* experience.

1. **Pick a flow.** One bounded task in a real product, roughly 5 to 15 steps. A
   first-time-user task is best, because that is where lived friction is richest.
2. **Pre-register.** Before either pass, freeze the flow definition and the hypotheses
   to git (the timestamp is the honesty anchor). What do you expect the divergences to
   look like, and what would make you wrong.
3. **Model pass (blind).** A model predicts, step by step, where a first-time user
   feels friction, where they get stuck, and the valence (delight / neutral / friction).
   It sees no human reaction. Frozen to `model_pass.md`. For real rigor use a model not
   otherwise in the conversation; for a first probe any frontier model is fine, note the
   caveat.
4. **Human pass (blind).** You run the flow for real and log, step by step, what you
   actually felt and where you stuck. You do **not** read the model pass first. Frozen
   to `human_pass.md`. You are the sandwiching subject: a real user with ground truth,
   which is exactly the rig the method needs.
5. **Align and score.** Match steps and classify each (below). The misses and flips are
   the residue.

## Scoring classes (per step)

- **agree-friction**: both flagged friction here.
- **agree-smooth**: both said it is fine.
- **model false-alarm**: model predicted friction, you felt none. (Models over-weight
  documented complexity.)
- **model miss**: you hit friction the model did not predict. *This is the residue.*
- **valence flip**: model predicted delight or neutral, you felt friction, or the
  reverse.

Then split every **model miss** into:

- **visible-in-UI**: the friction was on screen; the model should have caught it. (Not
  residue, just a model error.)
- **lived-knowledge**: the friction comes from having used it before, state that is not
  in the product's text. *This is the structural residue.*

The headline number for one probe: lived-knowledge misses over total friction points.
Across probes, that number and what it clusters on is the dataset the residue-map note
leads with.

## Why this is honest

The model pass is frozen before the human pass, and both before alignment, so neither
can be retrofitted to the other. It is the same clean-room discipline that ran the
decorrelation study, applied to a sample of one lived human, which is the whole point:
one lived human is the instrument a model structurally lacks.

## Scaling up

n=1 (you) is a real probe, not a toy, because the claim is about a *kind* of friction,
not a population. To strengthen: more flows (breadth), more humans per flow (does the
lived-knowledge miss replicate across people), and a clean external model for the model
pass (true decorrelation). A handful of flows is enough to write the residue map with
evidence instead of assertion.
