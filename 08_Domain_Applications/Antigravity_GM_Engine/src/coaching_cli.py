"""File handling for the local coaching interface. Importing this never opens a process."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def export_path(value):
    path=Path(value).resolve()
    if not path.is_relative_to((ROOT/"_exports").resolve()):
        raise ValueError("LOCAL_EXPORTS_PATH_REQUIRED")
    return path

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write_json(path,data):
    path=export_path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
