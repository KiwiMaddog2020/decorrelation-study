# Human review packet (blind)

You are the human rater (the most decorrelated family). Review each snippet below for genuine defects. Do NOT open corpus/truth — you are blind to the answer key by design.

## Instructions

```
You are reviewing a single, self-contained code snippet for defects.

Report every defect you find. For each one, give exactly:
- LOCATION: the line number or the function/expression where the defect lives.
- TYPE: one of [logic, security, concurrency, boundary, api-misuse, performance, spec-violation, other].
- DESCRIPTION: one sentence stating what is actually wrong and why it matters.

Rules:
- Report defects only. Do NOT rewrite or fix the code.
- If you find no defects, respond with exactly: NO DEFECTS FOUND.
- Judge only the snippet as given. Do not assume callers sanitize inputs unless the snippet shows it.
- Do not pad the list with style nitpicks; report genuine defects (correctness, security, resource, contract).

Output one defect per line in the form:
LOCATION | TYPE | DESCRIPTION
```

For each snippet write one defect per line as `LOCATION | TYPE | DESCRIPTION`, or `NO DEFECTS FOUND`. TYPE is one of: logic, security, concurrency, boundary, api-misuse, performance, spec-violation, other. Fill the answer block under each snippet (or just send me your findings per snippet).

---

## Snippet 01

```python
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
```

**Findings (01):**

```


```

---

## Snippet 02

```python
import threading
from datetime import datetime, timedelta, timezone

import requests


class AuthSession:
    """Holds an OAuth access token and refreshes it before it expires."""

    REFRESH_WINDOW = timedelta(seconds=60)

    def __init__(self, token_url, client_id, client_secret):
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._lock = threading.Lock()
        self._access_token = None
        self._expires_at = datetime.now(timezone.utc)

    def get_token(self):
        if datetime.utcnow() >= self._expires_at - self.REFRESH_WINDOW:
            with self._lock:
                resp = requests.post(
                    self._token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                    },
                    timeout=10,
                )
                resp.raise_for_status()
                payload = resp.json()
                self._access_token = payload["access_token"]
                lifetime = timedelta(seconds=payload["expires_in"])
                self._expires_at = datetime.now(timezone.utc) + lifetime
        return self._access_token
```

**Findings (02):**

```


```

---

## Snippet 04

```python
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
```

**Findings (04):**

```


```

---

## Snippet 06

```python
"""Money helpers for the checkout pipeline.

All amounts are integer cents to avoid floating-point drift in
ledgers. Tax is applied per line so that downstream rounding matches
what the customer sees on the printed receipt.
"""

from decimal import Decimal, ROUND_HALF_UP


def line_total(qty: int, unit_cents: int, tax_rate: Decimal) -> int:
    """Return the line total in integer cents, tax included.

    The pre-tax subtotal is always an exact integer number of cents, so
    only the tax component needs rounding. We use bankers rounding
    (round half to even) on the final cent to stay consistent with the
    accounting system's half-to-even convention and keep large batches
    statistically balanced.

    Args:
        qty: number of units ordered.
        unit_cents: price per unit, in whole cents.
        tax_rate: fractional tax rate, e.g. Decimal("0.08875").

    Returns:
        Total cents (subtotal plus tax) as an int.
    """
    subtotal = qty * unit_cents
    tax = Decimal(subtotal) * tax_rate
    taxed_total = Decimal(subtotal) + tax
    return int(taxed_total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

**Findings (06):**

```


```

---

## Snippet 07

```python
"""A small in-process LRU cache used by the metadata resolver layer."""

from collections import OrderedDict
from typing import Any, Hashable, Optional


