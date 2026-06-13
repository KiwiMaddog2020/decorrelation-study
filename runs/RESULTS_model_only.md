# Results (model-only; human family pending)

60 clean-room model reviews (Claude, Gemini, Codex x 20 snippets) scored against
the reconciled ground truth (29 planted defects, 4 clean controls). The human
family (Kevin) is not yet in, so H3 is open. Numbers from `harness/metrics.py`;
machine-readable copy in `runs/RESULTS.json`. **This is pre-registered: the
contradictions below ship as findings, not footnotes.**

## Rater performance (29 planted defects)

| rater  | caught | false positives | operating point |
|--------|--------|-----------------|-----------------|
| gemini | 27/29  | 3               | high recall     |
| claude | 22/29  | 1               | balanced        |
| codex  | 20/29  | 0               | high precision  |

Three genuinely different operating points: Gemini sweeps widest (and pays in
false positives), Codex is the most conservative (zero FPs on the clean
controls), Claude sits between.

## H1 coverage payoff: directional YES, effect-size NO

Union of all three caught **29/29**; best single (Gemini) caught 27/29. The
ensemble strictly beats the best single reviewer (29 > 27), so combining helps.
But the ratio is **1.07x**, below the pre-registered interest threshold of 1.20x.
The gain is real but modest, because one thorough reviewer already catches most
defects. The pre-registered effect size was not met; that ships.

## H2 correlation structure: CONTRADICTED

Predicted: corr(Claude, Codex) is the highest pairwise model-model correlation.
Measured (phi over caught/missed vectors):

- corr(Gemini, Codex) = **+0.406**  (highest)
- corr(Claude, Codex) = +0.318
- corr(Claude, Gemini) = **-0.154**  (lowest; anti-correlated)

The two most similar models are **Gemini and Codex**, not Claude and Codex. And
the most *decorrelated* model pair is **Claude and Gemini**, whose errors are
anti-correlated: where one misses, the other tends to catch. The directional
prediction is falsified.

## H5 type-specific blindness: the strongest finding

Per-type catch rate (planted defects of each type caught):

| type           | n | claude | gemini | codex |
|----------------|---|--------|--------|-------|
| api-misuse     | 4 | 3      | 3      | 3     |
| boundary       | 4 | 2      | 4      | 3     |
| concurrency    | 3 | 3      | 3      | 3     |
| logic          | 6 | 5      | 5      | 5     |
| performance    | 4 | 2      | **4**  | **0** |
| security       | 5 | 4      | 5      | 4     |
| spec-violation | 3 | 3      | 3      | 2     |

**Codex caught 0/4 performance defects** (verified by reading its reviews of 01,
08, 11, 15: it flagged the correctness/security/logic issue in each and never the
performance one). Gemini caught 4/4. Claude is weakest on boundary (2/4). Families
genuinely own and miss different defect *types*. This is the qualitative payoff
the pre-registration flagged as valuable even if the confirmatory tails are weak.

## H4 unanimity (exploratory): 17 unanimous-caught, 0 unanimous-missed, 12 split

The decorrelation lives in the 12 split defects. With zero unanimous-missed, the
"unanimous and wrong" rate is not assessable here, as pre-registered for small n.

## Bonus: complementary candidates (the verification shadow, again)

Even against a ground truth already completed by the Gemini audit, the clean-room
reviewers surfaced real defects not in it: Codex (non-positive page size on 08,
minconn>maxconn on 11, double-release on 11), Gemini (stale-connection reuse on
11, hardcoded 100 minor-units / JPY-BHD on 15), Claude (KeyError on a malformed
event on 01). Fresh decorrelated reviewers keep finding more, which is the thesis.

## Honest headline

The big intuition (decorrelated models give a large coverage win) got a *modest*
yes. The specific correlation prediction (H2) was *wrong*. The cleanest, most
durable result is type-specific blindness (H5): Codex is blind to performance,
Claude weakest on boundary, and the most decorrelated model pair is Claude-Gemini.
The centerpiece, whether the human is the most decorrelated reviewer of all (H3),
is still open and needs the human reviews. A pre-registered study that contradicts
its own prediction and ships it is the exact discipline this work argues for.
