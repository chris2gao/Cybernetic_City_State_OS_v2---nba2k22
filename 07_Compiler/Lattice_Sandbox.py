import os
import sys
import json
import time
import subprocess
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Lattice_Sandbox")

def get_iso_time():
    return datetime.now(timezone.utc).isoformat()

def to_event(issue_id, content, action_type="FUZZ_RESULT"):
    """Bridges the sandbox execution result to the CQRS event log."""
    event = {
        "schema_version": "1.0",
        "timestamp": get_iso_time(),
        "issue_id": issue_id,
        "agent_role": "Judge",
        "action_type": action_type,
        "content": content
    }
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "03_Daily_Execution", "activity.jsonl"))
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

class SandboxStrategy(ABC):
    @abstractmethod
    def execute(self, code_str: str, timeout: int = 10) -> dict:
        pass

    @abstractmethod
    def cleanup(self):
        pass

class DockerStrategy(SandboxStrategy):
    def execute(self, code_str: str, timeout: int = 10) -> dict:
        logger.info("Executing via Docker Strategy")
        return {"status": "success", "stdout": "", "stderr": "Docker not fully implemented in mock", "exit_code": 0}
        
    def cleanup(self):
        pass

class WSL2Strategy(SandboxStrategy):
    def execute(self, code_str: str, timeout: int = 10) -> dict:
        logger.info("Executing via WSL2 Strategy")
        # TODO: Implement WSL2 namespace isolation
        return {"status": "success", "stdout": "", "stderr": "WSL2 not fully implemented in mock", "exit_code": 0}
        
    def cleanup(self):
        pass

class SubprocessStrategy(SandboxStrategy):
    """
    ⚠️ DEGRADED ISOLATION: This backend provides soft restrictions only. 
    Do not use for untrusted code in production.
    """
    def execute(self, code_str: str, timeout: int = 10) -> dict:
        logger.warning("Using DEGRADED ISOLATION Subprocess Strategy. Soft restrictions only.")
        
        # Inject soft restrictions (e.g., overriding builtins, sys.modules)
        # Note: A real attacker can bypass this. This is just for demonstration of the boundary.
        secure_header = """
import sys
import builtins

_orig_import = builtins.__import__

# Soft isolation mock
def secure_import(name, globals=None, locals=None, fromlist=(), level=0):
    forbidden = ['os', 'subprocess', 'socket', 'urllib', 'requests']
    if name in forbidden:
        raise ImportError(f"Isolation violation: Cannot import {name}")
    return _orig_import(name, globals, locals, fromlist, level)

builtins.__import__ = secure_import

# OOM simulation: if they try to allocate huge lists, we can't easily intercept in pure python
# but we can try to use resource module on Linux. On Windows, we rely on the OS or timeout.
"""
        full_code = secure_header + code_str
        
        import tempfile
        import uuid
        temp_file = os.path.join(tempfile.gettempdir(), f"sandbox_exec_{uuid.uuid4().hex}.py")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(full_code)
            
        start_time = time.time()
        # Create subprocess
        if sys.platform == "win32":
            proc = subprocess.Popen([sys.executable, temp_file], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE,
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            proc = subprocess.Popen([sys.executable, temp_file], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
        
        try:
            # 1. Wait with timeout
            stdout, stderr = proc.communicate(timeout=timeout)
            return {
                "status": "success",
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "exit_code": proc.returncode,
                "execution_time": time.time() - start_time
            }
        except subprocess.TimeoutExpired:
            # 2. Two-stage kill
            logger.warning(f"Timeout of {timeout}s reached. Sending SIGTERM/CTRL_C...")
            if sys.platform == "win32":
                import signal
                os.kill(proc.pid, signal.CTRL_C_EVENT)
            else:
                proc.terminate()
                
            try:
                stdout, stderr = proc.communicate(timeout=2.0)
                status = "TIMEOUT_GRACEFUL"
            except subprocess.TimeoutExpired:
                logger.error("Process ignored SIGTERM. Sending SIGKILL...")
                proc.kill()
                stdout, stderr = proc.communicate()
                status = "TIMEOUT_KILL"
                
            return {
                "status": status,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "exit_code": proc.returncode,
                "execution_time": time.time() - start_time
            }
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def cleanup(self):
        # Clean up any leftover processes or files
        pass

class AutoDetector:
    @staticmethod
    def get_strategy() -> SandboxStrategy:
        # Detect Docker
        try:
            subprocess.run(["docker", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return DockerStrategy()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        # Detect WSL2
        try:
            subprocess.run(["wsl", "--status"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return WSL2Strategy()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        # Fallback to Subprocess
        return SubprocessStrategy()

class EphemeralSandbox:
    def __init__(self):
        self.strategy = AutoDetector.get_strategy()
        
    def execute_isolated(self, code_str: str, timeout: int = 5):
        try:
            result = self.strategy.execute(code_str, timeout)
            return result
        finally:
            self.strategy.cleanup()

class SandboxSession:
    """Warm pool for Fuzzing."""
    def __init__(self):
        self.strategy = AutoDetector.get_strategy()
        
    def __enter__(self):
        self.reset()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.strategy.cleanup()
        
    def reset(self):
        """Clears residual state before next injection."""
        logger.info("Resetting Sandbox Session state...")
        self.strategy.cleanup()
        # In a real Docker Warm pool, this would rm -rf /tmp/* and kill background procs
        
    def inject(self, code_str: str, timeout: int = 5):
        self.reset()
        return self.strategy.execute(code_str, timeout)

if __name__ == "__main__":
    # Quick test of ephemeral
    sandbox = EphemeralSandbox()
    res = sandbox.execute_isolated("print('Hello from Lattice Sandbox')")
    print(res)
