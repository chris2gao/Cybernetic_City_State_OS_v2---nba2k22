import ast
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from fixtures import project, put, ROOT, proposal
from gm_core.data_reader import DataReader, load_json
from gm_core.history import StateStore
from gm_core.reports import prepare_run, markdown


class ReadOnlyTests(unittest.TestCase):
    def test_no_game_or_write_module_imports(self):
        forbidden = {"memory", "modifier", "scanner", "strategy_manager", "slider_manager", "trade_engine", "gm_engine", "ctypes", "win32api"}
        for path in (ROOT / "src/gm_core").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertFalse({name.name.split(".")[0] for name in node.names} & forbidden, str(path))
                if isinstance(node, ast.ImportFrom):
                    self.assertNotIn((node.module or "").split(".")[0], forbidden, str(path))

    def test_preparation_preserves_published_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory)
            source_paths = list((Path(directory) / "published").rglob("*.json"))
            before = {str(path): path.stat().st_mtime_ns for path in source_paths}
            run = prepare_run(data, "SYNTHETIC_READONLY")
            StateStore(directory).save_run(run, markdown(run))
            self.assertEqual(before, {str(path): path.stat().st_mtime_ns for path in source_paths})
            self.assertFalse(list(Path(directory).rglob("*.sqlite")))

    def test_incomplete_publication_and_validation_stream_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            project(directory)
            path = Path(directory) / "published/saves/synthetic_career/latest.json"
            pointer = load_json(path)
            pointer["uploaded_at"] = None
            put(path, pointer)
            with self.assertRaises(ValueError):
                DataReader(directory).read("synthetic_career")
            pointer.update(uploaded_at="2026-01-01T00:01:00Z", purpose="validation")
            put(path, pointer)
            with self.assertRaises(ValueError):
                DataReader(directory).read("synthetic_career")

    def test_cannot_write_state_into_sources(self):
        with self.assertRaises(ValueError):
            StateStore(ROOT, ROOT / "published")
        with self.assertRaises(ValueError):
            StateStore(ROOT, ROOT / "database")

    def test_published_real_data_readonly_compatibility(self):
        data = DataReader(ROOT).read("mc_haliburton_2021")
        run = prepare_run(data, "DEVELOPMENT_COMPATIBILITY_ONLY")
        self.assertEqual(run["teams_reviewed"], 30)
        self.assertEqual(run["decisions"], [])
        # Published snapshots now contain observed season totals. Compatibility
        # cannot assume the old fixture's all-unknown statistics; preparation
        # must still never approve a lifecycle or create formal decisions.
        self.assertTrue(all(item["profile"]["lifecycle"]["status"] in {"PROPOSED","NOT_EVALUABLE"}
                            for item in run["team_reviews"].values()))
        self.assertIn(run["calculations"]["IND.win_percentage"]["availability"],{"CALCULATED","UNKNOWN"})

    def test_cli_prepares_simulation_and_calculates(self):
        with tempfile.TemporaryDirectory() as directory:
            data = project(directory, complete=True)
            command = [sys.executable, str(ROOT / "scripts/gm_prepare.py"), "--project-root", directory,
                       "--save-id", "synthetic_career", "--run-id", "SYNTHETIC_CLI", "--mode", "simulation"]
            completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            run = load_json(Path(directory) / "gm_state/careers/synthetic_career/runs/SYNTHETIC_CLI/run.json")
            self.assertEqual(run["teams_reviewed"], 30)
            request = Path(directory) / "calculation_request.json"
            put(request, {"career_id": "synthetic_career", "source_batch_id": "SYNTHETIC_BATCH_1",
                          "operation": "win_percentage", "inputs": {"wins": 12, "losses": 8}})
            completed = subprocess.run([sys.executable, str(ROOT / "scripts/gm_calculate.py"), "--request", str(request)],
                                       capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("0.6", completed.stdout)
            proposal_path = Path(directory) / "synthetic_proposal.json"
            put(proposal_path, proposal(data))
            completed = subprocess.run([sys.executable, str(ROOT / "scripts/gm_validate_proposal.py"),
                                       "--project-root", directory, "--save-id", "synthetic_career",
                                       "--proposal", str(proposal_path), "--save-pending"],
                                      capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('"execution_authorized": false', completed.stdout)
