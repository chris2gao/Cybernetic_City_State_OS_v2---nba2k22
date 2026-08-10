import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import yaml
from typing import Any, Dict, List, Set

# Exit codes
EC_SUCCESS = 0
EC_PARSE_ERROR = 10
EC_TEST_ID_ISSUE = 11
EC_FAILURE_CODE_ISSUE = 12
EC_BINDING_ISSUE = 13
EC_BLOB_MISMATCH = 14
EC_CANDIDATE_DIGEST_MISMATCH = 15
EC_SEMANTIC_DIGEST_MISMATCH = 16

EXPECTED_BLOBS = {
    "测试组_01_消息与YAML_v1.yml": "2913280e9bced46055e2f4c39979758785aa4550",
    "测试组_02_序号角色权限引用_v1.yml": "2e761ae4df25b68f45289017f8fd78482ce80709",
    "测试组_03_上下文文档隐私发布_v1.yml": "95c0fbf1ef8d2e7fead99f5d0b15778af9b832b8",
    "测试组_04_Git收敛路由归档_v1.yml": "269418233b2edcaea0fcb58af835717982246323",
    "测试组_05_导航索引纠正跨端_v1.yml": "e3a2563da01344e9bd2f07842e70e8759b22d12c",
}

EXPECTED_CANDIDATE_DIGEST = "2bd1fb7237cbb95527b9cae75542c7e81a1412be393307b8b96b7c96a7c7a70b"
EXPECTED_SEMANTIC_DIGEST = "9b506c7b1d4b95f296ad398a9c4b4187ed135333a12cb59e236ed467366971e5"

VALID_EVIDENCE = {f"E-{i:02d}" for i in range(1, 11)}
VALID_CRITERIA = {f"AC-{i:02d}" for i in range(1, 10)}

def exit_with_finding(code: int, message: str, details: Any = None):
    finding = {
        "status": "error" if code != EC_SUCCESS else "success",
        "code": code,
        "message": message,
        "details": details or {}
    }
    print(json.dumps(finding, ensure_ascii=False, indent=2))
    sys.exit(code)

def compute_sha256(data: Any) -> str:
    dumped = yaml.safe_dump(data, allow_unicode=True, sort_keys=True, width=4096)
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()

