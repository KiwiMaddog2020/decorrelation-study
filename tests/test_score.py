"""Scorer: default behaviour is the pre-registered one; the two stricter modes
are opt-in by argument or by environment variable."""
from __future__ import annotations
import json

import pytest

from conftest import ROOT, load


@pytest.fixture
def score(monkeypatch):
    for var in ("SCORE_STEM", "SCORE_HEADERS", "SCORE_DESCRIBED"):
        monkeypatch.delenv(var, raising=False)
    return load("harness/score.py")


HEADER_TEXT = """LOCATION | TYPE | DESCRIPTION
---|---|---
| --- | --- | --- |
Note: the answer uses a | b style notation | in prose
line 12 | logic | the loop skips the last element
"""


# ---- bug (a): parse_flags treats any piped line as a flag -------------------

def test_default_parse_keeps_header_rows(score):
    flags = score.parse_flags(HEADER_TEXT)
    # Old behaviour preserved: header, both separators and the prose row count.
    assert len(flags) == 5
    assert flags[0]["type"] == "type"


def test_header_filter_by_argument(score):
    flags = score.parse_flags(HEADER_TEXT, filter_headers=True)
    assert [f["type"] for f in flags] == ["logic"]
    assert flags[0]["lines"] == {12}


def test_header_filter_by_env(monkeypatch):
    monkeypatch.setenv("SCORE_HEADERS", "1")
    monkeypatch.delenv("SCORE_DESCRIBED", raising=False)
    sc = load("harness/score.py")
    assert len(sc.parse_flags(HEADER_TEXT)) == 1
    # explicit argument beats the environment
    assert len(sc.parse_flags(HEADER_TEXT, filter_headers=False)) == 5


@pytest.mark.parametrize("row,typ", [
    ("line 3 | **Logic** | wrong branch taken", "**logic**"),
    ("line 3 | `security` | injection", "`security`"),
    ("| line 3 | api-misuse | wrong call |", "api-misuse"),
    ("LOCATION: line 3 | TYPE: boundary | off by one", "type: boundary"),
    ("line 3 | SPEC-VIOLATION | contract broken", "spec-violation"),
    ("line 3 | other | something | with a pipe", "other"),
])
def test_header_filter_tolerates_markdown_and_case(score, row, typ):
    flags = score.parse_flags(row, filter_headers=True)
    assert len(flags) == 1
    assert flags[0]["type"] == typ
    assert 3 in flags[0]["lines"]


@pytest.mark.parametrize("row", [
    "LOCATION | TYPE | DESCRIPTION",
    "**Location** | **Type** | **Description**",
    "|:---|:---:|---:|",
    "see below | contract | prose row with no line number and no allowed type",
    "line 4 | logic",
    "a | b",
])
def test_header_filter_drops_non_flags(score, row):
    assert score.parse_flags(row, filter_headers=True) == []


def test_header_filter_keeps_a_real_flag_with_an_off_list_type(score):
    # A sloppy label on a row that still points at a line is a real flag; dropping
    # it would under-count false positives on clean snippets.
    flags = score.parse_flags("line 4 | contract | breaks the stated contract", filter_headers=True)
    assert [f["lines"] for f in flags] == [{4}]


def test_parse_edge_cases(score):
    assert score.parse_flags("") == []
    assert score.parse_flags("NO DEFECTS FOUND") == []
    assert score.parse_flags("NO DEFECTS FOUND", filter_headers=True) == []
    f = score.parse_flags("lines 18-20 (fn) | logic | x | y")[0]
    assert f["lines"] == {18, 20}
    assert f["desc"] == "x|y"  # extra pipes stay in the description, as before
    assert score.parse_flags("fn | logic | no line number")[0]["lines"] == set()


def test_normalize_type(score):
    assert score.normalize_type(" **`Api-Misuse`** ") == "api-misuse"
    assert score.normalize_type("Type: logic") == "logic"
    assert score.normalize_type("TYPE") == "type"


