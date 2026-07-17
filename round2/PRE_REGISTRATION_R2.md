# Pre-registration R2: decorrelated reviewer families at scale

**Status: FROZEN pre-registration for a future round. NOT yet executed. No data has been collected against it.**

Date frozen: 2026-06-14. Author: Kevin Madson. Analysis collaborator: Claude (Opus 4.8).

This file is the honesty anchor for a planned scale-up of the round-1 study
(`PRE_REGISTRATION.md`, `PRE_REGISTRATION_AMENDMENT.md`,
`runs/RESULTS_model_only.md`). It exists so that when real data is later collected,
no result can be selected after the fact to flatter a conclusion. Round 1 was
honest about its limits but left the scoring instrument under-specified: the
methodology audit (`docs/FORKING_PATHS.md`) found at least five live researcher
degrees of freedom in `harness/score.py`, two of which each flip the H2 verdict
on their own. R2 closes every one of those paths by naming a value here, before
any new review is read.

Nothing in this file changes a round-1 conclusion. Round 1 still reports exactly
what it reported: H2 unresolvable at n=30, H1 effect-size null, Codex blind to
performance, Claude-Gemini the most decorrelated pair. R2 is the resolvable
successor, not a re-analysis of round 1.

---

## 0. Why R2 exists (the gap R2 closes)

Round 1's published escape hatch was correct given its instrument: "report the
sensitivity, claim nothing." The audit verified, against the live harness, that
the H2 ordering flips on more than the one scoring choice the write-up names:

- **Answer-key knob (29 vs 30).** Dropping the reconciliation-added defect
  `11-d5` (`minconn > maxconn`) makes gemini-codex the top pair
  (corr 0.406 > 0.318), H2 refuted; keeping it makes claude-codex top
  (0.327 > 0.267), H2 holds. `11-d5` was flagged by Claude and Codex but not
  Gemini, so crediting it mechanically moves the exact pair ordering H2 is about,
  and it was adjudicated in *after* the reviews were visible.
  Independently reproduced 2026-06-14 by driving the existing `harness/score.py`
  in memory (no tracked file touched): 30 defects -> corr(cl,cx)=+0.327,
  corr(gm,cx)=+0.267, top claude-codex; 29 defects -> corr(cl,cx)=+0.318,
  corr(gm,cx)=+0.406, top gemini-codex.
- **Line-overlap tolerance knob.** `harness/score.py:74` hard-codes `<= 1`. At
  `<= 2` the top pair flips to gemini-codex (corr(cl,cx) falls to +0.218, below
  corr(gm,cx)=+0.267), H2 refuted; at `<= 0` and `<= 1` claude-codex stays top.
  Independently reproduced 2026-06-14 the same way. This knob flips H2 on its
  own, independent of stemming and independent of `11-d5`.

So at least two entangled choices each flip H2. R2's job is to make every such
choice a number frozen here, so the next verdict cannot ride on a knob nobody
declared.

---

## The question (unchanged from round 1)

When several reviewers with different training each look at the same code, does
the diversity of their blind spots produce complementary coverage that no single
reviewer matches, and which reviewer families share blind spots? The hypotheses
below are the round-1 hypotheses carried forward, sharpened with frozen decision
rules and a target sample size, plus one new exploratory family hypothesis.

Reviewer families in R2: **Claude, Codex (OpenAI), Gemini (Google)**, optionally
**one or more additional model families** (see Design), and **one human (Kevin)**
in the product-flow track only (see H3-prime). Each model is treated as a trained
estimator with its own error distribution.

---

## 1. The frozen scoring instrument (closes forking paths A-E)

This is the heart of R2. Round 1 left these as code constants; R2 fixes them as
named, pre-committed values. **The five knobs below are frozen before any R2
review is collected.** Exactly one canonical setting is primary; everything else
is a *declared* sensitivity grid, reported always, never chosen after seeing
which way it cuts.

### Canonical (primary) scorer, frozen

