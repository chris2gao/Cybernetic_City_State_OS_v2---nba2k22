import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import hashlib

# Configuration
STATE_FILE = ".interceptor_state.json"
MAX_RETRIES = 3

MODEL_THRESHOLDS = {
    "gemini-3.1-pro": 2048 * 1024, # 2MB
    "gemini-flash": 512 * 1024,    # 512KB
    "claude-opus": 600 * 1024,     # 600KB
    "default": 100 * 1024          # 100KB
}

def throw_fatal_error(message):
    """Prints a cold, structured fatal error and exits."""
    print(f"\n[SYSTEM 2 FATAL ERROR]")
    print(message)
    print("Directive: You have failed the Execution Gate. Self-correct immediately.\n")
    sys.exit(1)

def throw_system_halt():
    """Prints the ultimate halt signal when retries are exhausted."""
    print(f"\n[FATAL SYSTEM HALT]")
    print("Retry limit exceeded. Agent loop terminated to prevent cascading failure.")
    print("[SYSTEM_HALT_REQUESTED]\n")
    sys.exit(1)

def get_state_key(artifact_path):
    """Generates a unique key for the artifact path for state isolation."""
    abs_path = os.path.abspath(artifact_path)
    return hashlib.md5(abs_path.encode('utf-8')).hexdigest()

def load_state():
    """Loads the interceptor state JSON file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_state(state):
    """Saves the interceptor state JSON file."""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

def check_and_increment_retry(artifact_path, reset=False):
    """Checks retry count and increments it. Halts if exceeds MAX_RETRIES."""
    state = load_state()
    key = get_state_key(artifact_path)
    
    if reset or key not in state:
        state[key] = {"retry_count": 0}
    
    count = state[key]["retry_count"]
    
    if count >= MAX_RETRIES:
        # Reset count before halting to allow human intervention and restart
        state[key]["retry_count"] = 0
        save_state(state)
        throw_system_halt()
    
    state[key]["retry_count"] = count + 1
    save_state(state)
    return count + 1

def reset_retry(artifact_path):
    """Resets the retry count upon success."""
    state = load_state()
    key = get_state_key(artifact_path)
    if key in state:
        state[key]["retry_count"] = 0
        save_state(state)

def parse_persona(xml_path):
    """Parses the persona XML to extract forbidden tokens and schema."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"[SYSTEM 2 ERROR] Failed to parse Persona XML: {e}")
        sys.exit(1)

    forbidden_text = ""
    schema_text = ""

    # Search for Forbidden_Tokens and Output_Schema in the XML
    for elem in root.iter():
        if elem.tag == 'Forbidden_Tokens':
            forbidden_text = elem.text or ""
        elif elem.tag == 'Output_Schema':
            schema_text = elem.text or ""

    if not forbidden_text and not schema_text:
        print("[SYSTEM 2 WARNING] Found neither <Forbidden_Tokens> nor <Output_Schema> in the persona XML.")

    # Process forbidden tokens into a list of cleaned strings
    tokens = [t.strip().strip('"').strip("'") for t in forbidden_text.split(',') if t.strip()]
    return tokens, schema_text

def validate_artifact(artifact_path, forbidden_tokens, schema_text, model="default"):
    """Scans the artifact against forbidden tokens and schema requirements."""
    try:
        with open(artifact_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        throw_fatal_error(f"Cannot read artifact file: {e}")

    content_full = "".join(lines).strip()

    # 0. Thalamic Circuit Breaker: OOM Prevention (Adaptive Threshold)
    file_size = os.path.getsize(artifact_path)
    threshold = MODEL_THRESHOLDS.get(model, MODEL_THRESHOLDS["default"])
    
    if file_size > threshold:
        check_and_increment_retry(artifact_path)
        throw_fatal_error(
            f"[FATAL OOM PREVENTION: TRUNCATION REQUIRED]\n"
            f"Artifact size ({file_size} bytes) exceeds {model} threshold ({threshold} bytes).\n"
            f"The monolithic pipeline has entered a paradoxical loop or hallucination avalanche.\n"
            f"Circuit breaker tripped. You must truncate the context and degrade to a safe state."
        )

    # 1. Scanner: Check for Forbidden Tokens
    for line_num, line in enumerate(lines, 1):
        for token in forbidden_tokens:
            if not token:
                continue
            # Simple case-insensitive match. For robustness, regex bounds can be used.
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            if pattern.search(line):
                check_and_increment_retry(artifact_path)
                throw_fatal_error(
                    f"Violated Contract: <Forbidden_Tokens>\n"
                    f"Trigger Word: \"{token}\" found on Line {line_num}.\n"
                    f"Line Content: {line.strip()}"
                )

    # 2. Validator: Check Output Schema (Specific to Red Team Mathematician logic for now, 
    # but can be generalized based on the schema_text presence)
    # The XML states: Must output ONLY [VERDICT: APPROVE] or [VERDICT: REJECT] - Reason: ...
    if "VERDICT: APPROVE" in schema_text or "VERDICT: REJECT" in schema_text:
        is_approve = "[VERDICT: APPROVE]" in content_full
        is_reject = "[VERDICT: REJECT]" in content_full

        if is_approve and is_reject:
            check_and_increment_retry(artifact_path)
            throw_fatal_error(
                "Violated Contract: <Output_Schema>\n"
                "Artifact contains both APPROVE and REJECT verdicts. Must be strictly one."
            )
        
        if not is_approve and not is_reject:
            check_and_increment_retry(artifact_path)
            throw_fatal_error(
                "Violated Contract: <Output_Schema>\n"
                "Artifact must contain either [VERDICT: APPROVE] or [VERDICT: REJECT]."
            )
            
        # Optional: Strict enforcement that it shouldn't contain long conversational padding
        if is_approve and len(content_full) > 50:
             check_and_increment_retry(artifact_path)
             throw_fatal_error(
                "Violated Contract: <Output_Schema>\n"
                "Artifact contains excessive padding. When APPROVE, output ONLY [VERDICT: APPROVE]."
            )

    # If it passed everything
    reset_retry(artifact_path)
    print("\n[SYSTEM_VERIFICATION: PASSED]")
    print(f"Artifact {artifact_path} successfully passed the Execution Gate.\n")
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="System 2 Execution Gate Interceptor")
    parser.add_argument("--persona", required=True, help="Path to the Persona XML file.")
    parser.add_argument("--artifact", required=True, help="Path to the generated artifact file to verify.")
    parser.add_argument("--model", default="default", help="The target model to adapt context thresholds for.")
    parser.add_argument("--reset", action="store_true", help="Reset the circuit breaker retry counter.")
    
    args = parser.parse_args()

    if not os.path.exists(args.persona):
        print(f"[SYSTEM 2 ERROR] Persona file not found: {args.persona}")
        sys.exit(1)

    if args.reset:
        reset_retry(args.artifact)
        print(f"[SYSTEM 2 INFO] Retry counter reset for artifact: {args.artifact}")
        sys.exit(0)

    if not os.path.exists(args.artifact):
        print(f"[SYSTEM 2 ERROR] Artifact file not found: {args.artifact}")
        sys.exit(1)

    forbidden_tokens, schema_text = parse_persona(args.persona)
    validate_artifact(args.artifact, forbidden_tokens, schema_text, args.model)
