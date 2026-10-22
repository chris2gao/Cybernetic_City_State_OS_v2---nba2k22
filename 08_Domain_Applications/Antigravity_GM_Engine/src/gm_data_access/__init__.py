"""Bounded access to audited static SQLite snapshots; no game/process imports."""

QUERY_VERSION = "gm_sqlite_m0_v1"


class AccessError(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)