def get_git_blob_hash(repo_root: Path, file_path: Path) -> str:
    try:
        # Use git hash-object to compute the blob SHA without needing it to be committed
        result = subprocess.run(
            ["git", "hash-object", str(file_path)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        exit_with_finding(EC_BLOB_MISMATCH, "Failed to compute git hash-object", {"error": str(e), "file": str(file_path)})
        return ""

def main():
    parser = argparse.ArgumentParser(description="Validate test candidate")
    parser.add_argument("--repo-root", required=True, type=str, help="Repository root path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    stage04_dir = repo_root / "08_os" / "_runs" / "run-20260805-全局通讯机制-001" / "04_测试生成"

    if not stage04_dir.exists():
        exit_with_finding(EC_PARSE_ERROR, f"Stage 04 directory not found: {stage04_dir}")

    candidate_file = stage04_dir / "冻结测试候选_v1.yml"
    specs_dir = stage04_dir / "specs"

    # 1. Parse candidate file
    try:
        with open(candidate_file, "r", encoding="utf-8") as f:
            candidate_data = yaml.safe_load(f)
    except Exception as e:
        exit_with_finding(EC_PARSE_ERROR, "Failed to parse candidate file", {"error": str(e)})

    # 2. Parse spec files and verify blobs
    spec_tests: List[Dict] = []
    
    for spec_name, expected_hash in EXPECTED_BLOBS.items():
        spec_file = specs_dir / spec_name
        if not spec_file.exists():
            exit_with_finding(EC_PARSE_ERROR, f"Spec file not found: {spec_name}")

        # Verify blob
        actual_hash = get_git_blob_hash(repo_root, spec_file)
        if actual_hash != expected_hash:
            exit_with_finding(EC_BLOB_MISMATCH, f"Git blob hash mismatch for {spec_name}", {
                "expected": expected_hash,
                "actual": actual_hash
            })

        # Parse
        try:
            with open(spec_file, "r", encoding="utf-8") as f:
                spec_data = yaml.safe_load(f)
                spec_tests.extend(spec_data.get("tests", []))
        except Exception as e:
            exit_with_finding(EC_PARSE_ERROR, f"Failed to parse spec file {spec_name}", {"error": str(e)})

    # 3. Verify test_ids (unique and sequential GC-T001 to GC-T050)
    expected_test_ids = [f"GC-T{i:03d}" for i in range(1, 51)]
    actual_test_ids = [t.get("test_id") for t in spec_tests]
    
    if len(actual_test_ids) != 50:
        exit_with_finding(EC_TEST_ID_ISSUE, "Expected 50 tests", {"actual_count": len(actual_test_ids)})
        
    actual_test_ids_sorted = sorted(actual_test_ids)
    if actual_test_ids_sorted != expected_test_ids:
        exit_with_finding(EC_TEST_ID_ISSUE, "Test IDs are not unique and sequential GC-T001 through GC-T050", {
            "missing": list(set(expected_test_ids) - set(actual_test_ids_sorted)),
            "extra": list(set(actual_test_ids_sorted) - set(expected_test_ids))
        })

    # 4. Verify failure codes (50 unique)
    failure_codes = [t.get("failure_code") for t in spec_tests if t.get("failure_code")]
    if len(set(failure_codes)) != 50:
        exit_with_finding(EC_FAILURE_CODE_ISSUE, "Expected 50 unique failure codes", {
            "total": len(failure_codes),
            "unique": len(set(failure_codes))
        })

    # 5. Verify bindings
    for t in spec_tests:
        test_id = t.get("test_id")
        
        # Verify bindings logic: tests usually have evidence_claim_ids and criterion_ids
        # They might be directly under the test or in a bindings section, assuming directly or metadata.
        # Requirements: Verify every test binds valid E-01 through E-10 evidence_claim_ids and AC-01 through AC-09 criterion_ids
        e_claims = t.get("evidence_claim_ids", [])
        c_ids = t.get("criterion_ids", [])
        
        if not isinstance(e_claims, list):
            exit_with_finding(EC_BINDING_ISSUE, f"Invalid evidence_claim_ids format in {test_id}", {"type": type(e_claims).__name__})
        if not isinstance(c_ids, list):
            exit_with_finding(EC_BINDING_ISSUE, f"Invalid criterion_ids format in {test_id}", {"type": type(c_ids).__name__})
            
        if not e_claims:
            exit_with_finding(EC_BINDING_ISSUE, f"No evidence_claim_ids bound in {test_id}")
        if not c_ids:
            exit_with_finding(EC_BINDING_ISSUE, f"No criterion_ids bound in {test_id}")

        invalid_e = [e for e in e_claims if e not in VALID_EVIDENCE]
        if invalid_e:
            exit_with_finding(EC_BINDING_ISSUE, f"Invalid evidence_claim_ids in {test_id}", {"invalid": invalid_e})
            
        invalid_c = [c for c in c_ids if c not in VALID_CRITERIA]
        if invalid_c:
            exit_with_finding(EC_BINDING_ISSUE, f"Invalid criterion_ids in {test_id}", {"invalid": invalid_c})

    # 6. Candidate Digest Match
    candidate_tests = candidate_data.get("tests", [])
    actual_candidate_digest = compute_sha256(candidate_tests)
    if actual_candidate_digest != EXPECTED_CANDIDATE_DIGEST:
        exit_with_finding(EC_CANDIDATE_DIGEST_MISMATCH, "Candidate index SHA256 mismatch", {
            "expected": EXPECTED_CANDIDATE_DIGEST,
            "actual": actual_candidate_digest
        })

    # 7. Semantic Specs Digest Match
    sorted_spec_tests = sorted(spec_tests, key=lambda x: x.get("test_id", ""))
    actual_semantic_digest = compute_sha256(sorted_spec_tests)
    if actual_semantic_digest != EXPECTED_SEMANTIC_DIGEST:
        exit_with_finding(EC_SEMANTIC_DIGEST_MISMATCH, "Semantic specs SHA256 mismatch", {
            "expected": EXPECTED_SEMANTIC_DIGEST,
            "actual": actual_semantic_digest
        })

    exit_with_finding(EC_SUCCESS, "Validation passed")

if __name__ == "__main__":
    main()
