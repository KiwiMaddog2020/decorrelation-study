"""Unicode-aware string truncation helpers."""

import unicodedata


def truncate(s, n):
    """Return s shortened to at most n user-perceived characters.

    A user-perceived character (grapheme) may span several code points,
    e.g. a base letter followed by combining marks, or a sequence joined
    by a zero-width joiner. We never cut in the middle of such a cluster:
    if including a cluster would push the count past n, we stop before it.

    Out of scope: emoji modifiers (skin-tone selectors), regional-indicator
    flags, variation selectors, and enclosing keycaps are treated as their
    own code points rather than merged into the preceding cluster.
    """
    if n <= 0:
        return ""

    clusters = []
    for ch in s:
        # A combining mark (or zero-width joiner) attaches to the cluster
        # that precedes it rather than starting a new one.
        if clusters and (unicodedata.combining(ch) or ch == "‍"):
            clusters[-1] += ch
        elif clusters and clusters[-1].endswith("‍"):
            clusters[-1] += ch
        else:
            clusters.append(ch)

    if len(clusters) <= n:
        return s
    return "".join(clusters[:n])
