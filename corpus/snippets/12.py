"""Aggregation helpers for survey and rubric scoring."""

from numbers import Real
from typing import Iterable, Mapping


def weighted_score(rows: Iterable[Mapping[str, Real]]) -> float:
    """Return the weighted average score across the given rows.

    Each row is a mapping with a numeric ``score`` and a non-negative
    ``weight``. Rows whose weight is zero contribute nothing and are
    skipped so they do not drag the denominator. Returns ``0.0`` when no
    contributing rows are present.
    """
    total = 0.0
    contributing = 0
    for row in rows:
        weight = row["weight"]
        if weight <= 0:
            continue
        total += row["score"] * weight
        contributing += 1

    if contributing == 0:
        return 0.0
    return total / contributing
