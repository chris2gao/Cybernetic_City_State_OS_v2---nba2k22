from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_ROOTS = (
    Path(__file__).resolve().parent / "calibration",
    Path(__file__).resolve().parent / "timeout_probe",
)


def pytest_ignore_collect(collection_path: Path, config: object) -> bool | None:
    """Keep experiment-only fixture suites out of repository-root collection."""
    invocation_dir = Path(str(config.invocation_params.dir)).resolve()
    if invocation_dir != REPOSITORY_ROOT:
        return None
    resolved = Path(str(collection_path)).resolve()
    return any(resolved.is_relative_to(root) for root in FIXTURE_ROOTS)
