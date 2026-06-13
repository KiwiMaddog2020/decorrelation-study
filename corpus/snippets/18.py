"""Configuration merge helpers used to layer overrides over defaults."""

from copy import deepcopy


def deep_merge(a, b):
    """Return a new dict that deep-merges ``b`` over ``a``.

    Where both ``a`` and ``b`` have a dict at the same key, the values are
    merged recursively. For any other conflict ``b`` wins. Neither input is
    mutated; the result is built from fresh copies.
    """
    result = deepcopy(a)
    for key, b_value in b.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(b_value, dict)
        ):
            result[key] = deep_merge(result[key], b_value)
        else:
            result[key] = deepcopy(b_value)
    return result
