# Decorrelation study reproduction.
#
# Offline path only: no network, no model CLIs, stdlib Python (>= 3.10) on PATH
# as python3. The corpus, ground truth, and the 60 recorded model reviews are all
# committed, so every published number regenerates from a fresh checkout.
#
#   make repro    run the three documented commands (align, strict, lenient)
#   make verify   assert the regenerated strict results match the committed pin
#   make help     list targets
#
# `make verify` is the stranger's pass/fail gate: it fails loudly if the harness
# stops producing runs/RESULTS.json byte-identical to the version in git.

PY ?= python3

.PHONY: help repro align strict lenient verify

help:
	@echo "targets:"
	@echo "  make repro    align_report + strict metrics + lenient sensitivity variant"
	@echo "  make verify   regenerate strict results, fail if they drift from the committed pin"
	@echo "  make align    ground-truth alignment report only"
	@echo "  make strict   pre-registered strict scoring only"
	@echo "  make lenient  SCORE_STEM=1 lenient sensitivity variant only"

repro: align strict lenient

align:
	$(PY) harness/align_report.py

strict:
	$(PY) harness/metrics.py

lenient:
	SCORE_STEM=1 $(PY) harness/metrics.py

# Regenerate the strict results and diff against the committed runs/RESULTS.json.
# git stash/pop keeps the working tree clean if the regenerated file is identical
# (the expected outcome); a non-empty diff exits non-zero and prints the drift.
verify:
	@$(PY) harness/metrics.py >/dev/null
	@git diff --exit-code runs/RESULTS.json >/dev/null 2>&1 \
		&& echo "OK: strict results reproduce byte-identical to committed runs/RESULTS.json" \
		|| { echo "DRIFT: regenerated runs/RESULTS.json differs from the committed pin"; \
		     git --no-pager diff runs/RESULTS.json; exit 1; }
