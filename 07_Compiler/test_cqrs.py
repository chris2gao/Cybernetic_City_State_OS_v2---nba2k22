import os
import json
import time
from CQRS_Projector import CQRSProjector

jsonl_path = "../03_Daily_Execution/activity.jsonl"
md_path = "../03_Daily_Execution/status.md"

def reset():
    if os.path.exists(jsonl_path): os.remove(jsonl_path)
    if os.path.exists(md_path): os.remove(md_path)

def test_idempotency():
    print("Running Idempotency Test...")
    reset()
    
    event = {
        "schema_version": "1.0",
        "timestamp": "2026-06-04T12:00:00Z",
        "issue_id": "007",
        "agent_role": "Speaker",
        "action_type": "PROPOSE",
        "content": "Initialize V6"
    }
    
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
        
    projector = CQRSProjector(jsonl_path, md_path)
    projector.process_once()
    
    with open(md_path, "r", encoding="utf-8") as f:
        content1 = f.read()
        
    # Process again without changing the file
    projector.process_once()
    with open(md_path, "r", encoding="utf-8") as f:
        content2 = f.read()
        
    assert content1 == content2, "Idempotency failed"
    assert "Initialize V6" in content1
    print("Idempotency Test Passed!")

def test_dirty_data_downgrade():
    print("Running Dirty Data Tiered Response Test...")
    # Add 5 dirty lines
    with open(jsonl_path, "a", encoding="utf-8") as f:
        for i in range(5):
            f.write("THIS IS NOT JSON\n")
            
    projector = CQRSProjector(jsonl_path, md_path)
    # We must reset offset to read the new lines if using a new instance, but actually we should just run process_once
    projector.process_once()
    
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "系统降级中" in content, "Downgrade warning missing!"
    print("Dirty Data Test Passed!")
    
def test_structural_crash():
    print("Running Structural Crash Test...")
    reset()
    event = {
        "schema_version": "1.0",
        "timestamp": "2026-06-04T12:00:00Z",
        # MISSING action_type
    }
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
        
    projector = CQRSProjector(jsonl_path, md_path)
    try:
        projector.process_once()
        assert False, "Should have crashed!"
    except RuntimeError:
        print("Structural Crash Test Passed!")

if __name__ == "__main__":
    os.makedirs("../03_Daily_Execution", exist_ok=True)
    test_idempotency()
    test_dirty_data_downgrade()
    test_structural_crash()
    print("All physical tests passed!")
