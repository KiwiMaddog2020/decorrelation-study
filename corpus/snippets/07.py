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
