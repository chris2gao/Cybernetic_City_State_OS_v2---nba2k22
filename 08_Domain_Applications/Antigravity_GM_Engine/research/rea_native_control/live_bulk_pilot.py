"""NBA2K22 REA Controlled Live Bulk Pilot Runner.

Coordinates:
  1. Live roster & tendency discovery probe
  2. Stage 1 Live No-Op execution (Gate G5)
  3. Stage 2 Live Bounded Mutation execution to min value 0 (Gate G6)
  4. Stage 3 Independent post-write readback verification
"""
import argparse
import json
from pathlib import Path
import sys

_RESEARCH_DIR = Path(__file__).resolve().parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

import probe_live_roster
import run_live_stage1_noop
import run_live_stage2_mutation

def main():
    parser = argparse.ArgumentParser(description="NBA2K22 REA Controlled Live Bulk Pilot")
    parser.add_argument('--action', choices=['probe', 'stage1', 'stage2', 'all'], default='all',
                        help="Action to execute: probe, stage1 (no-op), stage2 (mutation to 0), or all")
    parser.add_argument('--expected-pid', type=int, default=10404, help="Expected NBA2K22 PID")
    args = parser.parse_args()

    run_root = Path("01_os/07_content/_runs/run-20261101-nba2k22-rea-controlled-live-bulk-pilot-001").resolve()

    if args.action in ('probe', 'all'):
        print("[*] Running Live Roster and Tendency Probe...")
        out_probe = run_root / "07_测试执行" / "probe_run"
        res_probe = probe_live_roster.run_probe(out_probe, expected_pid=args.expected_pid)
        print(f"[+] Probe completed with outcome: {res_probe.get('outcome')}")

    if args.action in ('stage1', 'all'):
        print("\n[*] Running Stage 1: Live No-Op Multi-Chunk Execution...")
        res_stage1 = run_live_stage1_noop.main()
        assert res_stage1['metrics']['conservation_holds'] is True

    if args.action in ('stage2', 'all'):
        print("\n[*] Running Stage 2: Live Bounded Mutation Execution (Target=0)...")
        res_stage2 = run_live_stage2_mutation.main()
        assert res_stage2['metrics']['conservation_holds'] is True

        print("\n[*] Running Stage 3: Independent Post-Mutation Readback Verification...")
        out_readback = run_root / "07_测试执行" / "post_mutation_readback"
        res_readback = probe_live_roster.run_probe(out_readback, expected_pid=args.expected_pid)
        print(f"[+] Readback completed with outcome: {res_readback.get('outcome')}")

if __name__ == '__main__':
    main()
