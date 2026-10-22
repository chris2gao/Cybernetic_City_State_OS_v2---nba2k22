"""PR #3 path fix only: no game access or observed database reads."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from gm_workbench.store import Store

spec = importlib.util.spec_from_file_location('finance_path_check', ROOT/'scripts/gm_finance.py')
finance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finance)


class WorkbenchPathTests(unittest.TestCase):
    def test_store_rejects_protected_directories_before_creating_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ('saves', 'query_snapshots', 'published', 'PuBlIsHeD', 'seasons'):
                with self.subTest(folder=folder):
                    target = root/folder/'nested/gm_workbench.sqlite'
                    with self.assertRaisesRegex(ValueError, 'WORKBENCH_PATH_REQUIRED_NOT_FACTS'):
                        Store(target)
                    self.assertFalse((root/folder).exists())

    def test_store_allows_normal_derived_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'database/workbench/test/gm_workbench.sqlite'
            with Store(target) as store:
                self.assertEqual(store.list_runs('test'), [])
            self.assertTrue(target.is_file())

    def test_finance_export_rejects_protected_paths_and_allows_exports(self):
        run = dict(run_id='path_check', source_binding=dict(career_id='test', batch_id='synthetic'),
                   calculation_version='synthetic', base_season='2021-2022', horizon_seasons=[],
                   season_anchor_evidence={}, teams=[])
        with tempfile.TemporaryDirectory() as directory, patch.object(finance, 'Store') as factory:
            factory.return_value.__enter__.return_value.load_run.return_value = run
            root = Path(directory)
            for folder in ('saves', 'query_snapshots', 'published', 'PuBlIsHeD', 'seasons'):
                with self.subTest(folder=folder):
                    target = root/folder/'finance_summary'
                    args = finance.parser().parse_args(['export', '--career', 'test', '--run', 'path_check', '--output', str(target)])
                    with self.assertRaisesRegex(ValueError, 'EXPORT_CANNOT_TARGET_FACTS'):
                        finance.run(args)
                    self.assertFalse((root/folder).exists())
            target = root/'_exports/finance/path_check'
            args = finance.parser().parse_args(['export', '--career', 'test', '--run', 'path_check', '--output', str(target)])
            self.assertEqual(finance.run(args)['status'], 'EXPORTED_ANALYSIS_ONLY')
            self.assertEqual(json.loads((target/'summary.json').read_text(encoding='utf-8'))['status'], 'ANALYSIS_ONLY')
            self.assertTrue((target/'summary.md').is_file())


if __name__ == '__main__':
    unittest.main()
