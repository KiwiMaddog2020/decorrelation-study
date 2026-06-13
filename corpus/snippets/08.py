from bisect import bisect_left
from typing import Optional


def page(items, cursor, size):
    """Return one keyset page of ``items`` plus the cursor for the next page.

    ``items`` is assumed sorted ascending. ``cursor`` is the id of the last
    item the caller already received and is treated as *exclusive*: the page
    returned starts strictly after it. Pass ``cursor=None`` for the first page.

    Returns ``(slice, next_cursor)`` where ``next_cursor`` is ``None`` once the
    final page has been served.
    """
    ids = [it["id"] for it in items]

    if cursor is None:
        start = 0
    else:
        start = bisect_left(ids, cursor)

    window = items[start:start + size]

    if start + size >= len(items):
        next_cursor = None
    else:
        next_cursor = window[-1]["id"] if window else None

    return window, next_cursor
