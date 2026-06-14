# Robustness Audit: decorrelation-study

Date: 2026-06-14. Branch: `claude/repro-hardening`. Tree: clean.
Scope: an adversarial audit plus safe, additive hardening. No published file
was edited, no published number was changed, and nothing was pushed. Every
number below was reproduced against the live harness tonight
(`python3 harness/align_report.py`, `python3 harness/metrics.py`,
`SCORE_STEM=1 python3 harness/metrics.py`).

This file is itself a recommendation document. It changes no conclusion of the
study. See the GATE at the end: nothing here ships until Kevin reviews it.

---

## Verdict (one paragraph, honest)

The study is more robust than most work of its kind and its published numbers
are correct: every headline figure reproduced exactly tonight, and the
canonical `runs/RESULTS.json` regenerates byte-identical to its committed pin.
The honesty discipline is real, not decorative: pre-registration was frozen
before data, the failed 1.20x effect-size bar ships as a finding, and the H2
flip is shipped rather than buried. The exposure is not in the data. It is in
scoring choices that were not frozen before the data was seen, and in
write-up wording that calls those choices smaller than they are. The single
most serious item is that the one answer-key element that decides the H2
ordering (defect `11-d5`) was adjudicated in after the reviews were visible,
inside the very result the study is being honest about. None of this makes any
current number wrong. It means the load-bearing H2 ordering rests on knobs that
a future round must freeze in advance, and that two published sentences should
be softened. Bottom line: the data is sound, the discipline is genuine, and the
remaining risk is forking-paths exposure that hardening (done tonight for the
reproduce path and the next round) and two wording edits (recommended, not
applied) close.

---

## What is SOLID (defended, all verified tonight)

1. **Every published number reproduces exactly.**
   Strict: claude 23/30, gemini 27/30, codex 21/30; phi
   corr(claude,gemini) = -0.184, corr(claude,codex) = +0.327,
   corr(gemini,codex) = +0.267; H1 union 30/30 vs best-single 27, payoff 1.11x;
   H4 all-models-missed 0. Lenient (`SCORE_STEM=1`): gemini 28, codex 23,
   payoff 1.07x. `make verify` prints
   `OK: strict results reproduce byte-identical to committed runs/RESULTS.json`
   and exits 0. No false published number was found.

2. **Codex 0/4 performance is the durable headline, and it is matcher-independent.**
   Verified by reading the raw review text, not the scorer: across the
   performance-defect snippets, Codex names the spec/logic/security/boundary
   issue and never the performance one, while Gemini caught all four. In the
   strict per-type table, `performance (4)` shows codex `0/4` and gemini `4/4`.
   This survives every scoring knob. It is the study's strongest claim and it
   holds.

3. **The H2 honesty move is real.** The study refuses to claim H2 and ships the
   29-vs-30 flip rather than the variant where it "holds." Reproduced tonight by
   driving `harness/score.py` in memory (no tracked file touched): with the
   30-defect key, claude-codex is the top pair (+0.327); dropping the
   reconciliation-added `11-d5` makes gemini-codex top (+0.406, H2 refuted). The
   study claims neither ordering.

4. **Pre-registration was genuinely frozen before data.** `PRE_REGISTRATION.md`
   fixed the 1.20x bar in advance; the H1 result (1.11x, bar not met) ships as a
   contradiction. Amendment 1 was logged before the confirmatory data and states
   the hypotheses are unchanged. Amend-before-not-after discipline is followed.

5. **Two specific claims survive adversarial knob-sweeping.**
   "Claude-Gemini is the lowest-phi (most decorrelated) pair" is the negative-sign
   pair in every reported variant, and the H1 effect-size null (< 1.20x) holds in
   every reported variant. These two survive the knob sweep as stated.

6. **The planter-is-a-rater conflict is mitigated honestly** via a blind external
   Gemini audit that found real holes in the author's own "clean" controls
   (the snippet-20 symlink hole), with the reconciliation logged in
   `runs/gemini_audit/RECONCILIATION.md`.

---

## WEAKNESSES (prioritized, with evidence)

Ties are broken toward the weakness. Evidence is file:line plus the harness
output above.

**W1 (most serious): the decisive answer-key element was adjudicated in after
the data was visible, and it is outcome-correlated.**
Defect `11-d5` (minconn > maxconn, `corpus/truth/11.json:53`) was added in commit
`8e80876`, whose subject is
`adjudicate: complete truth (11-d5) + report H2 as scoring-sensitive`. That one
commit bundles the answer-key addition (`corpus/truth/11.json`), the matcher
change (`harness/score.py`), the reframe (`runs/RESULTS_model_only.md`), and the
regenerated `runs/RESULTS.json`. Verified tonight: `11-d5` was flagged by Claude
(review line 5) and Codex (review line 3) but not Gemini (grep of
`runs/full/11.gemini.txt` for minconn/maxconn is empty). Crediting it raises
corr(claude,codex) and lowers corr(gemini,codex), which is exactly the H2 pair
ordering. The single answer-key element that flips H2 is the one decided after
the reviews existed. This is the finding most in tension with the study's own
honesty thesis, because it sits inside the result the study is being honest
about.