| knob | source of freedom | R2 canonical value | rationale |
|------|-------------------|--------------------|-----------|
| A. token stemming (`SCORE_STEM`) | `score.py:18,46` | **OFF (strict, whole-token match)** | The pre-registered round-1 matcher. Stemming was only ever a sensitivity variant; it stays one. |
| B. answer-key completion rule | amendment-1 "human adjudicates" | **frozen criterion, see section 2** | Replaces "a person decides" with a rule decided before reviews are read. |
| C. line-overlap tolerance | `score.py:74`, was `<= 1` | **`<= 1` line** | Matches round-1 strict; `+/-1` absorbs off-by-one line citations without merging adjacent distinct defects. |
| D. content-match threshold | `score.py:79`, was `best_score = 2` | **`> 2` shared content words** (i.e. needs >= 3) | Round-1 default; high enough that a no-line-overlap match requires real lexical agreement, not one shared stopword-survivor. |
| E. affinity tie-break | `score.py:55-64,77` | **type-match (+2) plus shared-content-word count, highest wins; ties -> lowest defect id** | Round-1 rule, with an explicit deterministic tiebreak (lowest id) added so multi-defect snippets are fully determined with no implicit "first listed" dependence. |

The canonical scorer is therefore: **strict tokens, line gap `<= 1`, content
threshold `> 2`, affinity tie-break with lowest-id final tiebreak, and the
section-2 answer-key rule.** This single setting is the only one any R2 headline
claim may rest on.

### Declared sensitivity grid (reported, never selected from)

Every R2 results file MUST report all of these alongside the canonical number,
so a reader sees the full forking surface, not the one cell that happened to land
where the author hoped:

- stemming: {OFF (canonical), ON}
- line gap: {0, 1 (canonical), 2}
- content threshold: {2 (canonical), 3}
- answer key: {section-2 rule (canonical)} only. There is no "drop a defect"
  variant in R2 because section 2 freezes the key before reviews are read, so
  there is no post-hoc 29-vs-30 fork to report.

That is 2 x 3 x 2 = 12 scorer cells. **A claim is "robust" in R2 iff it holds in
all 12 cells.** A claim that holds only in the canonical cell is reported as
canonical-only and explicitly flagged as knob-sensitive, never as the result.

### Reproducibility fix carried as a pre-commitment (closes W6)

Round 1's `runs/RESULTS.json` is git-tracked and overwritten by every
`metrics.py` run, so a lenient run silently clobbers the canonical pin. R2
freezes the rule that **only the canonical (strict) scorer may write the tracked
pin**; every sensitivity-grid cell writes to a distinct, untracked-or-suffixed
path (e.g. `runs/RESULTS_R2.json` for canonical, `runs/sensitivity/<cell>.json`
for the grid), and each emitted file records the exact knob values that produced
it. No documented reproduce command may leave the canonical pin holding
non-canonical numbers.

---

## 2. The single rule that resolves H2 (closes the sharpest forking path, W1)

Round-1 amendment 1 pre-registered a *procedure* ("an unmatched flag is a
candidate; the human adjudicates; if real, it is credited") but **no rule for the
adjudication itself**. That left an unbounded degree of freedom sitting directly
on the hypothesis it decides, and the one defect it decided (`11-d5`) flips H2.

R2 replaces the person with a frozen criterion, **decided here, before any R2
review is read:**

> **R2 answer-key completion rule.** Start from the planted ground truth. A
> *candidate* (a flag matching no planted defect) is admitted to the answer key
> **iff both**: (a) **>= 2 of the reviewer families flag it independently**, AND
> (b) **an external decorrelated model not in the reviewer panel** (the
> "adjudicator model", named and frozen in the run manifest before reviews are
> read) **confirms, from the snippet alone, that it is a real defect** and writes
> a one-line justification. A candidate failing either test is recorded as a
> logged false positive for whoever raised it, never silently dropped. The human
> does not adjudicate candidates onto the answer key in R2; the human's only role
> in the key is to *run* this deterministic rule and to break a literal tie in
> the adjudicator model's verdict (which is logged as a known residual judgment
> call).

This rule is symmetric across families by construction: it cannot prefer a
Claude+Codex defect over a Gemini+X defect, because it never looks at *which*
families flagged a candidate beyond counting that >= 2 did, and the confirming
adjudicator is decorrelated from the panel. Under this rule the round-1 `11-d5`
case would have been admitted on its merits (>= 2 families flagged it, an
external model can confirm `minconn > maxconn` is real) **or not**, but either
way the decision is made by a frozen rule before the correlation is computed,
not by a person who can already see the pair ordering.

