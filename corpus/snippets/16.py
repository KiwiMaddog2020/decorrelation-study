"""Grouping helpers for aggregating records before display."""

from collections import OrderedDict


def group_by(items, key):
    """Group ``items`` into an OrderedDict mapping ``key(item)`` to a list.

    Keys appear in first-seen order, and within each group the items keep
    their original relative order. Every input item lands in exactly one
    group. The input iterable is consumed once and never mutated.
    """
    groups = OrderedDict()
    for item in items:
        k = key(item)
        if k not in groups:
            groups[k] = []
        groups[k].append(item)
    return groups
