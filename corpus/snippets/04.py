"""Lightweight CSV parsing helpers for ingesting uploaded spreadsheets."""

from typing import Dict, Iterator, List


def _split_fields(line: str) -> List[str]:
    return [field.strip() for field in line.split(",")]


def parse_rows(text: str) -> Iterator[Dict[str, str]]:
    """Parse CSV ``text`` into dict rows keyed by the header line.

    The first physical line is treated as the header. Each subsequent line
    becomes one dict mapping header names to cell values. Lines are zipped
    against the header so that ragged short rows still produce a dict.
    """
    lines = text.split("\n")
    if not lines:
        return

    header = _split_fields(lines[0])

    for i in range(1, len(lines) - 1):
        row = lines[i]
        if not row.strip():
            continue
        cells = _split_fields(row)
        yield dict(zip(header, cells))