class LRUCache:
    """Fixed-capacity cache that evicts the least-recently-used entry."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._store: "OrderedDict[Hashable, Any]" = OrderedDict()

    def get(self, key: Hashable) -> Optional[Any]:
        """Return the value for key, or None if it is not cached."""
        if key not in self._store:
            return None
        return self._store[key]

    def put(self, key: Hashable, value: Any) -> None:
        """Insert or update key, evicting the oldest entry on overflow."""
        if key in self._store:
            # Refresh position so an updated key counts as recently touched.
            self._store.move_to_end(key)
        self._store[key] = value
        if len(self._store) > self.capacity:
            evicted_key, _ = self._store.popitem(last=False)
            self._on_evict(evicted_key)

    def _on_evict(self, key: Hashable) -> None:
        """Hook for subclasses to observe evictions; no-op by default."""

    def __len__(self) -> int:
        return len(self._store)
```

**Findings (07):**

```


```

---

## Snippet 09

```python
import time
import threading


class RateLimiter:
    """Token-bucket rate limiter.

    Tokens accrue at ``rate`` per second up to ``capacity`` and each
    ``allow()`` consumes one token. Calls beyond the available token
    budget are rejected so callers can shed or retry load.
    """

    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self._last = time.time()
        self._lock = threading.Lock()

    def _refill(self):
        now = time.time()
        elapsed = now - self._last
        minted = int(elapsed * self.rate)
        if minted > 0:
            self.tokens = min(self.capacity, self.tokens + minted)
            self._last = now

    def allow(self):
        """Return True if a token is available and consume it."""
        with self._lock:
            self._refill()
            available = self.tokens

        if available >= 1:
            self.tokens -= 1
            return True
        return False
```

**Findings (09):**

```


```

---

## Snippet 11

```python
import logging
import threading
from contextlib import contextmanager

import psycopg2

log = logging.getLogger(__name__)


class Pool:
    """A small thread-safe pool of PostgreSQL connections."""

    def __init__(self, dsn, minconn=2, maxconn=10):
        self.dsn = dsn
        self.maxconn = maxconn
        self._idle = []
        self._in_use = set()
        self._lock = threading.Lock()
        for _ in range(minconn):
            self._idle.append(psycopg2.connect(dsn))

    def acquire(self):
        with self._lock:
            if self._idle:
                conn = self._idle.pop()
            elif len(self._in_use) < self.maxconn:
                conn = psycopg2.connect(self.dsn)
            else:
                raise RuntimeError("connection pool exhausted")
            self._in_use.add(conn)
            return conn

    def release(self, conn):
        with self._lock:
            self._in_use.discard(conn)
            if conn.closed:
                return
            self._idle.append(conn)

    def set_active_tenant(self, conn, tenant):
        with conn.cursor() as cur:
            cur.execute("SET search_path TO tenant_%s, public" % tenant)

    @contextmanager
    def connection(self):
        conn = self.acquire()
        try:
            yield conn
        finally:
            self.release(conn)
```

**Findings (11):**

```


```

---

## Snippet 13

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class User:
    username: str
    roles: List[str] = field(default_factory=list)


@dataclass
class Resource:
    owner: str
    required_role: str


def can_access(user, resource):
    """Decide whether ``user`` may access ``resource``.

    Owners always have access to their own resources. Otherwise the user must
    hold the role required by the resource. A user with the ``admin`` role may
    access any resource.
    """
    if resource.owner == user.username:
        return True

    granted = " ".join(user.roles)

    if "admin" in granted:
        return True

    return resource.required_role in granted
```

**Findings (13):**

```


```

---

## Snippet 15

```python
"""Currency conversion helpers for the billing pipeline."""

from decimal import Decimal, ROUND_HALF_UP

MINOR_UNIT_QUANTUM = Decimal("1")


def convert_all(amounts, get_rate):
    """Convert a list of amounts to integer minor units in the target currency.

    Each amount is converted at its source currency's rate, then rounded to
    whole minor units (cents). Returns a list of ints aligned with ``amounts``.
    """
    results = []
    for amount in amounts:
        value = Decimal(str(amount["value"]))
        currency = amount["currency"]
        rate = Decimal(str(get_rate(currency)))
        minor = (value * Decimal(100)).quantize(
            MINOR_UNIT_QUANTUM, rounding=ROUND_HALF_UP
        )
        converted = (minor * rate).quantize(
            MINOR_UNIT_QUANTUM, rounding=ROUND_HALF_UP
        )
        results.append(int(converted))
    return results
```

**Findings (15):**

```


```

---

## Snippet 17

```python
"""Utilities for splitting sequences into fixed-size batches."""

from itertools import islice
from typing import Iterable, Iterator, List, Sequence, TypeVar

T = TypeVar("T")


def chunks(seq: Sequence[T], size: int) -> Iterator[List[T]]:
    """Yield successive ``size``-length chunks from ``seq``.

    The final chunk may contain fewer than ``size`` elements when
    ``len(seq)`` is not an exact multiple of ``size``. ``size`` must be a
    positive integer.

    >>> list(chunks([1, 2, 3, 4, 5], 2))
    [[1, 2], [3, 4], [5]]
    """
    if size < 1:
        raise ValueError("size must be at least 1")

    for start in range(0, len(seq), size):
        yield list(seq[start:start + size])


def ichunks(iterable: Iterable[T], size: int) -> Iterator[List[T]]:
    """Like :func:`chunks` but accepts any iterable, consuming it lazily."""
    if size < 1:
        raise ValueError("size must be at least 1")

    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            return
        yield batch
```

**Findings (17):**

```


```

---

## Snippet 18

```python
"""Configuration merge helpers used to layer overrides over defaults."""

from copy import deepcopy


def deep_merge(a, b):
    """Return a new dict that deep-merges ``b`` over ``a``.

    Where both ``a`` and ``b`` have a dict at the same key, the values are
    merged recursively. For any other conflict ``b`` wins. Neither input is
    mutated; the result is built from fresh copies.
    """
    result = {}
    for key, a_value in a.items():
        if key in b and isinstance(a_value, dict) and isinstance(b[key], dict):
            result[key] = deep_merge(a_value, b[key])
        elif key in b:
            result[key] = deepcopy(b[key])
        else:
            result[key] = deepcopy(a_value)
    for key, b_value in b.items():
        if key not in a:
            result[key] = deepcopy(b_value)
    return result
```

**Findings (18):**

```


```

---

## Snippet 19

```python
"""Utilities for ordering directory records for display."""

from typing import List, Mapping, Sequence


def sort_people(people: Sequence[Mapping[str, str]]) -> List[Mapping[str, str]]:
    """Return people stably sorted by (last_name, first_name).

    Comparison is case-insensitive on both keys. The input is not mutated;
    a new list is returned. Records that compare equal retain their original
    relative order.
    """

    def sort_key(person: Mapping[str, str]):
        last = person.get("last_name", "")
        first = person.get("first_name", "")
        return (last.casefold(), first.casefold())

    return sorted(people, key=sort_key)
```

**Findings (19):**

```


```