**H2 is declared "resolved" in R2 only if the top-two pairwise phi 95% confidence
intervals separate (do not overlap).** Never on point estimates. If they overlap
at the target n, the honest verdict is "still within scoring/sampling noise,"
reported as such, exactly as round 1 did, and the decision rule (section 6) says
scale further or stop, not "pick the cell where they separate."

---

## 3. Hypotheses (fixed, falsifiable, with frozen decision rules)

Confirmatory:

- **H1 (coverage payoff).** The union of all reviewer families catches strictly
  more true defects than the single best family. Pre-registered effect size of
  interest: union catches **>= 1.20x** the best single family's count.
  *Decision rule:* H1's effect-size claim is supported only if the payoff ratio's
  95% CI lower bound is >= 1.20x in the canonical cell AND the point estimate is
  >= 1.20x in all 12 grid cells. Round 1 returned 1.11x (strict) / 1.07x
  (lenient), CI not computed; R2 computes the CI and holds the same bar.

- **H2 (correlation structure).** Among model families, the two most architecturally
  similar share the highest pairwise error correlation. Round-1 prediction
  retained: corr(Claude, Codex) is the highest model-model pair.
  *Decision rule:* resolved only if the top-two phi 95% CIs separate, per
  section 2. Direction predicted; magnitude not.

- **H5 (type-specific blindness).** Per-defect-type catch rates differ across
  families. *Decision rule:* a family-by-type cell is called a real blind spot
  only if the family's catch rate on that type is 0 (or differs from the panel
  mean) with a 95% CI that excludes the panel mean, AND the gap is verified by
  reading the reviews, not only the scorer (the round-1 Codex-performance result
  was confirmed this way and is the model for R2).

Exploratory (declared exploratory because they remain underpowered even at the
R2 target n):

- **H4 (unanimity is a blind-spot signal).** When all model families agree on a
  defect call, they are wrong more often than when they split. Round 1 found
  **0 all-models-missed cases at n=30**, so H4 was uncomputable; R2 reports H4's
  computability and, if computable, its verdict, so no pre-registered hypothesis
  silently vanishes (closes audit W7). If still uncomputable at the R2 n, that
  null is reported explicitly.

- **H6 (NEW: family-pair blind-spot stability).** The most-decorrelated model
  pair identified in round 1 (Claude-Gemini) remains the lowest-phi pair at
  scale. Exploratory because it is a directional carry-forward of a round-1
  observation, pre-registered here so confirming it later is not a post-hoc story.

