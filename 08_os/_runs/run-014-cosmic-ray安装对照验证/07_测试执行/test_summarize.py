from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[4]
SUMMARY_PATH = REPO_ROOT / "08_os/06_execution/tools/cosmic_ray/summarize.py"
SPEC = importlib.util.spec_from_file_location("cosmic_ray_summary", SUMMARY_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load Cosmic Ray summary helper")
SUMMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUMMARY)


def work_item(occurrence: int = 0) -> dict[str, object]:
    return {
        "job_id": "random-job-id-must-not-survive",
        "mutations": [
            {
                "module_path": "target/example.py",
                "operator_name": "core/Fake",
                "occurrence": occurrence,
                "start_pos": [1, 1],
                "end_pos": [1, 2],
                "operator_args": {},
                "definition_name": "example",
            }
        ],
    }


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        (None, "incomplete"),
        (
            {
                "worker_outcome": "normal",
                "test_outcome": "killed",
                "output": "timeout",
            },
            "timeout",
        ),
        (
            {
                "worker_outcome": "exception",
                "test_outcome": "incompetent",
                "output": "boom",
            },
            "worker_exception",
        ),
        (
            {
                "worker_outcome": "normal",
                "test_outcome": "survived",
                "output": "ok",
            },
            "survived",
        ),
    ],
)
def test_semantic_outcome(result: dict[str, object] | None, expected: str) -> None:
    assert SUMMARY.semantic_outcome(result) == expected


def test_summary_removes_job_ids_and_is_stable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dump = tmp_path / "session.jsonl"
    output = tmp_path / "summary.json"
    rows = [
        [
            work_item(1),
            {
                "worker_outcome": "normal",
                "test_outcome": "killed",
                "output": "timeout",
                "diff": "second",
            },
        ],
        [
            work_item(0),
            {
                "worker_outcome": "normal",
                "test_outcome": "killed",
                "output": "failure",
                "diff": "first",
            },
        ],
    ]
    dump.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", ["summarize.py", str(dump), str(output)])
    assert SUMMARY.main() == 0
    summary = json.loads(output.read_text(encoding="utf-8"))
    assert summary["semantic_outcome_counts"] == {"killed": 1, "timeout": 1}
    assert summary["fail_closed"] is True
    assert [item["occurrence"] for item in summary["objects"]] == [0, 1]
    assert "random-job-id-must-not-survive" not in output.read_text(encoding="utf-8")


def test_invalid_work_item_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dump = tmp_path / "invalid.jsonl"
    output = tmp_path / "summary.json"
    dump.write_text(json.dumps([{"mutations": []}, None]) + "\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["summarize.py", str(dump), str(output)])
    with pytest.raises(ValueError, match="expected one mutation"):
        SUMMARY.main()
