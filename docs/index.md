---
title: "Do AI code reviewers have complementary blind spots?"
date: 2026-06-13
---

# Do AI code reviewers have complementary blind spots?

<p class="dek">A pre-registered test of three AI models reviewing the same planted bugs: what each one missed, the result I could not honestly claim, and why the most useful finding was about my own measuring stick.</p>

<p class="meta">Kevin Madson · June 2026 · 9 min read</p>

> **If someone forwarded this to you:** I build software with AI agents, programs
> that read and review code on their own, often several different models at once.
> A natural question is whether running more than one model actually helps, or
> whether they all just agree. I ran a small, pre-registered experiment to find
> out. The honest answer is more interesting than a clean yes or no, and the part
> I am proudest of is the result I decided I was not allowed to claim.

<p class="contact-card">
<a href="https://github.com/KiwiMaddog2020/decorrelation-study">github.com/KiwiMaddog2020/decorrelation-study</a>
<a href="mailto:kevinmadson@protonmail.com">kevinmadson@protonmail.com</a> <!-- pragma: allowlist -->
</p>

---

## The question, and why it matters for self-improving systems

When you ask several reviewers with different training to look at the same code,
do the gaps in what they notice line up, or do they cover for each other? If they
cover for each other, an ensemble is worth the cost: each one is blind to things
the others catch. If their blind spots overlap, you are paying three times for
one opinion.

This is not only a code-review question. Any system that improves itself has to
check its own work, and a checker is blind to exactly the kinds of mistakes it
would make itself. That is the trap behind a lot of AI safety worry: a loop that
grades its own output cannot see the errors baked into its own judgment. The
standard escape is to bring in a checker whose errors are not correlated with the
thing being checked. So the practical question, "is it worth running a second
model," and the deep question, "can a system safely judge itself," are the same
question wearing different clothes. I wanted a real number, not an intuition.

## The setup, and the rule I made to keep myself honest

I wrote 20 small, realistic Python functions: an LRU cache, a token-bucket rate
limiter, a connection pool, a currency converter, that kind of thing. Into 16 of
them I planted defects with an exact answer key, the line, the type, the precise
description. The other 4 I left genuinely correct, to measure how often a reviewer
flags a bug that is not there. Thirty planted defects in all, spread across seven
kinds: logic, security, concurrency, off-by-one, API misuse, performance, and
contract violations.

