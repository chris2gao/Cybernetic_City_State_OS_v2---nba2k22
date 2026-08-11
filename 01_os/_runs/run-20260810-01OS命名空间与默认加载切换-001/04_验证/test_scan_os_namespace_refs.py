from __future__ import annotations

import importlib.util
from pathlib import Path


SCANNER_PATH = Path(__file__).with_name("scan_os_namespace_refs.py")
SPEC = importlib.util.spec_from_file_location("scan_os_namespace_refs", SCANNER_PATH)
assert SPEC and SPEC.loader
scanner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scanner)


def matches(text: str) -> list[str]:
    return [match.group(0).rstrip(".,;:") for match in scanner.REFERENCE_RE.finditer(text)]


def test_repository_path_forms_are_detected() -> None:
    line = "01_os/a.yml 01_os\\b.ps1 '01_os' \"01_os\" 01_os/** Path('01_os')"
    assert matches(line) == [
        "01_os/a.yml",
        "01_os\\b.ps1",
        "'01_os'",
        '"01_os"',
        "01_os/**",
        "'01_os'",
    ]


def test_bare_narrative_token_is_not_a_path_hit() -> None:
    assert matches("the namespace is called 01_os but no repository path is present") == []


def test_trailing_sentence_punctuation_is_not_part_of_match() -> None:
    assert matches("See 01_os/README.md.") == ["01_os/README.md"]


def test_binary_and_non_utf8_are_not_scanned_as_text() -> None:
    assert scanner.decode_tracked_text(b"abc\0def") == (None, "binary_nul")
    assert scanner.decode_tracked_text(b"\xff") == (None, "non_utf8")


def test_run_location_alone_never_implies_history() -> None:
    proposal = scanner.classify_occurrence(
        "01_os/_runs/run-x/notes.md",
        "See 01_os/README.md",
        "See 01_os/README.md",
        "generic notes without immutable bindings",
    )
    assert proposal["classification"] == "manual_review"


def test_bound_record_and_current_loader_are_distinguished() -> None:
    bound = scanner.classify_occurrence(
        "01_os/_runs/run-x/task.yml",
        "path: 01_os/README.md",
        "path: 01_os/README.md",
        "schema_version: x\ntask_id: t\nrun_id: r\npath: 01_os/README.md",
    )
    current = scanner.classify_occurrence(
        "01_os/06_execution/load.py",
        "root = Path('01_os')",
        "root = Path('01_os')",
        "root = Path('01_os')",
    )
    assert bound["classification"] == "preserve_historical_literal"
    assert current["classification"] == "rewrite_current_path"


def test_run_executable_stays_manual_without_caller_evidence() -> None:
    proposal = scanner.classify_occurrence(
        "01_os/_runs/run-x/replay.py",
        "root = '01_os'",
        "root = '01_os'",
        "root = '01_os'",
    )
    assert proposal["classification"] == "manual_review"
