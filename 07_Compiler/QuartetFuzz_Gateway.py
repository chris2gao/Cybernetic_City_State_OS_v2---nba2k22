import hashlib
import time
import random
import logging
from Lattice_Sandbox import SandboxSession, to_event

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuartetFuzz")

class MutationEngine:
    """Pure Python Property-Based Mutation Engine."""
    def mutate_string(self, seed: str) -> str:
        if not seed:
            return random.choice(["\x00", "A"*10000, "'; DROP TABLE users;--", "\n\r\t", "👍"])
        
        mutations = [
            lambda s: s + "\x00",
            lambda s: s * 100,
            lambda s: s[:len(s)//2],
            lambda s: s + "A" * (10**4),
            lambda s: s.replace(s[0], random.choice(['\x00', '\n', '\xff'])),
            lambda s: ""
        ]
        return random.choice(mutations)(seed)

    def mutate_int(self, seed: int) -> int:
        mutations = [
            lambda x: 0,
            lambda x: -1,
            lambda x: 2**31 - 1,
            lambda x: -(2**31),
            lambda x: x * 1000,
            lambda x: x // 2 if x != 0 else 1
        ]
        return random.choice(mutations)(seed)

    def mutate_value(self, val):
        if isinstance(val, str): return self.mutate_string(val)
        if isinstance(val, int): return self.mutate_int(val)
        if isinstance(val, list): return val + [self.mutate_value(random.choice(val)) if val else None] # stub
        if isinstance(val, dict): return val # stub
        return val # fallback

class CrashDeduplicator:
    def __init__(self):
        self.seen_hashes = set()

    def add_and_check(self, traceback_str: str) -> bool:
        """Returns True if this is a new unique crash."""
        if not traceback_str:
            return False
            
        lines = traceback_str.strip().split('\n')
        # Take the last 3 lines
        fingerprint_lines = lines[-3:] if len(lines) >= 3 else lines
        fingerprint = "\n".join(fingerprint_lines).strip()
        
        hash_val = hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()
        if hash_val in self.seen_hashes:
            return False
        
        self.seen_hashes.add(hash_val)
        return True

class BaselineValidator:
    @staticmethod
    def validate(session: SandboxSession, harness_code: str, seed_injection_code: str) -> bool:
        """Runs the harness with the original un-mutated seed. Must pass."""
        logger.info("Running Zero-Defect Baseline Check...")
        full_code = harness_code + "\n" + seed_injection_code
        res = session.inject(full_code, timeout=5)
        
        if res['exit_code'] != 0 or "TIMEOUT" in res['status'] or "Traceback" in res['stderr']:
            logger.critical("HARNESS_BROKEN: The baseline execution failed. Harness itself is defective.")
            logger.error(f"Stderr: {res['stderr']}")
            return False
            
        logger.info("Baseline Check Passed.")
        return True

class CampaignController:
    def __init__(self, issue_id: str):
        self.issue_id = issue_id
        self.mutator = MutationEngine()
        self.deduplicator = CrashDeduplicator()

    def generate_injection(self, template: str, target_var: str, val) -> str:
        """Generates the python code to inject the mutated variable."""
        if isinstance(val, str):
            val_repr = repr(val)
        else:
            val_repr = str(val)
            
        return f"\n{target_var} = {val_repr}\n" + template

    def run_fuzzing_campaign(self, harness_code: str, target_var: str, seed_val, max_iters=1000, max_seconds=120):
        start_time = time.time()
        crashes_found = 0
        
        with SandboxSession() as session:
            # 1. Baseline Check
            baseline_code = self.generate_injection("run_target()", target_var, seed_val)
            if not BaselineValidator.validate(session, harness_code, baseline_code):
                to_event(self.issue_id, "FUZZING ABORTED: HARNESS_BROKEN on baseline check.")
                return {"status": "HARNESS_BROKEN"}

            logger.info(f"Starting Fuzzing Campaign for {max_iters} iterations or {max_seconds}s...")
            
            # 2. Main Loop
            for i in range(max_iters):
                if time.time() - start_time > max_seconds:
                    logger.warning("Fuzzing Campaign hit hard timeout.")
                    break
                    
                mutated_val = self.mutator.mutate_value(seed_val)
                injection_code = self.generate_injection("run_target()", target_var, mutated_val)
                full_code = harness_code + "\n" + injection_code
                
                res = session.inject(full_code, timeout=2)
                
                # Check for crash
                if res['exit_code'] != 0 or "TIMEOUT" in res['status'] or "Traceback" in res['stderr']:
                    err_str = res['stderr'] if res['stderr'] else f"Exit code {res['exit_code']} or {res['status']}"
                    
                    if self.deduplicator.add_and_check(err_str):
                        crashes_found += 1
                        logger.error(f"New unique crash found at iteration {i}!")
                        
                        report = f"### [QuartetFuzz] Unique Crash Detected!\n"
                        report += f"**Input Value**: `{repr(mutated_val)}`\n"
                        report += f"**Traceback**:\n```python\n{err_str}\n```\n"
                        
                        to_event(self.issue_id, report)

        logger.info(f"Campaign completed. {crashes_found} unique crashes found.")
        to_event(self.issue_id, f"Fuzzing Campaign Completed. {crashes_found} unique crashes discovered.")
        return {"status": "COMPLETED", "crashes": crashes_found}
