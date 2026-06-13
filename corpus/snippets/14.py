import hashlib
import json

from .errors import IdempotencyError


def idempotency_key(request):
    """Derive a stable key so a retried request is not processed twice.

    The client may supply an explicit Idempotency-Key header; otherwise we
    fall back to a deterministic fingerprint of the request so that an
    accidental retry of the same operation maps to the same stored result.
    """
    explicit = request.headers.get("Idempotency-Key")
    if explicit:
        explicit = explicit.strip()
        if len(explicit) < 8 or len(explicit) > 255:
            raise IdempotencyError("Idempotency-Key must be 8-255 characters")
        return explicit

    fingerprint = {
        "method": request.method.upper(),
        "path": request.path,
        "body": request.get_json(silent=True) or {},
    }
    canonical = json.dumps(fingerprint, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return "auto-" + digest
