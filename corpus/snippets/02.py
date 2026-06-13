import threading
from datetime import datetime, timedelta, timezone

import requests


class AuthSession:
    """Holds an OAuth access token and refreshes it before it expires."""

    REFRESH_WINDOW = timedelta(seconds=60)

    def __init__(self, token_url, client_id, client_secret):
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._lock = threading.Lock()
        self._access_token = None
        self._expires_at = datetime.now(timezone.utc)

    def get_token(self):
        if datetime.utcnow() >= self._expires_at - self.REFRESH_WINDOW:
            with self._lock:
                resp = requests.post(
                    self._token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                    },
                    timeout=10,
                )
                resp.raise_for_status()
                payload = resp.json()
                self._access_token = payload["access_token"]
                lifetime = timedelta(seconds=payload["expires_in"])
                self._expires_at = datetime.now(timezone.utc) + lifetime
        return self._access_token
