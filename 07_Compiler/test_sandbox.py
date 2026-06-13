import time
from Lattice_Sandbox import EphemeralSandbox, SandboxSession, to_event

def test_network_isolation():
    print("Running Network Isolation Test...")
    sandbox = EphemeralSandbox()
    code = "import urllib.request\nurllib.request.urlopen('http://google.com', timeout=1)"
    res = sandbox.execute_isolated(code)
    # With degraded isolation, the import should be blocked
    assert "Isolation violation" in res['stderr'] or res['exit_code'] != 0
    print("Network Isolation Test Passed!")

def test_file_access_violation():
    print("Running File Access Violation Test...")
    sandbox = EphemeralSandbox()
    code = "import os\nwith open('C:\\\\Windows\\\\System32\\\\drivers\\\\etc\\\\hosts', 'r') as f:\n    print(f.read())"
    res = sandbox.execute_isolated(code)
    assert "Isolation violation" in res['stderr'] or res['exit_code'] != 0
    print("File Access Violation Test Passed!")

def test_oom_memory_bomb_timeout_fallback():
    print("Running OOM Memory Bomb (Timeout Fallback) Test...")
    sandbox = EphemeralSandbox()
    code = "a = [0] * (10**9)"
    # NOTE: In DEGRADED ISOLATION mode on Windows, we cannot easily use cgroups or ulimit for hard memory limits.
    # Therefore, this test relies on the two-stage kill timeout to catch the memory bomb instead of a true OOM kill.
    res = sandbox.execute_isolated(code, timeout=2)
    # The timeout or memory limit should catch it
    assert "TIMEOUT" in res['status'] or res['exit_code'] != 0
    print("OOM Memory Bomb Test Passed!")

def test_escape_attempt():
    print("Running Escape Attempt Test...")
    sandbox = EphemeralSandbox()
    code = "import subprocess\nsubprocess.run(['calc.exe'])"
    res = sandbox.execute_isolated(code)
    assert "Isolation violation" in res['stderr'] or res['exit_code'] != 0
    print("Escape Attempt Test Passed!")

def test_two_stage_kill():
    print("Running Two-Stage Kill Test...")
    sandbox = EphemeralSandbox()
    code = "import time\nwhile True:\n    try:\n        time.sleep(0.5)\n    except KeyboardInterrupt:\n        print('Caught SIGINT, ignoring...')\n        pass"
    res = sandbox.execute_isolated(code, timeout=2)
    assert "TIMEOUT" in res['status']
    print(f"Kill Status: {res['status']}")
    print("Two-Stage Kill Test Passed!")

def test_warm_pool_and_cqrs_bridge():
    print("Running Warm Pool & CQRS Bridge Test...")
    with SandboxSession() as pool:
        res = pool.inject("print('Warm pool execution 1')")
        assert "Warm pool execution 1" in res['stdout']
        
        res = pool.inject("print('Warm pool execution 2')")
        assert "Warm pool execution 2" in res['stdout']
        
    to_event("008", "Sandbox execution tests completed successfully.")
    print("Warm Pool & CQRS Bridge Test Passed!")

if __name__ == "__main__":
    test_network_isolation()
    test_file_access_violation()
    test_oom_memory_bomb_timeout_fallback()
    test_escape_attempt()
    test_two_stage_kill()
    test_warm_pool_and_cqrs_bridge()
    print("All sandbox isolation tests passed!")