- **H3-prime (human decorrelation, re-sited).** Round-1 H3 ("is the human the
  most decorrelated reviewer") was the wrong test as posed: asking a non-coding
  operator to find subtle code bugs measured code-reading skill, not
  decorrelation. R2 does **not** test human decorrelation in the code-review
  track. It is tested only in the product-flow track
  (`docs/FOLLOWUP_human_product_decorrelation.md` and `probes/PROTOCOL.md`),
  where the human has genuine ground truth, under that track's own frozen rules
  (section 7). Stated here so the centerpiece is not silently dropped, only moved
  to where it is a fair test.

---

## 4. Target sample size and stopping rule (closes W4, W10)

Round 1 ran at n=30 defects, where every gap of interest sits inside the scoring
noise (a seeded bootstrap put claude-codex top in only ~58% of resamples; the
top-two phi CIs overlapped across nearly their whole range). R2 pre-declares its n
and its stopping rule before any data, so the correlation is not read early and
stopped when it looks good.

Power reasoning carried from the statistical lens, recorded so the target is not
arbitrary:

- Resolving the round-1 observed ~0.06 phi gap at 80% power needs ~1000+ defects
  (impractical).
- Pinning a single pairwise phi to a 95% CI half-width of ~0.10 needs ~390
  defects.
- Powering for a moderate 0.15-0.20 phi gap needs ~300-540 defects.

**R2 target (frozen):** a floor of **>= 200 planted defects across >= 100
snippets**, with **>= 10 clean controls** (round 1 had 4; one false flag moved a
rate 25%, so FP rates were directional only; >= 10 gives FP rates a usable
denominator and closes W9).

**Defect non-independence (closes W10).** Round 1 had 30 defects clustered in 20
snippets (snippet 11 alone carried 5), so the effective n was below 30 and every
CI was, if anything, optimistically narrow. R2 freezes **one of these two designs,
chosen here, before data:**

> **R2 chooses: one planted defect per snippet** for the confirmatory corpus, so
> the 200 defects are 200 independent snippets and the binary caught/missed
> trials are genuinely independent. Multi-defect snippets, if used at all, live in
> a separate exploratory sub-corpus analyzed with a pre-registered cluster-robust
> method (snippet-level cluster bootstrap), and never enter the confirmatory phi
> CIs.

**Stopping rule (frozen).** Collect the full pre-declared corpus before computing
any pairwise correlation. Do **not** look at H2's ordering until all >= 200
confirmatory defects are scored. H2 is declared resolved only if its top-two phi
95% CIs separate at that n; if they overlap, the verdict is "unresolved at this
n," and the section-6 decision rule governs whether to scale further. No optional
stopping, no peeking.

---

## 5. Design (carried from round 1, with R2 freezes)

- **Corpus.** >= 100 snippets of real, realistic code, >= 200 planted defects
  (one per confirmatory snippet, per section 4), >= 10 clean controls. Defects
  balanced across the seven round-1 types (logic, security, concurrency,
  boundary/off-by-one, api-misuse, performance, spec-violation), with the
  per-type target counts frozen in the corpus manifest before planting so no type
  is back-filled to rescue H5.

- **Planter-is-a-rater mitigation, hardened.** Round 1 mitigated this with a blind
  external Gemini audit that found real holes in the author's own controls (the
  snippet-20 `safe_join` symlink hole), fully logged in
  `runs/gemini_audit/RECONCILIATION.md`. R2 keeps the blind external completeness
  audit AND adds the section-2 frozen admission rule, so no defect enters the key
  on the planter's word or a single person's post-hoc call. If Claude is the
  planter, **Claude reviews are scored but excluded from the H2 pair that includes
  the planter family when assessing planter bias**, and that exclusion is reported
  as its own sensitivity cell.

- **Blind independent review.** Each family sees only the snippet and the identical
  review prompt (`protocol/review_prompt.txt`). No family sees another's output.
  Models invoked clean-room (fresh context, no history). The adjudicator model
  (section 2) is named in the run manifest and is a family **not** in the
  reviewer panel.

- **Additional model families (optional, declared up front).** If more than three
  model families are run, the full pairwise phi matrix and the H1 union are
  computed over all of them; the H2 prediction is still specifically about the
  two most architecturally similar families, named in the manifest before data.

- **Provenance hygiene (closes W8).** Exactly one document is the authoritative
  answer-key-size record in R2 (the corpus manifest), and the count is written
  once, after the section-2 rule runs, and never edited post-hoc. Round 1's
  29-vs-30 disagreement between `corpus/MANIFEST.md` and the frozen
  `RECONCILIATION.md` is exactly the failure this prevents.

- **Metrics.** Identical to round 1: pairwise phi over caught/missed vectors (all
  pairs), coverage payoff (union / best single), unanimity calibration, per-type
  catch rate by family. R2 adds 95% CIs (Fisher-z for phi, Wilson or bootstrap
  for rates) to every headline number, and a seeded bootstrap (fixed seed in the
  manifest) reporting the fraction of resamples in which the predicted top pair is
  actually top.

---

## 6. Decision rule (frozen)

- If **H1's effect-size CI lower bound clears 1.20x** in the canonical cell and
  the point estimate clears it in all 12 grid cells: H1 effect size supported.
  Otherwise the null ships, as it did in round 1.
- If **H2's top-two phi CIs separate** at the target n in the canonical cell:
  H2 resolved in the indicated direction. If they overlap: "unresolved at this n"
  ships as the finding; scaling beyond 200 defects is justified only if the gap's
  point estimate is in the powered range (section 4) and the CIs are merely
  wide, not centered on zero.
