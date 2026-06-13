import os
import subprocess
import yaml

def test_pipeline():
    print("=== Cybernetic City State OS v9.1 Factory Pipeline Test ===")
    
    # Let's test our sandbox with an existing V9.1 pure math yaml
    # functional_analysis_attention.yaml
    target_yaml = "../../08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/functional_analysis_attention.yaml"
    
    print(f"[*] Testing Sandbox Evaluator on existing V9.1 node: {target_yaml}")
    
    if not os.path.exists(target_yaml):
        print(f"[ERROR] Could not find {target_yaml}")
        return
        
    result = subprocess.run(
        ["python", "sandbox_evaluator.py", target_yaml], 
        capture_output=True, 
        text=True
    )
    
    print(result.stdout)
    if result.returncode == 0:
        print("[SUCCESS] Sandbox execution passed for FA-001 (Attention)!")
    else:
        print("[FAILED] Sandbox execution failed. Error:")
        print(result.stderr)
        
if __name__ == "__main__":
    test_pipeline()