**W2: H2 flips on at least two independent knobs, not one; the write-up says one.**
Reproduced tonight without editing any tracked file, by driving the existing
`harness/score.py`: at the default line-overlap tolerance `<= 1`
(`harness/score.py:74`), claude-codex is the top pair (+0.327 > +0.267, H2
holds); at `<= 2`, gemini-codex becomes top (+0.218 < +0.267, H2 refuted), and
this is independent of the stemming knob and independent of `11-d5`. So the
matcher-tolerance knob flips H2 on its own, and the `11-d5` answer-key knob flips
it on its own. README.md:41 says "flips on a single scoring choice";
docs/index.md:139 says "a single judgment call." Both understate the
dimensionality.

**W3: the matcher has at least five degrees of freedom; only one (`SCORE_STEM`)
is disclosed.** In source: line-gap tolerance hard-coded `<= 1`
(`harness/score.py:74`), content-match threshold hard-coded `best_score = 2` so a
match needs `> 2` shared words (`harness/score.py:79`), the affinity tie-break
(`harness/score.py:55-64`), and the answer-key completion rule. None was
pre-registered as a named value, and the current values happen to land on "H2
holds." All are now named in `docs/FORKING_PATHS.md` (committed locally).

**W4: H2 is severely underpowered, and the write-up undersells how severe.** The
two leading phi values differ by 0.06 (claude-codex +0.327 vs gemini-codex
+0.267) at n = 30, with Fisher-z 95% CIs that overlap across nearly their whole
range. `runs/RESULTS_model_only.md:46` calls this "pure sampling noise at n=30,"
which is correct but unquantified. The study asserts the noise rather than
showing it (e.g. the bootstrap top-pair share).

**W5: H1's 1.11x rests on a margin of exactly 3 defects on a denominator of 30.**
Union 30 vs best-single 27 is a 3-defect margin (04-d3, 11-d1, 11-d5), one of
which (`11-d5`) is the reconciliation-added element from W1 and the other two are
single-rater Claude-only catches. The "modest yes" is 3 binary events with a wide
CI, inside the noise band of the 1.20x bar it failed. README.md gives 1.1x without
flagging the 3-event margin.

**W6: the README reproduce sequence corrupts its own canonical results file.**
Confirmed tonight: `runs/RESULTS.json` is git-tracked, and the README's third
command `SCORE_STEM=1 python3 harness/metrics.py` writes that same path
(`harness/metrics.py:111`). After running the three README commands in order, the
strict pin (best-single 27 / 1.11x) is silently overwritten with lenient numbers
(28 / 1.07x) and the tree goes dirty (`git status` showed ` M runs/RESULTS.json`
immediately after the lenient run). The local `make verify` gate (strict-only)
recovers it byte-identical, but the README path is the trap.

**W7: H4 is in the pre-registration but absent from every public file.** The
harness computes all-models-missed = 0, so H4 (the unanimity hypothesis) is
effectively null, yet the README hypothesis list names only H1/H2/H5. A
pre-registered hypothesis silently vanishing from the write-up is a minor
violation of the study's own ship-the-contradiction rule. Fix: ship an explicit
H4 null verdict.

**W8: two in-repo provenance documents disagree on the answer-key size.**
`corpus/MANIFEST.md` says 30 defects while the earlier frozen
`RECONCILIATION.md` says 29 ("ground truth of record") and does not list
`11-d5`. The manifest was updated post-hoc to absorb `11-d5`; the larger count is
the one that makes H2 hold.

**W9: FP rates rest on 4 clean controls only** (snippets 16-19): claude 1,
gemini 3, codex 0. One flag moves a rate by 25 points. The "Codex most
conservative, zero FPs" ranking is directional, not established at n = 4.

**W10: defect non-independence.** 20 snippets carry 30 defects with clustering
(snippet 11 carries 5, 08 carries 3, 04 carries 3). The phi correlations and the
recall CIs implicitly treat 30 as independent trials; true effective n is between
16 and 30, so every CI here is, if anything, optimistically narrow.

**W11: the next-round protocol repeats the unfrozen-matching mistake.**
`probes/PROTOCOL.md` step 5 says "match steps and classify each" with no matching
rule and undefined scoring-class boundaries, the same degree of freedom that bit
this study. It is not yet a hardened pre-registration.

---

## CLAIMS to soften (recommendations only; nothing published was changed)

These are wording recommendations for Kevin to decide on. Do not treat any of
these as applied. README.md and docs/index.md were not edited.

1. **README.md:41 / docs/index.md:139, "flips on a single scoring choice / a
   single judgment call."** Understated (W2). H2 also flips on the line-gap knob
   (`harness/score.py:74`) at tolerance 2, independent of stemming, and on the
   post-hoc `11-d5` answer-key addition. Recommended reframe: "flips on the
   scoring instrument: at least two entangled choices (matcher tolerance and the
   post-hoc `11-d5` answer-key addition), the latter adjudicated after the reviews
   were visible." This strengthens the anti-inflation thesis rather than weakening
   it.

