# Reconciliation: Gemini external audit -> ground truth of record

Policy (human-chosen): **complete the ground truth.** Add verified real defects
the audit surfaced; reject out-of-contract / nitpick findings; fix the clean
controls so any flag on them is an unambiguous false positive. The corpus grew
from 24 planted defects to **29**, and from 5 clean controls to **4**.

> **Update (superseded count):** this document records the corpus as of the
> Gemini-audit reconciliation, when the ground truth of record was **29
> defects**. That count was later superseded: defect `11-d5` (`minconn > maxconn`
> in snippet 11) was adjudicated into the answer key in commit `8e80876`,
> bringing the corpus to **30 defects**. The current authoritative count is
> `corpus/MANIFEST.md` (**30**), which matches the live harness output. The 29
> figures below are preserved as the historical reconciliation state, not the
> current count.

## Headline

The blind Gemini audit found **all planted defects (29/29 after reconciliation,
0 missed)**. Its real value was on the controls: it caught that several "clean"
snippets were not clean. The verification shadow landing on the answer key,
exactly as the study argues.

## Reclassified clean -> defective

- **20 safe_join** -> defective. `os.path.abspath` resolves `..` and absolute
  components but NOT symlinks, so a symlinked component inside `base` pointing
  out of it passes the prefix check. Tightened the docstring to clearly promise
  a symlink-resolved path, making the `abspath`-not-`realpath` choice a genuine
  security/subtle defect (20-d1). Re-audit confirms Gemini now reads it as
  "symlink traversal vulnerability ... direct violation of the docstring."

## Added to ground truth (verified real, in-scope)

- **04-d2** logic/moderate: `_split_fields` splits on every comma, breaking
  quoted fields (no CSV quoting).
- **04-d3** logic/subtle: `dict(zip(header, cells))` silently drops cells when a
  row has MORE fields than the header.
- **08-d3** performance/subtle: `page()` rebuilds the full id list O(N) on every
  call (paged walk becomes O(N*pages)).
- **11-d4** performance/subtle: `acquire()` calls `psycopg2.connect()` while
  holding the pool lock, serializing the whole pool behind a slow connect.

## Rejected (out-of-contract or nitpick -> the false-positive bait we want)

- 04 trailing `\r`: NOT a bug. `_split_fields` does `.strip()`, which removes it.
  (Correcting my own earlier call.)
- 19 "crashes on None": out of contract. The signature is `Mapping[str, str]`;
  None values are not valid input. Kept 19 clean.
- 18 redundant deepcopy: was real but perf-only. Fixed (see below) rather than
  recorded, so the control is pristine.
- 16/17 exotic-edge findings (CCC grapheme completeness, islice maxsize, etc.):
  nitpicks / out of contract.

## Fixed to pristine-clean controls

- **18 deep_merge**: rewrote to copy each leaf exactly once (no redundant
  deepcopy). Verified: correct merge, b-wins, no input mutation, fresh copies.
  Re-audit: only out-of-contract findings remain.
- **16**: the unicode truncator was an unfixable clean control. Any function
  claiming grapheme handling invites "your grapheme detection is incomplete"
  findings that are neither clearly real nor clearly false. **Replaced it** with
  `group_by`, whose contract is total (every item lands in exactly one group,
  first-seen key order, stable within group, no mutation). Re-audit: **0 findings.**

## Final corpus

16 defective + 4 clean = 20 snippets, **29 defects**. By type: logic 6,
security 5, api-misuse 4, boundary 4, performance 4, concurrency 3,
spec-violation 3. Difficulty: 26 subtle + 2 obvious anchors + 1 moderate.
Every cited line is live code (`align_report.py`); all 20 compile.
Ground truth is now of record, pending the 60 clean-room model reviews and the
human reviews.
