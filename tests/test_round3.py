"""Round 3 tooling: prompt builder, ingest and analysis. Everything is written
under pytest's tmp_path; nothing is written inside the repo."""
from __future__ import annotations
import json, re

import pytest

from conftest import ROOT, load

IDS = [f"{i:02d}" for i in range(1, 21)]


@pytest.fixture(scope="module")
def bp():
    return load("round3/build_prompts.py")


@pytest.fixture(scope="module")
def ing():
    return load("round3/ingest.py")


@pytest.fixture
def an(monkeypatch):
    for var in ("SCORE_STEM", "SCORE_HEADERS", "SCORE_DESCRIBED"):
        monkeypatch.delenv(var, raising=False)
    return load("round3/analyze.py")


# ---- build_prompts ----------------------------------------------------------

def test_build_is_deterministic(bp, tmp_path):
    a = bp.build(tmp_path / "a")
    b = bp.build(tmp_path / "b")
    assert a == b
    for p in a["prompts"]:
        assert (tmp_path / "a" / p["prompt_path"]).read_text() == \
            (tmp_path / "b" / p["prompt_path"]).read_text()
    assert bp.build(tmp_path / "c", seed=7)["prompts"] != a["prompts"]


def test_partitions_cover_each_snippet_once_per_review(bp, tmp_path):
    m = bp.build(tmp_path)
    parts = {}
    for p in m["prompts"]:
        assert len(p["snippet_ids"]) == 5
        parts.setdefault(p["review"], []).append(frozenset(p["snippet_ids"]))
    for rev in (1, 2):
        ids = sorted(s for batch in parts[rev] for s in batch)
        assert ids == IDS
    assert set(parts[1]) != set(parts[2])


def test_manifest_lists_all_calls(bp, tmp_path):
    m = bp.build(tmp_path)
    assert len(m["calls"]) == 32
    assert {c["tier"] for c in m["calls"]} == {"haiku", "sonnet", "opus", "fable"}
    assert {c["requested_model"] for c in m["calls"]} == {
        "claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5", "claude-fable-5-2"}
    for c in m["calls"]:
        assert c["answer_path"] == f"raw/{c['tier']}__{c['call_id']}.txt"
        assert c["rater"] == f"{c['tier']}{c['call_id'][1]}"
        assert (tmp_path / c["prompt_path"]).exists()
    # same batches for every tier
    by_call = {}
    for c in m["calls"]:
        by_call.setdefault(c["call_id"], set()).add(tuple(c["snippet_ids"]))
    assert all(len(v) == 1 for v in by_call.values())


def test_prompt_content(bp, tmp_path):
    m = bp.build(tmp_path)
    instr = (ROOT / "protocol" / "review_prompt.txt").read_text().split("--- SNIPPET ---")[0]
    for p in m["prompts"]:
        text = (tmp_path / p["prompt_path"]).read_text()
        assert text.startswith(instr.rstrip("\n") + "\n")
        assert "--- SNIPPET ---" not in text and "{{SNIPPET}}" not in text
        assert "NO DEFECTS FOUND" in text and "Line numbers restart at 1" in text
        assert "do not use any tools" in text
        heads = re.findall(r"^=== SNIPPET (\d\d) ===$", text, re.M)
        assert heads == p["snippet_ids"]
        for sid in p["snippet_ids"]:
            code = (ROOT / "corpus" / "snippets" / f"{sid}.py").read_text()
            assert f"=== SNIPPET {sid} ===\n{code}" in text


ALWAYS = ["planted", "truth", "decorrelat", "answer key", "kiwimaddog", "github",
          "trutina", "corpus"]
# Words that can occur in ordinary code, so only checked outside the snippets.
OUTSIDE_CODE = ["round", "study", "experiment", "snippets/", ".py", ".json",
                "30 defects", "how many", "repository", "git"]


@pytest.mark.parametrize("word", ALWAYS + OUTSIDE_CODE)
def test_prompt_has_no_leaks(bp, tmp_path, word):
    m = bp.build(tmp_path)
    for p in m["prompts"]:
        text = (tmp_path / p["prompt_path"]).read_text().lower()
        if word not in ALWAYS:
            text = text.split("=== snippet", 1)[0]
        assert word not in text


# ---- ingest -----------------------------------------------------------------

