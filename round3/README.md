# Round 3: Claude tiers

Do different Claude tiers cover each other's blind spots, or is a second look
from the same model just as good? The plan is in
[PRE_REGISTRATION_R3.md](PRE_REGISTRATION_R3.md).

## Reproduce, in order

```bash
python3 round3/build_prompts.py --out RUN_DIR     # prompts and call manifest
#   run each call in RUN_DIR/manifest.json in a fresh session and save the
#   reply verbatim to RUN_DIR/<answer_path>
python3 round3/ingest.py --run RUN_DIR            # split into round3/runs/full
python3 round3/analyze.py                         # round3/RESULTS.json and RESULTS.md
```

`RUN_DIR` is any folder outside the repo. Paths in the manifest are relative to
it. `ingest.py` stops on missing or malformed sections (add `--allow-partial` to
keep the valid ones) and never overwrites a file with different content.