def test_header_filter_on_clean_snippet_removes_false_positive(score, tmp_path):
    (tmp_path / "16.claude.txt").write_text(
        "LOCATION | TYPE | DESCRIPTION\n---|---|---\nNO DEFECTS FOUND\n")
    old = score.score_snippet("16", tmp_path)["raters"]["claude"]
    new = score.score_snippet("16", tmp_path, filter_headers=True)["raters"]["claude"]
    assert len(old["candidates"]) == 2
    assert new["candidates"] == []


# ---- bug (b): any flag within one line of a defect is credited --------------

DEFECTS = [
    {"id": "x-d1", "lines": [10], "type": "performance", "subtype": "quadratic",
     "canonical": "list membership scan makes dedupe quadratic"},
    {"id": "x-d2", "lines": [40], "type": "security", "subtype": "injection",
     "canonical": "user string reaches shell command unescaped"},
]


def flag(score, row):
    return score.parse_flags(row)[0]


def test_default_match_credits_unrelated_nearby_flag(score):
    f = flag(score, "line 11 | concurrency | thread race on shared counter")
    assert score.match(f, DEFECTS) == "x-d1"


def test_described_match_rejects_unrelated_nearby_flag(score):
    f = flag(score, "line 11 | concurrency | thread race on shared counter")
    assert score.match(f, DEFECTS, described=True) is None


def test_described_match_keeps_related_flag(score):
    by_type = flag(score, "line 10 | performance | slow")
    by_word = flag(score, "line 9 | logic | membership test walks the list")
    assert score.match(by_type, DEFECTS, described=True) == "x-d1"
    assert score.match(by_word, DEFECTS, described=True) == "x-d1"


def test_described_falls_through_to_content_matcher(score):
    # Near d1 by line, but it describes d2 in words: content matcher picks d2.
    f = flag(score, "line 10 | other | user string reaches shell command")
    assert score.match(f, DEFECTS) == "x-d1"
    assert score.match(f, DEFECTS, described=True) == "x-d2"


def test_described_by_env(monkeypatch):
    monkeypatch.setenv("SCORE_DESCRIBED", "1")
    monkeypatch.delenv("SCORE_HEADERS", raising=False)
    sc = load("harness/score.py")
    f = sc.parse_flags("line 11 | concurrency | thread race on shared counter")[0]
    assert sc.match(f, DEFECTS) is None
    assert sc.match(f, DEFECTS, described=False) == "x-d1"


def test_score_snippet_raters_argument(score, tmp_path):
    (tmp_path / "16.alpha.txt").write_text("NO DEFECTS FOUND\n")
    (tmp_path / "16.claude.txt").write_text("NO DEFECTS FOUND\n")
    res = score.score_snippet("16", tmp_path, raters=["alpha"])
    assert list(res["raters"]) == ["alpha"]


# ---- the published numbers still reproduce ----------------------------------

def _metrics(monkeypatch):
    for var in ("SCORE_STEM", "SCORE_HEADERS", "SCORE_DESCRIBED"):
        monkeypatch.delenv(var, raising=False)
    return load("harness/metrics.py")


def test_default_scoring_matches_committed_results(monkeypatch):
    m = _metrics(monkeypatch)
    text = json.dumps(m.payload(m.compute()), indent=2) + "\n"
    assert text == (ROOT / "runs" / "RESULTS.json").read_text()


def test_results_file_name_per_mode(monkeypatch):
    m = _metrics(monkeypatch)
    assert m.out_name() == "RESULTS.json"
    assert m.out_name(stem=True) == "RESULTS_lenient.json"
    assert m.out_name(headers=True) == "RESULTS_headers.json"
    assert m.out_name(described=True) == "RESULTS_described.json"
    assert m.out_name(headers=True, described=True) == "RESULTS_headers_described.json"
    monkeypatch.setenv("SCORE_HEADERS", "1")
    assert load("harness/metrics.py").out_name() == "RESULTS_headers.json"


def test_header_mode_only_drops_rows_on_committed_reviews(monkeypatch):
    """The header filter fixes parsing without changing matching: on the
    committed reviews no catch changes, only non-flag rows disappear."""
    m = _metrics(monkeypatch)
    base = m.compute()
    hdr = m.compute(filter_headers=True)
    assert hdr["caught"] == base["caught"]
    assert all(hdr["fp"][r] <= base["fp"][r] for r in base["raters"])
