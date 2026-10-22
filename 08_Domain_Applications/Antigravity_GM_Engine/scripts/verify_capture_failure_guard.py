"""Ensure an unreadable player-pool slot cannot replace the previous table."""
from pathlib import Path
from contextlib import redirect_stdout
import io
import sqlite3
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import dump_player_pool as capture


class UnreadableMemory:
    pid = 0

    def read_bytes(self, address, size):
        return None


class ValidAnchor:
    def __init__(self, mem):
        pass

    def check_and_calibrate_player_pool(self):
        return True, 0x1000


def main():
    with tempfile.TemporaryDirectory(prefix="nba2k22_failure_guard_") as temp:
        path = Path(temp) / "pool.sqlite"
        conn = sqlite3.connect(path)
        try:
            capture.init_player_pool_schema(conn)
            conn.execute("INSERT INTO player_pool(slot_id,full_name) VALUES (99,'Existing Player')")
            conn.commit()
        finally:
            conn.close()
        with patch.object(capture, "AddressCalibrator", ValidAnchor), redirect_stdout(io.StringIO()):
            try:
                capture.dump_all_players_to_db(mem=UnreadableMemory(), total_slots=1, db_path=str(path))
            except RuntimeError as exc:
                if "Slot 0" not in str(exc):
                    raise
            else:
                raise AssertionError("Unreadable capture incorrectly reported success")
        conn = sqlite3.connect(path)
        try:
            if conn.execute("SELECT slot_id,full_name FROM player_pool").fetchall() != [(99, "Existing Player")]:
                raise AssertionError("Failed capture replaced the previous player pool")
        finally:
            conn.close()
    print("[PASS] Unreadable slot rejected; original player_pool preserved; game not opened.")


if __name__ == "__main__":
    main()