The design put four reviewers on each snippet, blind, seeing only the code and the
same instructions: Claude, Codex (OpenAI), Gemini (Google), and one human, me. Four
differently-trained estimators, the bet being that they would have four different
error patterns. The three models did the reviews you are about to see. The fourth,
the human, turned out to be the most interesting part of the experiment, and not in
the way I planned; I will come back to it. Before collecting a single
review I wrote down the hypotheses, the metrics, and the scoring rules in a
[pre-registration](https://github.com/KiwiMaddog2020/decorrelation-study), and
committed it to git with a timestamp. That file is the honesty anchor. If the data
contradicted a prediction, I promised, the contradiction ships. It is easy to say
that. The rest of this note is what it cost me to mean it.

## The audit that caught its own answer key

I am the person who planted the defects, which means I am blind to the bugs I
introduced by accident. So before any reviews ran, I had Gemini, the model least
like me, audit every snippet for all defects, planted or not.

It found the planted ones. It also found that several of my supposedly clean
control functions were not clean. My "safe path join" used `os.path.abspath`,
which does not resolve symbolic links, so a symlinked directory could escape the
base it was supposed to be locked inside. A real security hole, in a function I
had labeled defect-free. My Unicode truncator quietly mishandled certain
character clusters. The answer key I wrote, and would have sworn was complete, had
holes the size of a security vulnerability.

This is the whole thesis arriving early and uninvited. The author of a checker
cannot certify the checker by inspecting it himself; it takes a reviewer whose
blind spots are different. I fixed the controls, promoted the symlink bug to a
real planted defect, and wrote the whole reconciliation down. The study had
already made its point before the experiment proper began.

## What the three models caught

With the answer key reconciled, the three models reviewed all 20 snippets, fresh
context each time, no memory of the audit, no peek at the answers. The headline
numbers, over 30 planted defects:

| reviewer | caught | false alarms |
| --- | --- | --- |
| Gemini | 27 / 30 | 3 |
| Claude | 23 / 30 | 1 |
| Codex | 21 / 30 | 0 |

Three genuinely different personalities. Gemini casts the widest net and pays for
it with the most false alarms. Codex is the cautious one: it caught the fewest
planted bugs but never once flagged a problem in a clean function. Claude sits in
between. None of them is simply best; they are tuned to different points on the
trade-off between catching everything and crying wolf.

Do they cover for each other? Somewhat. Together they caught all 30 defects, and
the best single reviewer caught 27. So the ensemble does strictly better than any
one model. But the gain is small, about 1.1 times the best single, well under the
1.2 times I had pre-registered as the threshold worth getting excited about. When
one reviewer is already thorough, a second and third add real but modest coverage.
I had guessed the payoff would be larger. It was not. That ships.

## The result I decided I was not allowed to claim

My second prediction was about which models would be most alike. I guessed Claude
and Codex would have the most similar error patterns. The data, scored by the
exact rule I had frozen in advance, said no: Gemini and Codex were the most
similar pair, and my guess was refuted.

Then I noticed the scorer had a bug. It matched a reviewer's finding to a planted
defect by comparing words, and it was failing on simple inflections. When Codex
wrote that a cache "does not mark the key as recently used," the scorer did not
connect "recently" to the answer key's "recency," so it threw away a correct catch
as if Codex had missed the bug. A real flaw in my measuring stick. I fixed it the
obvious way, by matching word stems instead of whole words.

The fix was correct. It was also the moment the study tried to seduce me. With the
better matcher, the numbers shifted just enough that my refuted prediction came
back to life: now Claude and Codex were the most similar pair, and my hypothesis
held after all. A principled bug fix to my own instrument had flipped the headline
from "I was wrong" to "I was right."

Here is the table that stopped me:

| scoring choice | most-similar pair | my prediction |
| --- | --- | --- |
| strict matcher, 29 defects | Gemini-Codex | refuted |
| strict matcher, 30 defects | Claude-Codex | holds |
| stemmed matcher, 30 defects | Claude-Codex | holds |

The verdict flips on a single judgment call, and the gaps between the top pairs
are tiny, the kind of difference that vanishes if you re-roll the dice. With only
30 data points, the ordering is not a finding, it is noise dressed up as one. The
tempting move was to report the version where I was right and footnote the rest.
The honest move was to report that **the prediction cannot be resolved at this
scale, so I am not claiming it.** The correlation ordering is inside the margin of
my own scoring rule. The measuring stick has a blind spot too, and it points
straight at the answer I wanted.

That is the same failure the whole study is about, now sprung on me by the study
itself. A system grading its own work will, without any bad intent, find the
grading choice that flatters the result. The only defense is a rule you wrote down
before you knew which way it would cut.

## What is actually true

Two things held up no matter how I scored them.

First, the most decorrelated pair of models is **Claude and Gemini.** Across every
version of the analysis their mistakes are anti-correlated: where one is blind,
the other tends to see. If you were going to run exactly two models to cover each
other, that is the pair, and it is not the pair I would have guessed.

Second, and this is the finding I trust most because it does not depend on the
scorer at all: the models are blind to different *kinds* of bug. **Codex caught
zero of the four performance defects.** Not one. I read its reviews of all four to
be sure; every time, it found the logic or security problem sitting right next to
the slow code and walked straight past the slowness. Gemini caught all four. Claude
was the weakest on off-by-one errors. The diversity that matters is not "more
reviewers," it is reviewers that fail in different directions. An ensemble is
worth it when its members are blind to different things, and these three are.

## The reviewer I was testing wrong

The human was supposed to be the centerpiece. The bet: a person, shaped by a
lifetime of experience instead of gradient descent, would be the most decorrelated
reviewer of all, not the strongest, just the least like the machines.

There is a problem I should have seen before I built a single snippet. I direct
these systems for a living; I do not sit and read source line by line hunting for
subtle bugs. That is exactly the work I hand to the models. So putting me in the
reviewer's chair and asking me to spot a timing leak in an HMAC comparison does not
measure whether my judgment is decorrelated from a model's. It measures whether I
can read code, which is a different thing and not my strength. A reviewer who is not
a fluent code reader misses most of these and comes out looking weak, when the entire
point was to measure difference, not skill. The test would have quietly relabeled
"not a programmer" as "not decorrelated." Those are not the same, and treating them
as the same would be its own kind of inflation, the exact thing this study keeps
trying not to do.

The fix is not a better human. It is a better question. The place a person's
judgment really is uncorrelated with a model's is not the code, it is the thing the
code becomes. A human knows what it feels like to be on the other end of an
interface: where it is confusing, where it fights the way you actually want to move
through it, what is missing that no specification lists. A model can predict, and
with enough data predict well, what a human will feel using something. What it
cannot do is be the human feeling it. So at the frontier, where the product is
genuinely new, the human is the one who generates the reaction the model can only
learn from secondhand. Models converge on the preferences they have seen; a human is
the one feeling the new thing first. The human's decorrelated value lives in using
the product, a different sense entirely, and a corpus of code defects is blind to it.

So H3, the way I posed it, is the wrong test, and I am not going to fake it with an
unqualified or contaminated human pass just to fill the box. The honest result is a
lesson about measurement itself: you measure a reviewer's decorrelation in the
domain where they are competent, not the one where they are not. The experiment that
would actually test it, a human and the models both evaluating real product flows
and counting what the human catches that no model does, is the one worth running
next; its design is a note in the repo. This was meant to be the centerpiece.
Instead it became the clearest example in the whole study of testing the wrong thing
and catching it in time.

## What this has to do with recursive AI

The small lesson is practical: if you run AI reviewers in an ensemble, choose them
for *different* blind spots, not for individual strength, and do not expect the
combination to be dramatically better than your best single model. The bigger
lesson is the one I keep relearning. Every checker has a verification shadow, the
region of mistakes it cannot see because they are its own. My planted-defect answer
key had one, and an outside model found the security hole in it. My scoring rule
had one, and it pointed at the conclusion I was hoping for. A system that improves
itself is a checker grading its own work, and it will have the same shadow, and it
will not feel like a problem from the inside. The escape is not a smarter checker.
It is a *different* one, with errors that do not line up, plus a rule fixed in
advance so that the grader cannot quietly choose how it grades. And "different" has
more than one axis: a different model family, a different scoring rule, or a human
put in the one seat where a human is genuinely unlike the machine, not reading the
work, but living with it.

That is a modest, almost boring conclusion, and I think it is the right one.
Decorrelation is real, it is worth paying for, and it is most valuable exactly
where it is least comfortable: when it is checking you.

The corpus, the pre-registration, the audit, every review, and the scoring code
are all in the [repository](https://github.com/KiwiMaddog2020/decorrelation-study),
and the numbers above reproduce from it. If they do not reproduce on your machine,
that is a bug, and I want to hear about it.

---

<p class="byline"><em>I build agentic systems across multiple coding LLMs. More of my research notes are <a href="/">here</a>.</em></p>