2. **Claude-Gemini "anti-correlated."** The sign is negative in all four reported
   variants, but the magnitude is small (~ -0.15 to -0.18) with a CI that crosses
   zero, and in the wider defensible knob space corr(claude,gemini) can go
   positive. Recommended: demote to the claim that survives the sweep,
   "Claude-Gemini is the lowest-phi (most decorrelated) pair," and hedge or drop
   "anti-correlated."

3. **`runs/RESULTS_model_only.md:46`, "pure sampling noise at n=30."** Correct but
   unquantified (W4). Recommended: add one shown number, e.g. the bootstrap
   top-pair share and that the top-two phi 95% CIs overlap across nearly their
   full range. Converts assertion to evidence.

4. **README.md best-single "27"** with no inline qualifier, when the README's own
   third command yields best-single 28 (lenient). Recommended inline qualifier:
   "(strict; 28 lenient)."

5. **MANIFEST vs RECONCILIATION (W8).** Recommended: reconcile the 29-vs-30
   discrepancy in-repo and state which document is authoritative.

6. **H1 1.11x.** Recommended: state the margin inline wherever it appears: "union
   beats best-single by exactly 3 defects (04-d3, 11-d1, 11-d5), one
   reconciliation-added."

7. **H4.** Recommended: add an explicit H4 null verdict to RESULTS and README so no
   pre-registered hypothesis silently disappears.

---

## What was hardened tonight (additive, local, unpushed)

All additive. No published file, number, harness behavior, or corpus truth was
changed.

1. **One-command reproduce path** (Makefile, commit `2b246b6`, already present;
   verified tonight, not duplicated).
   - `make repro` runs the three documented commands and prints the headline
     numbers.
   - `make verify` regenerates strict-only and diffs against the committed pin;
     tonight it printed
     `OK: strict results reproduce byte-identical to committed runs/RESULTS.json`,
     exit 0, tree clean. Strict-only, so it sidesteps the W6 lenient-clobber and
     gives a stranger a real pass/fail gate.

2. **Forking-paths ledger** (`docs/FORKING_PATHS.md`, commit `5ad05a9`). Records
   every matcher knob with reproduction steps and the verified harness output for
   each. Adds no claim, changes no published number, touches no corpus truth.

3. **Frozen R2 pre-registration** (`round2/PRE_REGISTRATION_R2.md`, commit
   `8dd8f9e`, 393 lines). Header: "FROZEN pre-registration for a future round.
   NOT yet executed. No data has been collected against it." Dated 2026-06-14. It
   pre-commits every forking path the audit found, before any future data:
   - All five scorer knobs as named canonical values: stemming OFF, line-gap
     `<= 1`, content threshold `> 2`, affinity tie-break with an explicit
     lowest-id final tiebreak, plus the answer-key rule. A 12-cell sensitivity
     grid is declared; "robust" means holds in all 12, never selected from.
     (Closes W2, W3.)
   - The single H2-resolving rule: a candidate enters the key iff at least two
     model families flag it AND an external decorrelated adjudicator model (named
     before any review is read) confirms it real, replacing round 1's unbounded
     "the human adjudicates." H2 is resolved only if the top-two phi 95% CIs
     separate, never on point estimates. (Closes W1.)
   - Target n at least 200 defects, one per snippet (independence), at least 10
     clean controls, and a no-peek stopping rule, with the power numbers recorded.
     (Closes W4, W9, W10.)
   - Folds in the W6 pin-write fix, the W7 explicit H4 computability report, the
     W8 single-source provenance, and the W11 `probes/PROTOCOL.md` step-5
     matching/classification freeze, all as pre-commitments.

Honesty note on the R2 pre-registration: it is frozen before any future data and
is designed to close the forking paths this audit found. It introduces no new
data, no new model review, and no new experimental snippet. It claims nothing the
data does not support, because it makes no claim yet.

## Recommended next safe steps (NOT applied; each touches a published surface or
harness behavior, so each stays a recommendation)

- Make the lenient run write a separate file (e.g. `runs/RESULTS_lenient.json`),
  or let only the strict run write the pinned `runs/RESULTS.json`, killing the W6
  clobber.
- Align `harness/align_report.py` with `harness/metrics.py` on the 20-snippet
  corpus (exclude the smoke artifact `001`, the source of the lone benign
  ALIGNMENT WARNING) so the two scripts agree on 20-vs-21.
- Pin the lenient and align_report outputs too, so all three documented outputs
  become mechanically confirmable.
- Add a regression test asserting the canonical strict numbers.

---

## GATE

Nothing in this audit has been published or pushed. No published file
(README.md, docs/index.md), no published number, no harness logic, and no corpus
truth was changed tonight. The only tracked additions are this audit file, the
Makefile, the forking-paths ledger, and the frozen R2 pre-registration, all
local commits on `claude/repro-hardening`.

Every item in the CLAIMS-to-soften section and every item in the next-safe-steps
section is a recommendation. Kevin must review before any change to the study or
any new claim. The R2 pre-registration is frozen and must stay frozen until the
next round begins; it must not be edited to fit data after data is collected. If
a published claim should change, that decision is Kevin's, made here on the
recommendation, not by an edit slipped into the published surface.
