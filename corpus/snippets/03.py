import threading
from collections import deque


class QueueFull(Exception):
    """Raised when an item cannot be enqueued because the buffer is full."""


class BoundedBuffer:
    """A thread-safe FIFO buffer that holds at most ``capacity`` items.

    Producers call :meth:`put` to enqueue work; consumers call :meth:`get`
    to drain it. A condition variable lets consumers block until an item is
    available instead of busy-waiting.
    """

    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._items = deque()
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)

    def put(self, item):
        """Append ``item`` to the buffer.

        Raises :class:`QueueFull` if the buffer is already at capacity so
        the caller can apply backpressure rather than growing unbounded.
        """
        with self._lock:
            if len(self._items) >= self._capacity:
                raise QueueFull("buffer at capacity")
        self._items.append(item)
        with self._not_empty:
            self._not_empty.notify()

    def get(self, timeout=None):
        with self._not_empty:
            while not self._items:
                if not self._not_empty.wait(timeout):
                    raise TimeoutError("no item available")
            return self._items.popleft()

    def __len__(self):
        with self._lock:
            return len(self._items)
