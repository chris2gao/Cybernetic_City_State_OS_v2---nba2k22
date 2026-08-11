from unittest import mock
import unittest
from pathlib import Path
from tempfile import gettempdir

import yaml

try:
    from . import stage04_production_adapter as production
    from .run_frozen_stage04_tests import REPO, STAGE04, _load_oracle, _sanitize_evidence
except ImportError:
    import stage04_production_adapter as production
    from run_frozen_stage04_tests import REPO, STAGE04, _load_oracle, _sanitize_evidence


class ProductionOracleCouplingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = _load_oracle()
        cls.freeze_data = yaml.safe_load(
            (STAGE04 / "冻结测试候选_v1.yml").read_text(encoding="utf-8")
        )

    def _case(self, test_id):
        return next(case for case in self.oracle.TESTS if case.test_id == test_id)

    def _assert_broken_route_detected(self, test_id, mode, patcher, *, exact_code=True):
        case = self._case(test_id)
        fixture = case.fixture_factory(mode, REPO, "", self.freeze_data)
        adapter = production.Stage04ProductionAdapter(mode)
        adapter.begin_case(test_id)
        exc = None
        with patcher:
            try:
                case.action(adapter, fixture)
            except Exception as caught:  # noqa: BLE001
                exc = caught
        if exact_code:
            with self.assertRaisesRegex(ValueError, f"^{case.failure_code}$"):
                case.evaluator(exc, fixture)
        else:
            with self.assertRaises(ValueError):
                case.evaluator(exc, fixture)

    def test_git_conflict_oracle_rejects_broken_stage06_observation(self):
        self._assert_broken_route_detected(
            "GC-T033",
            "full",
            mock.patch.object(production, "observe_same_path_conflict", return_value={}),
        )

    def test_archive_oracle_rejects_stage06_no_move(self):
        self._assert_broken_route_detected(
            "GC-T039",
            "full",
            mock.patch.object(
                production,
                "archive_physical_tree",
                return_value={
                    "archived_task_root": "missing",
                    "private_runtime_deleted": [],
                    "operation_trace": [],
                    "durable_prerequisite_observed": False,
                },
            ),
        )

    def test_sender_index_oracle_rejects_stage06_noop_validator(self):
        self._assert_broken_route_detected(
            "GC-T045",
            "mutation-suite",
            mock.patch.object(production, "validate_physical_pointer_index", return_value=None),
            exact_code=False,
        )

    def test_persisted_trace_removes_personal_random_temp_prefix(self):
        source = str(Path(gettempdir()) / "tmpabc123" / "task" / "message.yml")
        sanitized = _sanitize_evidence({"path": source})
        self.assertTrue(sanitized["path"].startswith("<isolated-temp>"))
        self.assertTrue(sanitized["path"].endswith("task\\message.yml"))


if __name__ == "__main__":
    unittest.main()
