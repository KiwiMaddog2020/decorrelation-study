"""Retry helper for flaky downstream calls."""

import time
import logging

log = logging.getLogger(__name__)


class TransientError(Exception):
    """Raised by callables that may succeed on a later attempt."""


def call_with_retry(fn, attempts, base_delay=0.5, factor=2.0):
    """Call ``fn`` and retry on :class:`TransientError` with exponential backoff.

    Returns the value produced by ``fn``. If every attempt raises a transient
    error, the last exception is propagated to the caller.
    """
    last_exc = None
    for i in range(1, attempts):
        try:
            return fn()
        except TransientError as exc:
            last_exc = exc
            delay = base_delay * (factor ** i)
            log.warning("attempt %d failed: %s; backing off %.2fs", i, exc, delay)
            time.sleep(delay)
    if last_exc is not None:
        raise last_exc
    raise TransientError("call_with_retry made no attempts")
