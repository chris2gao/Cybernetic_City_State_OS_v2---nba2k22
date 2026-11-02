"""Profile timing baseline and component breakdown for REA execution chain."""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import time

def measure_component_timings():
    results = {}
    
    # 1. Python overhead
    t0 = time.perf_counter()
    test_dir = pathlib.Path("test_timing_scratch")
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "test_req.json").write_text(json.dumps({"test": "data" * 100}), encoding="utf-8")
    h = hashlib.sha256((test_dir / "test_req.json").read_bytes()).hexdigest()
    shutil.rmtree(test_dir)
    t_python_io_ms = (time.perf_counter() - t0) * 1000.0
    results["t_python_prep_ms"] = round(t_python_io_ms, 3)
    
    # 2. PowerShell bootstrap overhead
    t0 = time.perf_counter()
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "exit 0"], capture_output=True)
    t_ps_bootstrap_ms = (time.perf_counter() - t0) * 1000.0
    results["t_powershell_bootstrap_ms"] = round(t_ps_bootstrap_ms, 3)
    
    # 3. Game EXE SHA256 hashing in PowerShell
    ps_hash_cmd = "$games = Get-Process NBA2K22; (Get-FileHash -LiteralPath $games[0].MainModule.FileName -Algorithm SHA256).Hash"
    t0 = time.perf_counter()
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_hash_cmd], capture_output=True, text=True)
    t_ps_hash_ms = (time.perf_counter() - t0) * 1000.0
    results["t_powershell_hash_exe_ms"] = round(t_ps_hash_ms, 3)
    
    # 4. REA CLI with duration 1000 ms vs duration 15000 ms
    node = shutil.which("node")
    rea = pathlib.Path(os.environ.get("APPDATA", "")) / "npm/node_modules/rea-agents/scripts/rea.mjs"
    
    # Measure REA CLI 1000 ms duration
    t0 = time.perf_counter()
    cmd_rea_1000 = [node, str(rea), "instrument-with-frida", "attach", "10404", "--script", "send({status:'ok'});", "--duration-ms", "1000", "--format", "json"]
    r_1000 = subprocess.run(cmd_rea_1000, capture_output=True, text=True)
    t_rea_1000_ms = (time.perf_counter() - t0) * 1000.0
    results["t_rea_cli_duration_1000ms_total_ms"] = round(t_rea_1000_ms, 3)
    
    # Extrapolated fixed REA overhead = Total (1000ms) - 1000ms
    results["t_rea_fixed_attach_detach_overhead_ms"] = round(t_rea_1000_ms - 1000.0, 3)
    
    # 5. Baseline run extraction
    baseline_run_dir = pathlib.Path("01_os/07_content/_runs/run-20261101-nba2k22-rea-controlled-live-bulk-pilot-001")
    stage2_res_path = baseline_run_dir / "07_测试执行/stage2_mutation/execution_result.json"
    stage1_res_path = baseline_run_dir / "07_测试执行/stage1_noop/execution_result.json"
    
    if stage2_res_path.exists():
        stage2_data = json.loads(stage2_res_path.read_text(encoding="utf-8"))
        results["baseline_stage2_mutation"] = stage2_data
    if stage1_res_path.exists():
        stage1_data = json.loads(stage1_res_path.read_text(encoding="utf-8"))
        results["baseline_stage1_noop"] = stage1_data
        
    return results

if __name__ == "__main__":
    timings = measure_component_timings()
    print(json.dumps(timings, indent=2))