def fake_run(bp, tmp_path, body=lambda tier, review, sid: "NO DEFECTS FOUND"):
    run = tmp_path / "run"
    m = bp.build(run)
    for c in m["calls"]:
        text = "".join(f"=== SNIPPET {sid} ===\n{body(c['tier'], c['review'], sid)}\n\n"
                       for sid in c["snippet_ids"])
        (run / c["answer_path"]).write_text(text)
    return run, m


def test_ingest_round_trip(bp, ing, tmp_path):
    def body(tier, review, sid):
        return f"line {int(sid)} | logic | {tier} review {review} on {sid}"
    run, m = fake_run(bp, tmp_path, body)
    dest = tmp_path / "dest"
    assert ing.main(["--run", str(run), "--dest", str(dest)]) == 0
    full = dest / "runs" / "full"
    for tier in ("haiku", "sonnet", "opus", "fable"):
        for rev in (1, 2):
            for sid in IDS:
                got = (full / f"{sid}.{tier}{rev}.txt").read_text()
                assert got == body(tier, rev, sid) + "\n"
    for sid in IDS:
        assert (full / f"{sid}.opus48_then.txt").read_text() == \
            (ROOT / "runs" / "full" / f"{sid}.claude.txt").read_text()
    assert len(list((dest / "raw").iterdir())) == 32
    assert json.loads((dest / "manifest.json").read_text()) == m
    # idempotent rerun
    assert ing.main(["--run", str(run), "--dest", str(dest)]) == 0


def test_ingest_tolerates_fences_preamble_and_markdown_headers(ing):
    text = ("Sure, here you go.\n```\n**=== SNIPPET 3 ===**\nNO DEFECTS FOUND.\n"
            "### === SNIPPET 07 ===\n\nline 2 | logic | bad\n```\n")
    sections, stray = ing.split_sections(text)
    assert [s for s, _ in sections] == ["03", "07"]
    assert sections[1][1] == "line 2 | logic | bad"
    assert stray == ["Sure, here you go."]


@pytest.mark.parametrize("mutate,expect", [
    (lambda t, ids: t.replace(f"=== SNIPPET {ids[0]} ===", "=== SNIPPET 99 ==="), "unexpected"),
    (lambda t, ids: t.replace(f"=== SNIPPET {ids[1]} ===", f"=== SNIPPET {ids[0]} ==="), "appears 2"),
    (lambda t, ids: t.split(f"=== SNIPPET {ids[-1]} ===")[0], "missing"),
    (lambda t, ids: t.replace("NO DEFECTS FOUND", "", 1), "empty section"),
    (lambda t, ids: t.replace("NO DEFECTS FOUND", "I think it looks fine.", 1), "neither"),
])
def test_ingest_detects_malformed(bp, ing, tmp_path, mutate, expect):
    run, m = fake_run(bp, tmp_path)
    c = m["calls"][0]
    p = run / c["answer_path"]
    p.write_text(mutate(p.read_text(), c["snippet_ids"]))
    writes, problems, _ = ing.plan(run, tmp_path / "dest")
    assert any(expect in x for x in problems), problems
    assert ing.main(["--run", str(run), "--dest", str(tmp_path / "dest")]) == 1
    assert not (tmp_path / "dest").exists()  # nothing written
    assert ing.main(["--run", str(run), "--dest", str(tmp_path / "dest"),
                     "--allow-partial"]) == 0
    assert (tmp_path / "dest" / "runs" / "full").exists()


def test_ingest_missing_answer_file(bp, ing, tmp_path):
    run, m = fake_run(bp, tmp_path)
    (run / m["calls"][5]["answer_path"]).unlink()
    _, problems, _ = ing.plan(run, tmp_path / "dest")
    assert any("missing answer file" in x for x in problems)


def test_ingest_refuses_overwrite(bp, ing, tmp_path):
    run, m = fake_run(bp, tmp_path)
    dest = tmp_path / "dest"
    assert ing.main(["--run", str(run), "--dest", str(dest)]) == 0
    target = dest / "runs" / "full" / f"{m['calls'][0]['snippet_ids'][0]}.haiku1.txt"
    target.write_text("line 1 | logic | edited by hand\n")
    assert ing.main(["--run", str(run), "--dest", str(dest)]) == 2
    assert target.read_text() == "line 1 | logic | edited by hand\n"


def test_ingest_default_dest_is_round3(ing):
    assert ing.HERE == ROOT / "round3"


# ---- analyze ----------------------------------------------------------------

