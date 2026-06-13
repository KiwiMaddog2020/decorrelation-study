import os


class PathTraversalError(ValueError):
    """Raised when a joined path would escape the configured base directory."""


def safe_join(base, *parts):
    """Join ``parts`` beneath ``base`` and reject any result that escapes it.

    The returned path is always an absolute, normalized path located inside
    ``base``. Attempts to traverse outside the base (via ``..`` segments,
    absolute components, or symlink-free trickery) raise PathTraversalError.
    """
    base_root = os.path.abspath(base)

    candidate = os.path.abspath(os.path.join(base_root, *parts))

    # Compare against the base with a trailing separator so that a sibling
    # directory sharing a name prefix (e.g. "/srv/data-evil" vs "/srv/data")
    # is not mistaken for a path inside the base.
    base_prefix = base_root
    if not base_prefix.endswith(os.sep):
        base_prefix += os.sep

    if candidate != base_root and not candidate.startswith(base_prefix):
        raise PathTraversalError(
            "refusing to access {!r}: outside base {!r}".format(candidate, base_root)
        )

    return candidate
