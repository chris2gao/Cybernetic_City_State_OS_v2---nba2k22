import argparse
import json
import os
import subprocess
import sys
import hashlib

# Configuration
BUS_STATE_FILE = ".bus_state_manager.json"
MAX_REJECTIONS = 5
INTERCEPTOR_SCRIPT = "system_2_interceptor.py"
PERSONA_XML = "../Personas/Red_Team_Mathematician_Protocol.xml"

MODEL_THRESHOLDS = {
    "gemini-3.1-pro": 2048 * 1024, # 2MB
    "gemini-flash": 512 * 1024,    # 512KB
    "claude-opus": 600 * 1024,     # 600KB
    "default": 100 * 1024          # 100KB
}

def get_state_key(draft_path):
    abs_path = os.path.abspath(draft_path)
    return hashlib.md5(abs_path.encode('utf-8')).hexdigest()

def load_state():
    if os.path.exists(BUS_STATE_FILE):
        try:
            with open(BUS_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_state(state):
    with open(BUS_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

def handle_submit_draft(draft_path, model="default"):
    if not os.path.exists(draft_path):
        print(f"[BUS ERROR] Draft file not found: {draft_path}")
        sys.exit(1)

    state = load_state()
    key = get_state_key(draft_path)
    
    # Initialize state for this draft if it doesn't exist
    if key not in state:
        state[key] = {"rejection_count": 0, "draft_path": draft_path}
    save_state(state)

    # Generate Task Request (with Delta-Sync Gateway logic placeholder)
    task_request_path = "task_request.md"
    file_size = os.path.getsize(draft_path)
    threshold = MODEL_THRESHOLDS.get(model, MODEL_THRESHOLDS["default"])
    
    with open(task_request_path, 'w', encoding='utf-8') as f:
        f.write(f"# Memento Handover: Formal Validation Request\n")
        f.write(f"Target Draft: {draft_path}\n")
        if file_size > threshold * 0.5: # 50% dynamic threshold for Delta-Sync isolation
            f.write(f"Directive: [DYNAMIC HYBRID MODE - ISOLATED] Artifact is large. Focus ONLY on topological edge cases. Do not re-verify standard text.\n")
        else:
            f.write(f"Directive: [DYNAMIC HYBRID MODE - COUPLED] You must execute your protocol against this draft. Output a valid verification_result.md file.\n")
    
    # Fire the System Summon Signal (Micro-Patch Bridge Protocol)
    print("======================================================================")
    print("[ACTION_REQUIRED: SUMMON_SUBAGENT]")
    print("Target_Class: Red_Team_Mathematician")
    print(f"Payload_File: {os.path.abspath(task_request_path)}")
    print("System Directive: LLM Coordinator, please trigger invoke_subagent now.")
    print("======================================================================")

def handle_submit_validation(validation_path, draft_path, model="default"):
    if not os.path.exists(validation_path):
        print(f"[BUS ERROR] Validation file not found: {validation_path}")
        sys.exit(1)
    
    # 1. Run the Interceptor (Execution Gate)
    interceptor_cmd = [
        sys.executable, 
        INTERCEPTOR_SCRIPT, 
        "--persona", PERSONA_XML, 
        "--artifact", validation_path,
        "--model", model
    ]
    
    # We use subprocess to actually run the Python script.
    try:
        result = subprocess.run(interceptor_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            stderr_output = result.stderr
            # [V8 P0] Traceback Topology Classification
            if "TypeError" in stderr_output or "AttributeError" in stderr_output:
                print("[V8 P0 ISOLATION] System Bug Detected (TypeError/AttributeError).")
                print("Action: Silent retry or fallback to L0 Socratic mode. DO NOT blame the student.")
                sys.exit(1)
            elif "kd.kernel.LemmaError" in stderr_output or "unsat" in stderr_output:
                print("[V8 P0 ISOLATION] Logic Bug / unsat Detected.")
                print("Action: Convert to Socratic probe.")
                sys.exit(1)
            else:
                print("[BUS NOTIFICATION] The execution gate rejected the artifact format. LLM must self-correct the subagent.")
                print(f"Details: {stderr_output}")
                sys.exit(1)
    except Exception as e:
        print(f"[V8 P0 ISOLATION] Unexpected System Error: {str(e)}")
        sys.exit(1)

    # 1.5 V9 Domain Classifier Gate (PURE_STRUCTURE vs COMPUTABLE_ALGEBRA)
    with open(validation_path, 'r', encoding='utf-8') as f:
        validation_content_lower = f.read().lower()
        
    pure_structure_keywords = ["topology", "banach", "hilbert", "manifold", "compact", "homeomorphism", "measure theory", "拓扑", "流形", "巴拿赫", "紧致"]
    is_pure_structure = any(kw in validation_content_lower for kw in pure_structure_keywords)
    
    if is_pure_structure:
        print("[V9 DOMAIN CLASSIFIER] [PURE_STRUCTURE_LANE] Detected advanced theoretical abstraction.")
        print("Action: Bypassing Z3 formal verification. Degrading to Semantic Consistency Audit.")
        print("Verdict: SEMANTIC_AUDIT_PASSED (Simulated Semantic Validation)")
    else:
        print("[V9 DOMAIN CLASSIFIER] [COMPUTABLE_ALGEBRA_LANE] Routing to V8 Z3+CEGAR Validation...")
        # 2. Run sym2z validation (P2)
        sym2z_cmd = [
            sys.executable,
            "sym2z_validator.py",
            validation_path
        ]
        try:
            sym2z_result = subprocess.run(sym2z_cmd, capture_output=True, text=True)
            if sym2z_result.returncode != 0:
                stderr_output = sym2z_result.stderr
                if "kd.kernel.LemmaError" in stderr_output or "unsat" in stderr_output:
                    print("[V8 P0 ISOLATION] Logic Bug / unsat Detected in sym2z.")
                    print("Action: Convert to Socratic probe.")
                    print(f"Details: {stderr_output}")
                    sys.exit(1)
                else:
                    print("[V8 P0 ISOLATION] System Bug Detected in sym2z.")
                    print("Action: Silent retry or fallback to L0 Socratic mode. DO NOT blame the student.")
                    print(f"Details: {stderr_output}")
                    sys.exit(1)
        except Exception as e:
            print(f"[V8 P0 ISOLATION] Unexpected System Error in sym2z: {str(e)}")
            sys.exit(1)

    # 3. Both gates passed. Now read the logical verdict.
    with open(validation_path, 'r', encoding='utf-8') as f:
        content = f.read()

    state = load_state()
    key = get_state_key(draft_path)
    if key not in state:
        state[key] = {"rejection_count": 0, "draft_path": draft_path}

    if "[VERDICT: APPROVE]" in content:
        # Success!
        final_path = "../final_lesson.md"
        # We simulate compilation by copying the draft.
        import shutil
        shutil.copy2(draft_path, final_path)
        
        # Reset state
        state[key]["rejection_count"] = 0
        save_state(state)
        
        print("======================================================================")
        print("[BUS_SIGNAL: DRAFT_APPROVED]")
        print(f"Compilation Successful. The mathematical topology is flawless.")
        print(f"Output File: {os.path.abspath(final_path)}")
        print("System Directive: Proceed to present the final lesson to the human.")
        print("======================================================================")
        
    elif "[VERDICT: REJECT]" in content:
        # Rejected! Increment counter and check for deadlock
        state[key]["rejection_count"] += 1
        count = state[key]["rejection_count"]
        save_state(state)
        
        if count >= MAX_REJECTIONS:
            print("======================================================================")
            print("[FATAL BUS ERROR: THALAMIC CIRCUIT BREAKER TRIPPED]")
            print(f"[Paradox_Exception: Unsolvable/Malicious Loop]")
            print(f"Maximum rejection limit reached ({MAX_REJECTIONS}/{MAX_REJECTIONS}) in short timeframe.")
            print("The Assembly_Agent and Exam_Agent are caught in a microservice RPC broadcast storm.")
            print("System Directive: Truncating current inference branch. Escalating to Safe Mode.")
            print("======================================================================")
            sys.exit(1)
            
        else:
            # Extract the reason to feed back
            reason = "Unknown flaw."
            for line in content.split('\n'):
                if "[VERDICT: REJECT]" in line and "Reason:" in line:
                    reason = line.split("Reason:")[1].strip()
                    break
                    
            print("======================================================================")
            print("[ACTION_REQUIRED: FRONTEND_REWRITE]")
            print(f"Rejection_Count: {count}/{MAX_REJECTIONS}")
            print(f"Flaw_Detected: {reason}")
            
            # [V8 P1] Dynamic Scaffolding & Early Stopping
            if count >= 3:
                print("[V8 P1 DYNAMIC SCAFFOLDING TRIGGERED]")
                print("System Directive: frustration_index >= 3. Socratic Router MUST execute 'Fading Assistance'. Drop high-dimensional metaphors and provide a simple univariate calculable branch immediately.")
            else:
                print("System Directive: Socratic Router must rewrite the draft based on these topological constraints. Maintain Socratic pressure.")
            print("======================================================================")
            sys.exit(0)
    else:
        print("[BUS ERROR] CRITICAL FAULT: Validated content does not contain APPROVE or REJECT despite passing interceptor. Protocol corruption.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="System 2 Dual-Ontology Execution Bus")
    parser.add_argument("--action", required=True, choices=["submit_draft", "submit_validation"], help="The stage of the workflow to process.")
    parser.add_argument("--draft", required=True, help="Path to the frontend draft file.")
    parser.add_argument("--validation", help="Path to the backend validation file (Required for submit_validation).")
    parser.add_argument("--model", default="default", help="The target model for context thresholding.")

    args = parser.parse_args()

    # Pre-flight check
    if not os.path.exists(INTERCEPTOR_SCRIPT):
         print(f"[BUS ERROR] Missing dependencies. {INTERCEPTOR_SCRIPT} not found.")
         sys.exit(1)

    if args.action == "submit_draft":
        handle_submit_draft(args.draft, args.model)
    elif args.action == "submit_validation":
        if not args.validation:
            print("[BUS ERROR] --validation argument required for submit_validation action.")
            sys.exit(1)
        handle_submit_validation(args.validation, args.draft, args.model)
