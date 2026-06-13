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
