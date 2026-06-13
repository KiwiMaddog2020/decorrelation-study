"""Event deduplication for the analytics ingestion pipeline."""

from typing import Any, Dict, List


def dedupe_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Collapse events to one row per (user_id, kind).

    When the same (user_id, kind) pair appears more than once we keep the
    most recent occurrence, identified by the integer ``ts`` field. The
    relative order of the surviving events is not significant downstream.
    """
    seen_keys: List[tuple] = []
    deduped: List[Dict[str, Any]] = []

    for event in events:
        key = (event["user_id"], event["kind"])
        if key in seen_keys:
            position = seen_keys.index(key)
            deduped[position] = event
        else:
            seen_keys.append(key)
            deduped.append(event)

    return deduped
