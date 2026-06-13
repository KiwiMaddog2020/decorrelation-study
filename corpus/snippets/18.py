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