SOURCE = {"haiku": "codex", "sonnet": "gemini", "opus": "claude", "fable": "codex"}


def fake_root(tmp_path, source=SOURCE, header=False):
    full = tmp_path / "r3" / "runs" / "full"
    full.mkdir(parents=True)
    for tier, src in source.items():
        for rev in (1, 2):
            for sid in IDS:
                text = (ROOT / "runs" / "full" / f"{sid}.{src}.txt").read_text()
                if header and rev == 2:
                    text = "LOCATION | TYPE | DESCRIPTION\n---|---|---\n" + text
                (full / f"{sid}.{tier}{rev}.txt").write_text(text)
    for sid in IDS:
        (full / f"{sid}.opus48_then.txt").write_text(
            (ROOT / "runs" / "full" / f"{sid}.claude.txt").read_text())
    return tmp_path / "r3"


def test_analyze_recovers_identical_same_tier_reviews(an, tmp_path):
    root = fake_root(tmp_path)
    res = an.run(root, boots=200, seed=1)
    assert (root / "RESULTS.json").exists() and (root / "RESULTS.md").exists()
    committed = json.loads((ROOT / "runs" / "RESULTS.json").read_text())
    for mode in ("original", "headers", "headers_described"):
        m = res["modes"][mode]
        s = m["summary"]
        assert s["same_tier"]["n_pairs"] == 4 and s["cross_tier"]["n_pairs"] == 24
        assert s["same_tier"]["mean_gain"] == 0
        assert s["same_tier"]["mean_phi"] == pytest.approx(1.0)
        assert s["cross_tier"]["mean_gain"] > 0
        assert m["gain_difference_cross_minus_same"] == pytest.approx(
            s["cross_tier"]["mean_gain"])
        assert len(m["four_tier_unions"]) == 16
        assert m["then_row"]["vs"]["opus1"]["phi"] == pytest.approx(1.0)
    m = res["modes"]["original"]
    # original mode reproduces the round 1 per-rater numbers
    assert m["raters"]["opus1"]["caught_ids"] == committed["caught"]["claude"]
    assert m["raters"]["sonnet2"]["caught_ids"] == committed["caught"]["gemini"]
    assert m["raters"]["sonnet2"]["false_positives_clean"] == committed["false_positives"]["gemini"]
    assert m["missed_by_every_round3_review"] == []
    md = (root / "RESULTS.md").read_text()
    assert "## Mode: headers (primary)" in md and "can and cannot support" in md
    assert "—" not in md


def test_analyze_header_mode_removes_echoed_headers(an, tmp_path):
    root = fake_root(tmp_path, header=True)
    res = an.run(root, boots=50, seed=1)
    orig, hdr = res["modes"]["original"]["raters"], res["modes"]["headers"]["raters"]
    assert orig["haiku2"]["false_positives_clean"] == orig["haiku1"]["false_positives_clean"] + 8
    assert hdr["haiku2"]["false_positives_clean"] == hdr["haiku1"]["false_positives_clean"]
    assert hdr["haiku2"]["caught_ids"] == hdr["haiku1"]["caught_ids"]


def test_analyze_bootstrap_is_seeded(an, tmp_path):
    root = fake_root(tmp_path)
    a = an.run(root, boots=100, seed=3)["modes"]["headers"]["bootstrap"]
    b = an.run(root, boots=100, seed=3)["modes"]["headers"]["bootstrap"]
    assert a == b


def test_analyze_partial_data(an, tmp_path):
    root = fake_root(tmp_path, source={"haiku": "codex", "opus": "claude"})
    (root / "runs" / "full" / "05.opus2.txt").unlink()
    res = an.run(root, boots=50, seed=1)
    assert res["incomplete_raters"] == {"opus2": ["05"]}
    m = res["modes"]["headers"]
    assert m["summary"]["same_tier"]["n_pairs"] == 2
    assert m["summary"]["cross_tier"]["n_pairs"] == 4
    assert m["four_tier_unions"] == []


@pytest.mark.parametrize("d,ci,want", [
    (1.5, [0.2, 2.9], "tiers cover each other"),
    (0.3, [-0.8, 1.4], "a second look is just as good"),
    (1.5, [-0.1, 3.0], "inconclusive at this sample size"),
    (0.8, [-0.5, 2.5], "inconclusive at this sample size"),
])
def test_decision_rule(an, d, ci, want):
    assert an.verdict(d, ci) == want
