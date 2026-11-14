# decorrelation-study

## What this is

A small pre-registered experiment: three AI models and one human review 20 code
snippets with planted defects, blind, to test whether their blind spots line up
or cover for each other. Write-up is in docs/.

## Build, test, run

- `bash bin/check.sh` runs `make verify` (set `PYTHON=/path/to/python` if needed).
- `make verify` regenerates runs/RESULTS.json and fails on any drift from git.
- `make repro` runs the align, strict and lenient commands.
- Stdlib Python 3.10 or newer, no network needed.

## Layout

- corpus/: snippets/ (planted defects) and truth/ (answer key).
- harness/: scoring, metrics, alignment, and review runners.
- runs/: recorded reviews, audits and results.
- probes/: follow-up probe and its protocol.
- round2/: round 2 pre-registration.
- protocol/: reviewer prompt.
- docs/: GitHub Pages source for the write-up (the only published folder).
- bin/: local check script.

## House rules

- All work lands on the session branch, one commit per phase. No pull request unless asked. Never force-push or rewrite history.
- No GitHub Actions or other CI automation. Use the local check script.
- User-facing text has no em-dashes and keeps a PG-clean tone.
- Never skip or disable a test to get a pass.
- Published results, run data and pre-registrations are a research record and are never overwritten. New runs go in new folders.

## Invariants

- PRE_REGISTRATION.md, PRE_REGISTRATION_AMENDMENT.md and
  round2/PRE_REGISTRATION_R2.md are frozen.
- corpus/snippets contain planted defects on purpose. Never fix or lint them.
- corpus/truth is the answer key.
- harness/metrics.py overwrites runs/RESULTS.json in place, so new runs must use
  a separate root. After make verify, git status must show no modified files.
