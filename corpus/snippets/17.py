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