- A clean null is as publishable as a clean positive. No outcome here is failure.
  A system that can only report success is the exact thing this study exists to
  argue against. Ties in any scored comparison break toward the weaker (more
  null) reading.

---

## 7. Product-flow track freeze (closes W11)

The divergence probes (`probes/PROTOCOL.md`) inherit round 1's single worst
forking path: **step 5 ("match steps and classify each") names no matching rule
and no scoring-class boundaries.** That is the same unfrozen-matching freedom that
made round-1 H2 unresolvable. Before the first R2 probe runs, the following are
frozen here:

- **Step-matching rule.** Model-pass steps and human-pass steps are aligned by a
  pre-declared step index agreed from the frozen flow definition (section
  `probes/PROTOCOL.md` step 1-2), not matched post-hoc. A model prediction counts
  as addressing a human-logged step iff it references the same frozen step index.
- **Scoring-class boundaries (frozen definitions).** The five classes
  (agree-friction, agree-smooth, model false-alarm, model miss, valence flip) and
  the model-miss split (visible-in-UI vs lived-knowledge) are decided per step by
  this rule, fixed before alignment: a step is a **model miss** iff the human
  logged friction at that frozen step index and the model pass logged
  delight/neutral (or no friction) at the same index; it is **lived-knowledge**
  (the structural residue) iff the friction the human logged is not present in any
  on-screen text of that step, judged from the frozen screenshots, and
  **visible-in-UI** otherwise. A **valence flip** is the specific case where the
  model logged delight/neutral and the human logged friction at the same index, or
  the reverse. These are the only admissible classifications; no class may be
  assigned after seeing the headline residue number.
- **Headline metric, frozen.** lived-knowledge misses / total friction points,
  per probe, with the per-class counts always reported beneath it.
- **Honesty.** Model pass frozen to `model_pass.md` and human pass to
  `human_pass.md`, both before alignment, both before either reads the other,
  exactly as `probes/PROTOCOL.md` already requires. R2 only adds the missing
  matching-and-classification rule so the residue number is not retrofitted.

---

## 8. Known limitations (declared up front, not discovered later)

1. **n = 1 human** in the product-flow track. Any human result speaks to this
   operator, never to humans in general. Carried from round 1.
2. **Planted is not wild.** Injected defects may be unrepresentative of in-the-wild
   defects. Host code is real to reduce this; the defects are not. Carried.
3. **The planter is also a rater family.** Mitigated by the blind external
   completeness audit plus the section-2 admission rule plus the planter-pair
   exclusion sensitivity cell; the residual risk is reported, not hidden.
4. **Possible host-code familiarity.** Models may recognize the open-source host
   code from training; contamination of the planted defects is low, familiarity
   with surrounding code is possible and noted.
5. **The adjudicator model is itself a model.** Section 2's confirming adjudicator
   is decorrelated from the panel but is not ground truth; its verdicts are logged
   with justifications so a human can audit them, and the one literal-tie human
   call is recorded as a residual judgment call.
6. **Even at >= 200 defects, the exact ~0.06 round-1 gap remains underpowered.**
   R2's n is chosen to resolve a *moderate* (0.15-0.20) gap, not the smallest one
   round 1 happened to observe. If the true gap is that small, R2 will honestly
   report "unresolved," not manufacture a verdict.

---

## 9. Verification debt for the human checkpoint

These are the things no agent can self-verify in R2; each gets a scheduled human
checkpoint before the corpus is locked, and human findings outrank agent findings:

- That the canonical scorer's five frozen knob values (section 1) are the ones
  actually wired into the R2 harness before the first review runs (read the code,
  do not trust a remembered value).
- That the adjudicator model named in the run manifest is genuinely outside the
  reviewer panel and was named before any review was read.
- That the per-type target counts were frozen in the manifest before planting.
- That the H2 correlation was not computed before the full corpus was scored
  (check the commit timestamps: corpus-lock commit precedes any metrics commit).

---

**Reminder: this is a FROZEN pre-registration for a future round. It has NOT been
executed. No data has been collected against it. When R2 is run, the first commit
of any R2 review datum must post-date this file, and any deviation from the freezes
above must be logged as a transparent amendment BEFORE the affected data is read,
never after, exactly as round 1's amendment 1 was.**
