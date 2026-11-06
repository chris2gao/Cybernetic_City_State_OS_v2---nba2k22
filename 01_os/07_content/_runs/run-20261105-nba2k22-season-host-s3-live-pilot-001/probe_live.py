"""Read the live process identity and game calendar without changing the game."""
import ctypes
import hashlib
import json
import sys
import time
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype"))
from live_reader import ReadOnlyGameProcess
from refresh import _context
from schedule_reader import collect_schedule


def main():
    pid = int(sys.argv[1])
    started = time.perf_counter()
    result = {"pid": pid, "admin": bool(ctypes.windll.shell32.IsUserAnAdmin())}
    reader = None
    try:
        reader = ReadOnlyGameProcess(pid)
        size = wintypes.DWORD(32768)
        image = ctypes.create_unicode_buffer(size.value)
        if not reader.k.QueryFullProcessImageNameW(reader.handle, 0, image, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        result.update(image=image.value, creation_filetime=reader.creation_filetime)
        with open(image.value, "rb") as binary:
            result["image_sha256"] = hashlib.file_digest(binary, "sha256").hexdigest()
        schedule = collect_schedule(reader, with_calendar=True, read_final_boxes=False)
        context = _context(pid)
        if context["epoch"]["creation_filetime"] != reader.creation_filetime:
            raise RuntimeError("Process epoch changed during L0")
        entries = schedule["manifest"]["entries"]
        finals = [entry for entry in entries if entry.get("status") == 2 and entry.get("record_shape_valid")]
        underway = [entry for entry in entries if entry.get("status") == 1 and entry.get("record_shape_valid")]
        result.update(calendar=schedule.get("calendar"), process_epoch=context["epoch"],
                      game_mode_progress=context["game_progress"], final_game_count=len(finals),
                      in_progress_count=len(underway), status="LIVE_READ")
    except Exception as exc:
        result.update(status="FAILED", error=repr(exc), winerror=getattr(exc, "winerror", None),
                      trace=getattr(exc, "read_trace", None))
    finally:
        if reader:
            reader.close()
        result["wall_seconds"] = time.perf_counter() - started
    Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "LIVE_READ" else 1


if __name__ == "__main__":
    raise SystemExit(main())
