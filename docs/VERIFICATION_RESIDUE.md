# The verification residue: where human value concentrates as the verifiable set expands

**One line.** Verifying a solution is often easier than producing one, so model
capability is racing to "verify everything." But it races toward a residue that
structurally resists verification: domains whose ground truth is a lived human
reaction. The marginal value of a human migrates to that residue. The optimistic
dual, "almost anything is verifiable with the right context," is the same claim seen
from the other side: the residue shrinks exactly as far as you can manufacture a
decorrelated outside check for the experiential signal, and not one step further on
its own.

This note sharpens point 2 of the [research agenda](RESEARCH_AGENDA.md) (the
"verifiability with the right context" umbrella) into the field's own vocabulary, and
lists where the gap can already be bridged today.

## The asymmetry the field is built on

A lot of recent capability rides on a simple asymmetry: for many tasks, checking an
answer is cheaper than generating it (the generation-verification gap, sometimes
called a verifier's law: progress on a task scales with how cleanly you can verify
it). Reinforcement learning from verifiable rewards (RLVR) is the engine. Where a
task has a checkable answer, you can reward the model against the checker and let it
climb. The recent reasoning gains in math and code are the clearest example.

## What the verifiable interior already contains

The interior is everything with a clean checker: arithmetic and proofs, code that
passes tests, formally specifiable outputs. The frontier has split the checker too:
outcome reward models grade the final answer, process reward models grade each step
(the "verify the steps, not just the answer" line of work). The interior is being
eaten fast, and the fact that it is verifiable is *why* it is being eaten fast.

## The residue that resists

When you push RLVR outward, it stalls at a boundary. On the far side sit the domains
whose ground truth is not a checkable fact but a reaction:

- whether a product flow feels good to use,
- whether a piece of writing lands,
- whether a research direction is worth taking before the results are in,
- taste, strategy under genuine novelty, the felt quality of an interaction.

These resist for a structural reason, not a temporary one. The ground truth is a lived
human reaction that no label captures cleanly, so the only stand-in is a judge model,
and a judge inherits two problems at once: it shares the doer's blind spots (a checker
is blind to the mistakes it would make itself), and it carries its own documented
judging biases (preferring its own outputs, longer answers, the first option it sees).
You cannot RLVR your way across a boundary where the reward signal itself is the thing
you do not have.

## The reframe that matters

The residue is not a shrinking nuisance to be cleaned up later. It is where durable
human value concentrates. As the verifiable interior gets eaten, the marginal worth of
a human does not fall evenly, it migrates to the boundary. "Verifiable with the right
context" is precise here: the residue shrinks exactly as far as you can build a
decorrelated outside check for the experiential signal, and for genuinely new products
that outside check is, for now, a lived human. The human is upstream of the judge
model's competence in that medium, generating the reaction the model only learns
secondhand.

## The research question

How far does "verifiable with the right context" push into the residue before it needs
a real lived human, and does that limit move as judge models improve? Put sharply: for
experiential quality on genuinely new products, can a decorrelated set of checks (a
different model, a rule, a frozen rubric) ever stand in for the lived reaction, or does
the residue have an irreducible core that always needs a human in the loop? The answer
is the whole bet.

## Where the gap can already be bridged (value, now)

These are application directions that route through the lived-interface edge and the
honest-measurement discipline, not through model implementation. Ranked by how little
setup they need.

1. **Divergence probes (cheapest, runnable this week).** A non-expert human with
   access to frontier models and real products is already a natural test rig. Pick one
   real product flow. Before using it, write down what a strong model predicts a person
   will feel and where they will get stuck. Then actually use it and record where
   reality diverges from the prediction. Each divergence is a residue data point: a
   place the model's prediction of experience came apart from the experience. Cost is
   near zero; the pre-registration discipline (predict before you look) keeps it honest.

2. **The self-grading-pipeline audit (highest external value).** Teams ship
   LLM-as-judge and RLAIF pipelines that grade their own work and do not know they are
   blind. Self-preference and the other judging biases are documented and live in
   production right now. A short playbook, "how to tell if your eval is grading itself,
   and what a decorrelated check actually costs you," with the decorrelation study as
   the worked example and the named biases as the failure catalog, meets a gap that is
   shipping today and that almost no one has the measurement posture to name.

3. **A residue benchmark (net-new artifact).** Most benchmarks measure verifiable
   things and score the human against the model. The hole is the other direction: a
   small, pre-registered benchmark of experiential judgments where the human is the gold
   standard and models are scored against the human. Even a tiny honest one is citable
   and underprovided. The product-flow follow-up study is the seed.

4. **The residue map (writing and reach).** Cataloging the residue plainly (what
   resists verification, why the resistance is structural, with concrete examples) is
   itself a contribution, because the framing is not yet written down in plain language.
   Low effort, real reach, and it plants the framing before anyone else states it
   clearly.

## What would falsify the value claim

If a judge model reaches human-level agreement on experiential quality across genuinely
new products, with no lived signal of its own, then the residue closes and the
human-as-medium edge closes with it. That is the measurable thing to watch. The bet is
that the residue has an irreducible core for as long as genuinely new products keep
appearing, because each new product is a medium the judge has not yet been trained on.
