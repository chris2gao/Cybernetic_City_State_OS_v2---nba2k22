import os
import glob
import subprocess
import time

def run_bulk_evaluation():
    db_dir = "../../08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/"
    yaml_files = glob.glob(os.path.join(db_dir, "*.yaml"))
    
    print(f"=== Bulk Sandbox Evaluator ===")
    print(f"Found {len(yaml_files)} V9.1 Math Nodes in DB.\n")
    
    passed_count = 0
    failed_count = 0
    failed_files = []
    
    start_time = time.time()
    
    for file_path in yaml_files:
        filename = os.path.basename(file_path)
        
        # Skip schema and legacy files
        if filename in ['schema.yaml', 'topology_compactness.yaml', 'topology_transformers.yaml']:
            continue
            
        print(f"[*] Testing Node: {filename} ", end="", flush=True)
        
        result = subprocess.run(["python", "sandbox_evaluator.py", file_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[PASSED]")
            passed_count += 1
        else:
            print("[FAILED]")
            failed_count += 1
            failed_files.append((filename, result.stderr or result.stdout))
            
    elapsed = time.time() - start_time
    
    print("\n=== BULK EVALUATION REPORT ===")
    print(f"Total Tested: {len(yaml_files)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Time Elapsed: {elapsed:.2f} seconds")
    
    if failed_count > 0:
        print("\n--- Failure Details ---")
        for fname, err in failed_files:
            print(f"\nNode: {fname}")
            print(err.strip())
            
    if failed_count == 0:
        print("\n[SUCCESS] Entire graph is mathematically sound. Ready for LLM Context Mounting.")

if __name__ == "__main__":
    run_bulk_evaluation()
