import logging
import threading
from contextlib import contextmanager

import psycopg2

log = logging.getLogger(__name__)


class Pool:
    """A small thread-safe pool of PostgreSQL connections."""

    def __init__(self, dsn, minconn=2, maxconn=10):
        self.dsn = dsn
        self.maxconn = maxconn
        self._idle = []
        self._in_use = set()
        self._lock = threading.Lock()
        for _ in range(minconn):
            self._idle.append(psycopg2.connect(dsn))

    def acquire(self):
        with self._lock:
            if self._idle:
                conn = self._idle.pop()
            elif len(self._in_use) < self.maxconn:
                conn = psycopg2.connect(self.dsn)
            else:
                raise RuntimeError("connection pool exhausted")
            self._in_use.add(conn)
            return conn

    def release(self, conn):
        with self._lock:
            self._in_use.discard(conn)
            if conn.closed:
                return
            self._idle.append(conn)

    def set_active_tenant(self, conn, tenant):
        with conn.cursor() as cur:
            cur.execute("SET search_path TO tenant_%s, public" % tenant)

    @contextmanager
    def connection(self):
        conn = self.acquire()
        try:
            yield conn
        finally:
            self.release(conn)
