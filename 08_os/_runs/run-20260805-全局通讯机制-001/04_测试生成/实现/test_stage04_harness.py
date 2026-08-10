#!/usr/bin/env python3
"""Harness self-tests for stage 04 test infrastructure."""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, unittest, yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
STAGE04_ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_PATH = STAGE04_ROOT / "冻结测试候选_v1.yml"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_stage04_executable_tests as runner_module
import synthetic_adapters

class TestDiscovery(unittest.TestCase):
    def test_startup_validation(self):
        ok, msg = runner_module.verify_specs(REPO_ROOT)
        self.assertTrue(ok, f"Startup validation failed: {msg}")

    def test_all_test_ids_sequential(self):
        data = yaml.safe_load(CANDIDATE_PATH.read_text(encoding="utf-8"))
        ids = [t["test_id"] for t in data["tests"]]
        expected = [f"GC-T{i:03d}" for i in range(1, 51)]
        self.assertEqual(ids, expected)
        self.assertNotIn("make_generic_test", open(runner_module.__file__, encoding="utf-8").read())

class TestRunnerCases(unittest.TestCase):
    def setUp(self):
        with open(CANDIDATE_PATH, "r", encoding="utf-8") as f:
            self.freeze_data = yaml.safe_load(f)
            
    def test_conforming_observation(self):
        # 1. conforming observation
        adapter = synthetic_adapters.SyntheticConformingAdapter("full")
        for tid, case in runner_module.TEST_CASES.items():
            fixture = case.fixture_factory("full", REPO_ROOT, "", self.freeze_data)
            exc = None
            try:
                case.action(adapter, fixture)
            except Exception as e:
                exc = e
            try:
                case.evaluator(exc, fixture)
            except Exception as e:
                self.fail(f"{tid} failed conforming test with {e}")

    def test_correct_mutation(self):
        # 2. correct mutation
        adapter = synthetic_adapters.SyntheticMutatingAdapter("mutation-suite")
        for tid, case in runner_module.TEST_CASES.items():
            fixture = case.fixture_factory("mutation-suite", REPO_ROOT, "", self.freeze_data)
            exc = None
            try:
                case.action(adapter, fixture)
            except Exception as e:
                exc = e
            with self.assertRaises(ValueError, msg=f"{tid} failed to catch correct mutation") as ctx:
                case.evaluator(exc, fixture)
            self.assertEqual(str(ctx.exception), case.failure_code)

    def test_wrong_mutation(self):
        # 3. wrong mutation
        adapter = synthetic_adapters.SyntheticMutatingAdapter("mutation-suite")
        tids = list(runner_module.TEST_CASES.keys())
        for i, (tid, case) in enumerate(runner_module.TEST_CASES.items()):
            wrong_tid = tids[(i + 1) % len(tids)]
            wrong_case = runner_module.TEST_CASES[wrong_tid]
            
            wf = wrong_case.fixture_factory("mutation-suite", REPO_ROOT, "", self.freeze_data)
            exc = None
            try:
                case.action(adapter, wf)
            except Exception as e:
                exc = e
            
            wrong_fixture = wf
            if exc is None:
                exc = RuntimeError("Simulated wrong mutation exception")
                wrong_fixture = {}
                wrong_tid = "Simulated"
            
            try:
                case.evaluator(exc, wrong_fixture)
                self.fail(f"{tid} silently passed when given a wrong mutation from {wrong_tid}. Evaluators MUST raise an exception for mutated input, even if it's not the target failure code.")
            except ValueError as e:
                if str(e) == case.failure_code:
                    self.fail(f"{tid} falsely reported correct failure code on wrong mutation from {wrong_tid}")

    def test_unrelated_exception(self):
        # 4. unrelated exception
        for tid, case in runner_module.TEST_CASES.items():
            fixture = case.fixture_factory("mutation-suite", REPO_ROOT, "", self.freeze_data)
            exc = RuntimeError("Some totally unrelated framework crash")
            try:
                case.evaluator(exc, fixture)
                passed = True
            except Exception as e:
                if str(e) == case.failure_code:
                    self.fail(f"{tid} falsely derived specific failure_code from unrelated crash")
                passed = False
            self.assertFalse(passed, f"{tid} swallowed an unrelated framework exception")

if __name__ == "__main__":
    unittest.main()
