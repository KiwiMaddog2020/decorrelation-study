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
