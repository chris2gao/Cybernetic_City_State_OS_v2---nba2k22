#!/usr/bin/env python3
import sys
import argparse
import hashlib
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Callable, List, Tuple
import yaml
import traceback
import os
import atexit
TEMP_DIRS = []
_ORIGINAL_CHECK_CALL = subprocess.check_call
def _quiet_check_call(*args, **kwargs):
    """Keep child-process chatter out of runner-generated YAML evidence."""
    kwargs.setdefault("stdout", subprocess.DEVNULL)
    kwargs.setdefault("stderr", subprocess.PIPE)
    return _ORIGINAL_CHECK_CALL(*args, **kwargs)
subprocess.check_call = _quiet_check_call

def _git_test_env() -> Dict[str, str]:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@example.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@example.com"
    return env

def cleanup_temp_dirs():
    for d in TEMP_DIRS:
        shutil.rmtree(d, ignore_errors=True)
atexit.register(cleanup_temp_dirs)
def setup_git_repos():
    base_dir = tempfile.mkdtemp()
    TEMP_DIRS.append(base_dir)
    remote_dir = os.path.join(base_dir, "remote.git")
    local_dir = os.path.join(base_dir, "local")
    
    subprocess.check_call(["git", "init", "--bare", remote_dir])
    subprocess.check_call(["git", "clone", remote_dir, local_dir])
    
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@example.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@example.com"
    
    with open(os.path.join(local_dir, "README.md"), "w") as f:
        f.write("init")
    subprocess.check_call(["git", "add", "README.md"], cwd=local_dir, env=env)
    subprocess.check_call(["git", "branch", "-M", "master"], cwd=local_dir, env=env)
    subprocess.check_call(["git", "commit", "-m", "init"], cwd=local_dir, env=env)
    subprocess.check_call(["git", "push", "origin", "master"], cwd=local_dir, env=env)
        
    return local_dir, remote_dir
class TestCase:
    def __init__(
        self,
        test_id: str,
        failure_code: str,
        fixture_factory: Callable[[str, Path, str, Dict[str, Any]], Any],
        action: Callable[[Any, Any], None],
        evaluator: Callable[[Exception, Any], None]
    ):
        self.test_id = test_id
        self.failure_code = failure_code
        self.fixture_factory = fixture_factory
        self.action = action
        self.evaluator = evaluator
TESTS = []
def verify_specs(root: Path) -> Tuple[bool, str]:
    stage04_root = root / "08_os/_runs/run-20260805-全局通讯机制-001/04_测试生成"
    
    # 1. Load candidate map
    candidate_path = stage04_root / "冻结测试候选_v1.yml"
    try:
        with open(candidate_path, encoding='utf-8') as fp:
            candidate_data = yaml.safe_load(fp)
            candidate_map = {t['test_id']: t['failure_code'] for t in candidate_data.get('tests', [])}
    except Exception as e:
        return False, f"Failed to load candidate: {e}"
    # 2. Load specs map
    specs_dir = stage04_root / "specs"
    spec_files = sorted(list(specs_dir.glob("*.yml")))
    spec_map = {}
    for f in spec_files:
        with open(f, encoding='utf-8') as fp:
            data = yaml.safe_load(fp)
            for t in data.get('tests', []):
                if t['test_id'] in spec_map:
                    return False, f"Duplicate test_id in specs: {t['test_id']}"
                spec_map[t['test_id']] = t['failure_code']
                
    # 3. Load runner map
    runner_map = {t.test_id: t.failure_code for t in TESTS}
    # Verify counts
    if len(candidate_map) != 50:
        return False, f"Expected 50 cases in candidate, found {len(candidate_map)}"
    if len(spec_map) != 50:
        return False, f"Expected 50 cases in specs, found {len(spec_map)}"
    if len(runner_map) != 50:
        return False, f"Expected 50 cases in runner, found {len(runner_map)}"
        
    for i in range(1, 51):
        tid = f"GC-T{i:03d}"
        if tid not in candidate_map:
            return False, f"Missing {tid} in candidate"
            
    if candidate_map != spec_map:
        return False, "Candidate map does not exactly match specs map"
    if spec_map != runner_map:
        return False, "Specs map does not exactly match runner map"
        
    return True, "Candidate, Specs, and Runner perfectly aligned"
def fix_GC_T001(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "requested_action": "do", "required_refs": []}
    if mode == "mutation-suite": fix.pop("endpoint_id")
    return fix
def act_GC_T001(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T001(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Missing endpoint" in str(exc): raise ValueError("VALID_MESSAGE_REQUIRED")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T001", "VALID_MESSAGE_REQUIRED", fix_GC_T001, act_GC_T001, eval_GC_T001))
def fix_GC_T002(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["synthesize_action"] = True
    return fix
def act_GC_T002(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T002(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Synthesized action not allowed" in str(exc): raise ValueError("RESULT_OPTIONAL_ACTION")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T002", "RESULT_OPTIONAL_ACTION", fix_GC_T002, act_GC_T002, eval_GC_T002))
def fix_GC_T003(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "requested_action": "do", "required_refs": []}
    if mode == "mutation-suite":
        fix.pop("requested_action")
        fix["missing_requested_action_test"] = True
    return fix
def act_GC_T003(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T003(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Missing requested action" in str(exc): raise ValueError("REQUESTED_ACTION_REQUIRED")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T003", "REQUESTED_ACTION_REQUIRED", fix_GC_T003, act_GC_T003, eval_GC_T003))
def fix_GC_T004(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    yaml_str = "endpoint_id: test\nrole: info\n"
    if mode == "mutation-suite": yaml_str += "role: duplicate\n"
    return yaml_str
def act_GC_T004(adapter, fix_data):
    adapter.parse_yaml(fix_data)
def eval_GC_T004(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Duplicate key found" in str(exc): raise ValueError("YAML_DUPLICATE_KEY")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T004", "YAML_DUPLICATE_KEY", fix_GC_T004, act_GC_T004, eval_GC_T004))
def fix_GC_T005(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    yaml_str = "endpoint_id: test\nrole: info\n"
    if mode == "mutation-suite": yaml_str += "---\nrole: second\n"
    return yaml_str
def act_GC_T005(adapter, fix_data):
    adapter.parse_yaml(fix_data)
def eval_GC_T005(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Multiple documents found" in str(exc): raise ValueError("YAML_MULTI_DOCUMENT")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T005", "YAML_MULTI_DOCUMENT", fix_GC_T005, act_GC_T005, eval_GC_T005))
def fix_GC_T006(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    base = "endpoint_id: test\nrole: info\n"
    if mode == "mutation-suite":
        return [
            base + "anchor: &A value\n",
            base + "anchor_base: &A value\nalias: *A\n",
            base + "anchor_base: &A {k: v}\n<<: *A\n"
        ]
    return [base]
def act_GC_T006(adapter, fix_data):
    if not isinstance(fix_data, list):
        adapter.parse_yaml(fix_data)
        return
        
    if len(fix_data) == 1:
        adapter.parse_yaml(fix_data[0])
        return
    exceptions = []
    for f in fix_data:
        try:
            adapter.parse_yaml(f)
        except Exception as e:
            exceptions.append(e)
            
    if len(exceptions) == len(fix_data):
        raise ValueError(" || ".join(str(e) for e in exceptions))
    else:
        raise ValueError(f"Only {len(exceptions)} of {len(fix_data)} mutations were rejected")
def eval_GC_T006(exc: Exception, fix_data):
    if exc is None: return
    msg = str(exc)
    if "Stage 06" in msg:
        raise ValueError("EXPECTED_FAIL_STAGE06")
    
    parts = msg.split(" || ")
    if all("Alias or merge key found" in p for p in parts):
        raise ValueError("YAML_ALIAS_OR_MERGE")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T006", "YAML_ALIAS_OR_MERGE", fix_GC_T006, act_GC_T006, eval_GC_T006))
def fix_GC_T007(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    yaml_str = "endpoint_id: test\nrole: info\n"
    if mode == "mutation-suite": yaml_str += "custom: !!python/object/apply:os.system ['ls']\n"
    return yaml_str
def act_GC_T007(adapter, fix_data):
    adapter.parse_yaml(fix_data)
def eval_GC_T007(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Custom tag found" in str(exc): raise ValueError("YAML_CUSTOM_TAG")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T007", "YAML_CUSTOM_TAG", fix_GC_T007, act_GC_T007, eval_GC_T007))
def fix_GC_T008(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["delivered"] = True
    return fix
def act_GC_T008(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T008(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Delivery state fields are not allowed" in str(exc): raise ValueError("PROHIBITED_DELIVERY_STATE")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T008", "PROHIBITED_DELIVERY_STATE", fix_GC_T008, act_GC_T008, eval_GC_T008))
def fix_GC_T009(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["summary"] = 'test'
    return fix
def act_GC_T009(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T009(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Summary field is prohibited" in str(exc): raise ValueError("PROHIBITED_SUMMARY_FIELD")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T009", "PROHIBITED_SUMMARY_FIELD", fix_GC_T009, act_GC_T009, eval_GC_T009))
def fix_GC_T010(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["sequence_mismatch"] = True
    return fix
def act_GC_T010(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T010(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Message ID does not match path" in str(exc): raise ValueError("MESSAGE_ID_PATH_MISMATCH")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T010", "MESSAGE_ID_PATH_MISMATCH", fix_GC_T010, act_GC_T010, eval_GC_T010))
def fix_GC_T011(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text"}
    if mode == "mutation-suite": fix["reuse_sequence"] = True
    return fix
def act_GC_T011(adapter, fix_data):
    adapter.publish_message(fix_data)
def eval_GC_T011(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Sequence number already in use" in str(exc): raise ValueError("SEQUENCE_REUSE")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T011", "SEQUENCE_REUSE", fix_GC_T011, act_GC_T011, eval_GC_T011))
def fix_GC_T012(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text"}
    if mode == "mutation-suite": fix["sequence"] = 10001
    return fix
def act_GC_T012(adapter, fix_data):
    adapter.publish_message(fix_data)
def eval_GC_T012(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Sequence numbers exhausted" in str(exc): raise ValueError("SEQUENCE_EXHAUSTED")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T012", "SEQUENCE_EXHAUSTED", fix_GC_T012, act_GC_T012, eval_GC_T012))
def fix_GC_T013(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text"}
    if mode == "mutation-suite": fix["task_scoped"] = True
    return fix
def act_GC_T013(adapter, fix_data):
    adapter.publish_message(fix_data)
def eval_GC_T013(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Sequence is not scoped to task properly" in str(exc): raise ValueError("TASK_SCOPED_SEQUENCE")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T013", "TASK_SCOPED_SEQUENCE", fix_GC_T013, act_GC_T013, eval_GC_T013))
def fix_GC_T014(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text"}
    if mode == "mutation-suite": fix["wrong_zone"] = True
    return fix
def act_GC_T014(adapter, fix_data):
    adapter.publish_message(fix_data)
def eval_GC_T014(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Cannot publish to another sender zone" in str(exc): raise ValueError("SENDER_ZONE_OWNERSHIP")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T014", "SENDER_ZONE_OWNERSHIP", fix_GC_T014, act_GC_T014, eval_GC_T014))
def fix_GC_T015(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["role"] = 'invalid_role'
    return fix
def act_GC_T015(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T015(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Role does not match endpoint" in str(exc): raise ValueError("ENDPOINT_ROLE_MISMATCH")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T015", "ENDPOINT_ROLE_MISMATCH", fix_GC_T015, act_GC_T015, eval_GC_T015))
def fix_GC_T016(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["role"] = 'architecture_and_decision'
    return fix
def act_GC_T016(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T016(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Role lacks authority" in str(exc): raise ValueError("ROLE_IS_NOT_AUTHORITY")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T016", "ROLE_IS_NOT_AUTHORITY", fix_GC_T016, act_GC_T016, eval_GC_T016))
def fix_GC_T017(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["authorization_ref"] = 'some_ref'
    return fix
def act_GC_T017(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T017(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Authorization ref provided but not required" in str(exc): raise ValueError("AUTH_REF_NOT_REQUIRED")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T017", "AUTH_REF_NOT_REQUIRED", fix_GC_T017, act_GC_T017, eval_GC_T017))
def fix_GC_T018(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["self_authorization"] = True
    return fix
def act_GC_T018(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T018(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Cannot self-authorize" in str(exc): raise ValueError("MESSAGE_SELF_AUTHORIZATION")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T018", "MESSAGE_SELF_AUTHORIZATION", fix_GC_T018, act_GC_T018, eval_GC_T018))
def fix_GC_T019(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["missing_ref"] = True
    return fix
def act_GC_T019(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T019(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "A required reference is missing" in str(exc): raise ValueError("REQUIRED_REF_MISSING")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T019", "REQUIRED_REF_MISSING", fix_GC_T019, act_GC_T019, eval_GC_T019))
def fix_GC_T020(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["set_mismatch"] = True
    return fix
def act_GC_T020(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T020(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Required ref set mismatch" in str(exc): raise ValueError("REQUIRED_REF_SET_MISMATCH")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T020", "REQUIRED_REF_SET_MISMATCH", fix_GC_T020, act_GC_T020, eval_GC_T020))
def fix_GC_T021(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["context_expansion"] = True
    return fix
def act_GC_T021(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T021(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Unauthorized context expansion" in str(exc): raise ValueError("UNAUTHORIZED_CONTEXT_EXPANSION")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T021", "UNAUTHORIZED_CONTEXT_EXPANSION", fix_GC_T021, act_GC_T021, eval_GC_T021))
def fix_GC_T022(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["bootstrap_read"] = True
    return fix
def act_GC_T022(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T022(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Bootstrap read set is invalid" in str(exc): raise ValueError("BOOTSTRAP_READ_SET")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T022", "BOOTSTRAP_READ_SET", fix_GC_T022, act_GC_T022, eval_GC_T022))
def fix_GC_T023(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["long_content"] = True
    return fix
def act_GC_T023(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T023(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Content too long to externalize" in str(exc): raise ValueError("LONG_CONTENT_EXTERNALIZATION")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T023", "LONG_CONTENT_EXTERNALIZATION", fix_GC_T023, act_GC_T023, eval_GC_T023))
def fix_GC_T024(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["front_matter"] = False
    return fix
def act_GC_T024(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T024(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Document front matter is missing" in str(exc): raise ValueError("DOCUMENT_FRONT_MATTER_REQUIRED")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T024", "DOCUMENT_FRONT_MATTER_REQUIRED", fix_GC_T024, act_GC_T024, eval_GC_T024))
def fix_GC_T025(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["existing_resource"] = True
    return fix
def act_GC_T025(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T025(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Invalid existing resource reference" in str(exc): raise ValueError("EXISTING_RESOURCE_REFERENCE")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T025", "EXISTING_RESOURCE_REFERENCE", fix_GC_T025, act_GC_T025, eval_GC_T025))
def fix_GC_T026(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text"}
    if mode == "mutation-suite": fix["local_only"] = True
    return fix
def act_GC_T026(adapter, fix_data):
    adapter.publish_message(fix_data)
def eval_GC_T026(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Local only content blocked from GitHub" in str(exc): raise ValueError("LOCAL_ONLY_GITHUB_BLOCK")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T026", "LOCAL_ONLY_GITHUB_BLOCK", fix_GC_T026, act_GC_T026, eval_GC_T026))
def fix_GC_T027(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["forbidden_data"] = True
    return fix
def act_GC_T027(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T027(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Forbidden data found" in str(exc): raise ValueError("FORBIDDEN_DATA")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T027", "FORBIDDEN_DATA", fix_GC_T027, act_GC_T027, eval_GC_T027))
def fix_GC_T028(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["local_default"] = True
    return fix
def act_GC_T028(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T028(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Local default route violated" in str(exc): raise ValueError("LOCAL_DEFAULT_ROUTE")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T028", "LOCAL_DEFAULT_ROUTE", fix_GC_T028, act_GC_T028, eval_GC_T028))
def fix_GC_T029(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["web_repub"] = True
    return fix
def act_GC_T029(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T029(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Web republication required" in str(exc): raise ValueError("WEB_REPUBLICATION_REQUIRED")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T029", "WEB_REPUBLICATION_REQUIRED", fix_GC_T029, act_GC_T029, eval_GC_T029))
def fix_GC_T030(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text"}
    if mode == "mutation-suite": fix["human_github"] = True
    return fix
def act_GC_T030(adapter, fix_data):
    adapter.publish_message(fix_data)
def eval_GC_T030(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Human GitHub trigger failed" in str(exc): raise ValueError("HUMAN_GITHUB_TRIGGER")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T030", "HUMAN_GITHUB_TRIGGER", fix_GC_T030, act_GC_T030, eval_GC_T030))
def fix_GC_T031(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    local_dir, remote_dir = setup_git_repos()
    
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@example.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@example.com"
    
    other_local = tempfile.mkdtemp()
    TEMP_DIRS.append(other_local)
    subprocess.check_call(["git", "clone", remote_dir, other_local])
    with open(os.path.join(other_local, "file1.txt"), "w") as f:
        f.write("remote")
    subprocess.check_call(["git", "add", "."], cwd=other_local, env=env)
    subprocess.check_call(["git", "commit", "-m", "remote ahead"], cwd=other_local, env=env)
    subprocess.check_call(["git", "push", "origin", "master"], cwd=other_local, env=env)
    
    with open(os.path.join(local_dir, "local.txt"), "w") as f:
        f.write("local")
    subprocess.check_call(["git", "add", "."], cwd=local_dir, env=env)
    subprocess.check_call(["git", "commit", "-m", "local"], cwd=local_dir, env=env)
    action = "pull_rebase_push"
    if mode == "mutation-suite":
        action = "bad_convergence_lose_local"
        
    return {"scenario": "GC-T031", "repo_path": local_dir, "action": action}
def act_GC_T031(adapter, fix_data):
    adapter.run_git_scenario(fix_data)
def eval_GC_T031(exc: Exception, fix_data):
    if exc is not None:
        if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
            raise ValueError("EXPECTED_FAIL_STAGE06")
        raise ValueError(f"Unrelated exception: {exc}")
    if fix_data.get("scenario") != "GC-T031":
        raise ValueError("Unrelated fixture")
        
    repo = fix_data["repo_path"]
    local_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo).decode("utf-8").strip()
    remote_head = subprocess.check_output(["git", "rev-parse", "origin/master"], cwd=repo).decode("utf-8").strip()
    
    if local_head != remote_head:
        raise ValueError("GIT_CONVERGENCE")
        
    if not os.path.exists(os.path.join(repo, "local.txt")):
        raise ValueError("GIT_CONVERGENCE")
TESTS.append(TestCase("GC-T031", "GIT_CONVERGENCE", fix_GC_T031, act_GC_T031, eval_GC_T031))
def fix_GC_T032(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    local_dir, remote_dir = setup_git_repos()
    
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@example.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@example.com"
    
    other_local = tempfile.mkdtemp()
    TEMP_DIRS.append(other_local)
    subprocess.check_call(["git", "clone", remote_dir, other_local])
    os.makedirs(os.path.join(other_local, "dir_A"))
    with open(os.path.join(other_local, "dir_A", "file.txt"), "w") as f:
        f.write("A")
    subprocess.check_call(["git", "add", "."], cwd=other_local, env=env)
    subprocess.check_call(["git", "commit", "-m", "A"], cwd=other_local, env=env)
    subprocess.check_call(["git", "push", "origin", "master"], cwd=other_local, env=env)
    
    os.makedirs(os.path.join(local_dir, "dir_B"))
    with open(os.path.join(local_dir, "dir_B", "file.txt"), "w") as f:
        f.write("B")
    subprocess.check_call(["git", "add", "."], cwd=local_dir, env=env)
    subprocess.check_call(["git", "commit", "-m", "B"], cwd=local_dir, env=env)
    
    action = "pull_rebase_push"
    if mode == "mutation-suite":
        action = "bad_disjoint_convergence"
        
    return {"scenario": "GC-T032", "repo_path": local_dir, "action": action}
def act_GC_T032(adapter, fix_data):
    adapter.run_git_scenario(fix_data)
def eval_GC_T032(exc: Exception, fix_data):
    if exc is not None:
        if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
            raise ValueError("EXPECTED_FAIL_STAGE06")
        raise ValueError(f"Unrelated exception: {exc}")
    if fix_data.get("scenario") != "GC-T032":
        raise ValueError("Unrelated fixture")
        
    repo = fix_data["repo_path"]
    if not os.path.exists(os.path.join(repo, "dir_A", "file.txt")) or not os.path.exists(os.path.join(repo, "dir_B", "file.txt")):
        raise ValueError("DISJOINT_SENDER_CONVERGENCE")
TESTS.append(TestCase("GC-T032", "DISJOINT_SENDER_CONVERGENCE", fix_GC_T032, act_GC_T032, eval_GC_T032))
def _make_GC_T033_fixture(mode: str) -> Dict[str, Any]:
    base = tempfile.mkdtemp()
    TEMP_DIRS.append(base)
    remote = os.path.join(base, "remote")
    local = os.path.join(base, "local")
    os.makedirs(remote)
    
    env = _git_test_env()
    
    subprocess.check_call(["git", "init", "--bare", remote])
    subprocess.check_call(["git", "clone", remote, local])
    
    with open(os.path.join(local, "README.md"), "w") as f: f.write("base\\n")
    subprocess.check_call(["git", "add", "README.md"], cwd=local)
    subprocess.check_call(["git", "commit", "-m", "init"], cwd=local, env=env)
    subprocess.check_call(["git", "push", "origin", "master"], cwd=local)
    
    local2 = os.path.join(base, "local2")
    subprocess.check_call(["git", "clone", remote, local2])
    with open(os.path.join(local2, "README.md"), "w") as f: f.write("remote update\\n")
    subprocess.check_call(["git", "add", "README.md"], cwd=local2)
    subprocess.check_call(["git", "commit", "-m", "remote"], cwd=local2, env=env)
    subprocess.check_call(["git", "push", "origin", "master"], cwd=local2)
    
    with open(os.path.join(local, "README.md"), "w") as f: f.write("local update\\n")
    subprocess.check_call(["git", "add", "README.md"], cwd=local)
    subprocess.check_call(["git", "commit", "-m", "local"], cwd=local, env=env)
    
    return {"scenario": "GC-T033", "base_dir": base, "repo_path": local,
            "remote_path": remote, "actor_path": local2, "mode": mode}

def fix_GC_T033(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    return _make_GC_T033_fixture(mode)

def act_GC_T033(adapter, fix_data):
    if fix_data.get("scenario") != "GC-T033":
        raise ValueError("GC-T033 received an unrelated fixture")
    if fix_data["mode"] == "mutation-suite":
        fix_data["subcases"] = []
        for mutation in ("auto_resolve_and_continue", "push_after_conflict",
                         "omit_exact_conflict_path", "omit_required_escalation"):
            case = _make_GC_T033_fixture("mutation-suite")
            request = dict(case)
            request["mutation"] = mutation
            observation = adapter.run_git_scenario(request)
            fix_data["subcases"].append({
                "fixture_root": case["base_dir"],
                "observation": observation,
            })
    else:
        request = dict(fix_data)
        request["mutation"] = None
        fix_data["observation"] = adapter.run_git_scenario(request)

def _GC_T033_conforms(observation: Dict[str, Any]) -> bool:
    if not isinstance(observation, dict):
        return False
    observed = observation.get("observed_unresolved_paths") or []
    emitted = observation.get("emitted_conflict_paths") or []
    return (
        observation.get("merge_return_code", 0) != 0
        and bool(observed)
        and emitted == observed
        and observation.get("continuation_commit_created") is False
        and observation.get("push_attempt_count") == 0
        and observation.get("operation_stopped") is True
        and observation.get("next_owner") == "task_navigation_owner"
        and observation.get("Human_escalation_required") is True
    )

def eval_GC_T033(exc: Exception, fix_data):
    if exc and ("Stage 06" in str(exc) or isinstance(exc, NotImplementedError)):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc is not None:
        raise ValueError(f"Unrelated exception: {exc}")
    if fix_data.get("mode") == "mutation-suite":
        cases = fix_data.get("subcases") or []
        roots = [case.get("fixture_root") for case in cases]
        if len(cases) != 4 or len(set(roots)) != 4:
            raise ValueError("GC-T033 negative subcases were not independently initialized")
        if any(_GC_T033_conforms(case.get("observation")) for case in cases):
            raise ValueError("GC-T033 negative subcase escaped the physical oracle")
        raise ValueError("SAME_PATH_CONFLICT")
    if not _GC_T033_conforms(fix_data.get("observation")):
        raise ValueError("SAME_PATH_CONFLICT")
def _make_GC_T034_fixture(mode: str) -> Dict[str, Any]:
    base = tempfile.mkdtemp()
    TEMP_DIRS.append(base)
    remote = os.path.join(base, "remote")
    local = os.path.join(base, "local")
    os.makedirs(remote)
    
    env = _git_test_env()
    
    subprocess.check_call(["git", "init", "--bare", remote])
    subprocess.check_call(["git", "clone", remote, local])
    
    with open(os.path.join(local, "file.txt"), "w") as f: f.write("base")
    subprocess.check_call(["git", "add", "file.txt"], cwd=local)
    subprocess.check_call(["git", "commit", "-m", "init"], cwd=local, env=env)
    subprocess.check_call(["git", "push", "origin", "master"], cwd=local)
    
    local2 = os.path.join(base, "local2")
    subprocess.check_call(["git", "clone", remote, local2])
    with open(os.path.join(local2, "file.txt"), "w") as f: f.write("remote update")
    subprocess.check_call(["git", "add", "file.txt"], cwd=local2)
    subprocess.check_call(["git", "commit", "-m", "remote"], cwd=local2, env=env)
    subprocess.check_call(["git", "push", "origin", "master"], cwd=local2)
    
    with open(os.path.join(local, "file2.txt"), "w") as f: f.write("local update")
    subprocess.check_call(["git", "add", "file2.txt"], cwd=local)
    subprocess.check_call(["git", "commit", "-m", "local"], cwd=local, env=env)
    
    return {"scenario": "GC-T034", "base_dir": base, "repo_path": local,
            "remote_path": remote, "actor_path": local2, "mode": mode}

def fix_GC_T034(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    return _make_GC_T034_fixture(mode)

def act_GC_T034(adapter, fix_data):
    if fix_data.get("scenario") != "GC-T034":
        raise ValueError("GC-T034 received an unrelated fixture")
    if fix_data["mode"] == "mutation-suite":
        fix_data["subcases"] = []
        for mutation in ("force_push", "automatic_retry", "remote_head_changes", "escalation_missing"):
            case = _make_GC_T034_fixture("mutation-suite")
            request = dict(case)
            request["mutation"] = mutation
            observation = adapter.run_git_scenario(request)
            fix_data["subcases"].append({
                "fixture_root": case["base_dir"],
                "observation": observation,
            })
    else:
        request = dict(fix_data)
        request["mutation"] = None
        fix_data["observation"] = adapter.run_git_scenario(request)

def _GC_T034_conforms(observation: Dict[str, Any]) -> bool:
    if not isinstance(observation, dict):
        return False
    attempts = observation.get("push_attempts") or []
    if len(attempts) != 1:
        return False
    return (
        attempts[0].get("return_code", 0) != 0
        and attempts[0].get("argv") == ["git", "push", "origin", "master"]
        and observation.get("retry_count") == 0
        and observation.get("remote_head_before") == observation.get("remote_head_after")
        and observation.get("route") == ["task_navigation_owner", "Human"]
    )

def eval_GC_T034(exc: Exception, fix_data):
    if exc and ("Stage 06" in str(exc) or isinstance(exc, NotImplementedError)):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc is not None:
        raise ValueError(f"Unrelated exception: {exc}")
    if fix_data.get("mode") == "mutation-suite":
        cases = fix_data.get("subcases") or []
        roots = [case.get("fixture_root") for case in cases]
        if len(cases) != 4 or len(set(roots)) != 4:
            raise ValueError("GC-T034 negative subcases were not independently initialized")
        if any(_GC_T034_conforms(case.get("observation")) for case in cases):
            raise ValueError("GC-T034 negative subcase escaped the physical oracle")
        raise ValueError("NON_FAST_FORWARD")
    if not _GC_T034_conforms(fix_data.get("observation")):
        raise ValueError("NON_FAST_FORWARD")
def fix_GC_T035(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["dangling_pointer"] = True
    return fix
def act_GC_T035(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T035(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Dangling pointer prevented" in str(exc): raise ValueError("DANGLING_POINTER_PREVENTED")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T035", "DANGLING_POINTER_PREVENTED", fix_GC_T035, act_GC_T035, eval_GC_T035))
def fix_GC_T036(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["route_override"] = True
    return fix
def act_GC_T036(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T036(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Human route override failed" in str(exc): raise ValueError("HUMAN_ROUTE_OVERRIDE")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T036", "HUMAN_ROUTE_OVERRIDE", fix_GC_T036, act_GC_T036, eval_GC_T036))
def fix_GC_T037(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["sent_scope"] = True
    return fix
def act_GC_T037(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T037(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Sent scope violation" in str(exc): raise ValueError("SENT_SCOPE")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T037", "SENT_SCOPE", fix_GC_T037, act_GC_T037, eval_GC_T037))
def fix_GC_T038(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["auto_delivery"] = True
    return fix
def act_GC_T038(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T038(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Automatic delivery prohibited" in str(exc): raise ValueError("AUTOMATIC_DELIVERY_PROHIBITED")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T038", "AUTOMATIC_DELIVERY_PROHIBITED", fix_GC_T038, act_GC_T038, eval_GC_T038))
def _make_GC_T039_fixture(mode: str) -> Dict[str, Any]:
    base = tempfile.mkdtemp()
    TEMP_DIRS.append(base)
    task_dir = os.path.join(base, "active_task")
    folders = ["indexes", "messages", "documents", "Human_decisions", "final_results", "material_failures"]
    for fldr in folders:
        os.makedirs(os.path.join(task_dir, fldr))
        with open(os.path.join(task_dir, fldr, f"file_{fldr}.txt"), "w") as f: f.write("data")
    
    with open(os.path.join(base, "discovery.yml"), "w") as f: yaml.dump({"roots": ["/active_task"]}, f)
    
    return {"scenario": "GC-T039", "base_dir": base, "task_dir": task_dir,
            "archive_dir": os.path.join(base, "archived_task"), "mode": mode}

def fix_GC_T039(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    return _make_GC_T039_fixture(mode)

def act_GC_T039(adapter, fix_data):
    if fix_data.get("scenario") != "GC-T039":
        raise ValueError("GC-T039 received an unrelated fixture")
    if fix_data["mode"] == "mutation-suite":
        fix_data["subcases"] = []
        for mutation in ("omit_public_history_category", "fail_to_update_discovery"):
            case = _make_GC_T039_fixture("mutation-suite")
            request = dict(case)
            request["mutation"] = mutation
            adapter.archive_task(request)
            fix_data["subcases"].append(case)
    else:
        request = dict(fix_data)
        request["mutation"] = None
        adapter.archive_task(request)

def _GC_T039_conforms(fix_data: Dict[str, Any]) -> bool:
    task_dir = fix_data["task_dir"]
    archive_dir = fix_data["archive_dir"]
    if os.path.exists(task_dir) or not os.path.isdir(archive_dir):
        return False
    folders = ["indexes", "messages", "documents", "Human_decisions",
               "final_results", "material_failures"]
    if any(not os.path.isfile(os.path.join(archive_dir, folder, f"file_{folder}.txt"))
           for folder in folders):
        return False
    discovery_path = os.path.join(fix_data["base_dir"], "discovery.yml")
    with open(discovery_path, "r", encoding="utf-8") as stream:
        discovery = yaml.safe_load(stream)
    return (
        isinstance(discovery, dict)
        and discovery.get("roots") == ["/archived_task"]
        and set(discovery) == {"roots"}
    )

def eval_GC_T039(exc: Exception, fix_data):
    if exc and ("Stage 06" in str(exc) or isinstance(exc, NotImplementedError)):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc is not None:
        raise ValueError(f"Unrelated exception: {exc}")
    if fix_data.get("mode") == "mutation-suite":
        cases = fix_data.get("subcases") or []
        roots = [case.get("base_dir") for case in cases]
        if len(cases) != 2 or len(set(roots)) != 2:
            raise ValueError("GC-T039 negative subcases were not independently initialized")
        if any(_GC_T039_conforms(case) for case in cases):
            raise ValueError("GC-T039 negative subcase escaped the physical oracle")
        raise ValueError("WHOLE_TASK_ARCHIVE")
    if not _GC_T039_conforms(fix_data):
        raise ValueError("WHOLE_TASK_ARCHIVE")

def _make_GC_T040_fixture(mode: str) -> Dict[str, Any]:
    base = tempfile.mkdtemp()
    TEMP_DIRS.append(base)
    external_runtime = tempfile.mkdtemp()
    TEMP_DIRS.append(external_runtime)
    task_dir = os.path.join(base, "active_task")
    archive_dir = os.path.join(base, "archived_task")
    os.makedirs(task_dir)
    env = _git_test_env()
    subprocess.check_call(["git", "init"], cwd=base)
    os.makedirs(os.path.join(task_dir, "private_runtime"))
    os.makedirs(os.path.join(task_dir, "_runtime"))
    with open(os.path.join(task_dir, "private_runtime", "sentinel.txt"), "w") as f: f.write("private")
    with open(os.path.join(task_dir, "_runtime", "sentinel.txt"), "w") as f: f.write("ignored")
    with open(os.path.join(external_runtime, "sentinel.txt"), "w") as f: f.write("external")
    with open(os.path.join(base, ".gitignore"), "w") as f:
        f.write("active_task/private_runtime/\nactive_task/_runtime/\n")
    with open(os.path.join(task_dir, "public_results.yml"), "w") as f: f.write("results\n")
    subprocess.check_call(["git", "add", ".gitignore", "active_task/public_results.yml"], cwd=base)
    subprocess.check_call(["git", "commit", "-m", "init"], cwd=base, env=env)
    return {
        "scenario": "GC-T040",
        "base_dir": base,
        "task_dir": task_dir,
        "archive_dir": archive_dir,
        "external_runtime": external_runtime,
        "mode": mode,
        "operation_trace": [],
        "durable_prerequisite_observed": False,
    }

def fix_GC_T040(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    return _make_GC_T040_fixture(mode)

def act_GC_T040(adapter, fix_data):
    if fix_data.get("scenario") != "GC-T040":
        raise ValueError("GC-T040 received an unrelated fixture")
    if fix_data["mode"] == "mutation-suite":
        fix_data["subcases"] = []
        for mutation in ("private_runtime_leaks_into_archive",
                         "private_runtime_becomes_git_tracked",
                         "private_runtime_deleted_before_durable_prerequisite"):
            case = _make_GC_T040_fixture("mutation-suite")
            request = dict(case)
            request["mutation"] = mutation
            adapter.archive_task(request)
            case["operation_trace"] = request["operation_trace"]
            case["durable_prerequisite_observed"] = request["durable_prerequisite_observed"]
            fix_data["subcases"].append(case)
    else:
        request = dict(fix_data)
        request["mutation"] = None
        adapter.archive_task(request)
        fix_data["operation_trace"] = request["operation_trace"]
        fix_data["durable_prerequisite_observed"] = request["durable_prerequisite_observed"]

def _GC_T040_conforms(fix_data: Dict[str, Any]) -> bool:
    archive_dir = fix_data["archive_dir"]
    tracked = subprocess.check_output(
        ["git", "ls-files"], cwd=fix_data["base_dir"]
    ).decode("utf-8").splitlines()
    trace = fix_data.get("operation_trace") or []
    try:
        gate_index = trace.index("durable_prerequisite_verified")
        deletion_index = trace.index("private_runtime_deleted")
    except ValueError:
        return False
    return (
        fix_data.get("durable_prerequisite_observed") is True
        and gate_index < deletion_index
        and os.path.isfile(os.path.join(archive_dir, "public_results.yml"))
        and not os.path.exists(fix_data["task_dir"])
        and not os.path.exists(os.path.join(archive_dir, "private_runtime"))
        and not os.path.exists(os.path.join(archive_dir, "_runtime"))
        and not os.path.exists(fix_data["external_runtime"])
        and not any("private_runtime" in path or "_runtime" in path for path in tracked)
    )

def eval_GC_T040(exc: Exception, fix_data):
    if exc and ("Stage 06" in str(exc) or isinstance(exc, NotImplementedError)):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc is not None:
        raise ValueError(f"Unrelated exception: {exc}")
    if fix_data.get("mode") == "mutation-suite":
        cases = fix_data.get("subcases") or []
        roots = [case.get("base_dir") for case in cases]
        if len(cases) != 3 or len(set(roots)) != 3:
            raise ValueError("GC-T040 negative subcases were not independently initialized")
        if any(_GC_T040_conforms(case) for case in cases):
            raise ValueError("GC-T040 negative subcase escaped the physical oracle")
        raise ValueError("PRIVATE_RUNTIME_LEAK")
    if not _GC_T040_conforms(fix_data):
        raise ValueError("PRIVATE_RUNTIME_LEAK")
def _make_GC_T041_fixture(mode: str) -> Dict[str, Any]:
    base = tempfile.mkdtemp()
    TEMP_DIRS.append(base)
    task_dir = os.path.join(base, "task")
    archive_dir = os.path.join(base, "archive")
    os.makedirs(task_dir)
    os.makedirs(archive_dir)
    with open(os.path.join(task_dir, "context.txt"), "w") as f: f.write("active")
    with open(os.path.join(archive_dir, "context.txt"), "w") as f: f.write("archived")
    
    return {"scenario": "GC-T041", "base_dir": base, "task_dir": task_dir,
            "archive_dir": archive_dir, "mode": mode}

def fix_GC_T041(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    return _make_GC_T041_fixture(mode)

def act_GC_T041(adapter, fix_data):
    if fix_data.get("scenario") != "GC-T041":
        raise ValueError("GC-T041 received an unrelated fixture")
    if fix_data["mode"] == "mutation-suite":
        case = _make_GC_T041_fixture("mutation-suite")
        request = dict(case)
        request.update({
            "authority": "implicit_default",
            "target": "archive",
            "bypass_authority": True,
        })
        fix_data["subcases"] = [{
            "fixture_root": case["base_dir"],
            "trace": adapter.load_default_context(request),
        }]
    else:
        fix_data["subcases"] = []
        for authority, target in (
            ("default_load", "active"),
            ("exact_archive_pointer", "archive"),
            ("Human_explicit_request", "archive"),
            ("implicit_default", "archive"),
        ):
            case = _make_GC_T041_fixture("full")
            request = dict(case)
            request.update({
                "authority": authority,
                "target": target,
                "bypass_authority": False,
            })
            fix_data["subcases"].append({
                "fixture_root": case["base_dir"],
                "trace": adapter.load_default_context(request),
            })

def _GC_T041_trace_conforms(trace: Dict[str, Any]) -> bool:
    if not isinstance(trace, dict) or not trace.get("structured_read_trace"):
        return False
    attempted = trace.get("attempted_paths") or []
    successful = trace.get("successful_read_paths") or []
    authority = trace.get("authority_source")
    target = trace.get("target")
    if len(attempted) != 1:
        return False
    if target == "active" and authority == "default_load":
        return len(successful) == 1 and trace.get("content") == "active" and not trace.get("rejected")
    if target == "archive" and authority in {"exact_archive_pointer", "Human_explicit_request"}:
        return len(successful) == 1 and trace.get("content") == "archived" and not trace.get("rejected")
    if target == "archive" and authority == "implicit_default":
        return successful == [] and trace.get("content") is None and trace.get("rejected") is True
    return False

def eval_GC_T041(exc: Exception, fix_data):
    if exc and ("Stage 06" in str(exc) or isinstance(exc, NotImplementedError)):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc is not None:
        raise ValueError(f"Unrelated exception: {exc}")
    cases = fix_data.get("subcases") or []
    roots = [case.get("fixture_root") for case in cases]
    if len(roots) != len(set(roots)):
        raise ValueError("GC-T041 subcases were not independently initialized")
    if fix_data.get("mode") == "mutation-suite":
        if len(cases) != 1 or _GC_T041_trace_conforms(cases[0].get("trace")):
            raise ValueError("GC-T041 unauthorized archive read was not physically detected")
        raise ValueError("ARCHIVE_DEFAULT_LOAD")
    if len(cases) != 4 or not all(_GC_T041_trace_conforms(case.get("trace")) for case in cases):
        raise ValueError("ARCHIVE_DEFAULT_LOAD")
def fix_GC_T042(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    base = tempfile.mkdtemp()
    TEMP_DIRS.append(base)
    
    if mode == "mutation-suite":
        subcases = []
        mutations = [
            {"execution_payload": "malicious"},
            {"message_body": "some text"},
            {"sender_index_entry": "some_entry"},
            {"delivery_state": "delivered"},
            {"full_history": "past_messages"}
        ]
        for i, m in enumerate(mutations):
            path = os.path.join(base, f"discovery_{i}.yml")
            with open(path, "w") as f: yaml.dump(m, f)
            subcases.append(path)
        return {"scenario": "GC-T042", "invalid_files": subcases}
    else:
        path = os.path.join(base, "discovery.yml")
        with open(path, "w") as f: yaml.dump({"roots": ["/some/path"]}, f)
        return {"scenario": "GC-T042", "file_path": path}
def act_GC_T042(adapter, fix_data):
    if "invalid_files" in fix_data:
        errors = []
        for f in fix_data["invalid_files"]:
            try:
                adapter.validate_discovery_file({"file_path": f})
            except ValueError as e:
                errors.append(e)
        if len(errors) == len(fix_data["invalid_files"]) and all("Discovery scope violation" in str(e) for e in errors):
            raise ValueError("Discovery scope violation")
        raise ValueError(f"Missing subcase rejection. Got: {errors}")
    else:
        adapter.validate_discovery_file(fix_data)
def eval_GC_T042(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Discovery scope violation" in str(exc): raise ValueError("DISCOVERY_SCOPE")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T042", "DISCOVERY_SCOPE", fix_GC_T042, act_GC_T042, eval_GC_T042))
def _make_GC_T043_fixture(mode: str) -> Dict[str, Any]:
    base = tempfile.mkdtemp()
    TEMP_DIRS.append(base)
    human_dir = os.path.join(base, "Human")
    os.makedirs(human_dir)
    current = os.path.join(human_dir, "current.yml")
    init_data = {"task_id": "t1", "title": "t", "current_stage_or_checkpoint": "s0", "important_refs": [], "pending_Human_decision": False, "last_material_update": "0"}
    with open(current, "w") as f: yaml.dump(init_data, f)
    
    return {"scenario": "GC-T043", "base_dir": base, "current": current, "mode": mode}

def fix_GC_T043(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    return _make_GC_T043_fixture(mode)

def _read_GC_T043_current(path: str) -> Tuple[bytes, Dict[str, Any]]:
    raw = Path(path).read_bytes()
    return raw, yaml.safe_load(raw.decode("utf-8"))

def _execute_GC_T043_sequence(adapter, case: Dict[str, Any], mutation: str = None) -> Dict[str, Any]:
    initial_bytes, initial_data = _read_GC_T043_current(case["current"])
    ordinary = {
        "event_kind": "ordinary_message",
        "task_id": "t1",
        "title": "t",
        "current_stage_or_checkpoint": "s0",
        "important_refs": [],
        "pending_Human_decision": False,
        "last_material_update": "0",
    }
    adapter.update_Human_current({
        "current": case["current"],
        "message": ordinary,
        "mutation": mutation if mutation == "ordinary_message_wrongly_updates_current" else None,
    })
    ordinary_bytes, ordinary_data = _read_GC_T043_current(case["current"])
    decision = dict(ordinary)
    decision.update({
        "event_kind": "Human_decision_required",
        "pending_Human_decision": True,
        "last_material_update": "decision-1",
    })
    adapter.update_Human_current({
        "current": case["current"],
        "message": decision,
        "mutation": mutation if mutation in {
            "material_event_fails_to_update",
            "material_update_missing_required_field",
            "material_update_contains_prohibited_extra_payload",
        } else None,
    })
    decision_bytes, decision_data = _read_GC_T043_current(case["current"])
    stage = dict(decision)
    stage.update({
        "event_kind": "stage_completion",
        "current_stage_or_checkpoint": "stage04-complete",
        "pending_Human_decision": False,
        "last_material_update": "stage-1",
    })
    adapter.update_Human_current({
        "current": case["current"],
        "message": stage,
        "mutation": None,
    })
    stage_bytes, stage_data = _read_GC_T043_current(case["current"])
    return {
        "initial_bytes": initial_bytes,
        "initial_data": initial_data,
        "ordinary_bytes": ordinary_bytes,
        "ordinary_data": ordinary_data,
        "decision_bytes": decision_bytes,
        "decision_data": decision_data,
        "stage_bytes": stage_bytes,
        "stage_data": stage_data,
    }

def act_GC_T043(adapter, fix_data):
    if fix_data.get("scenario") != "GC-T043":
        raise ValueError("GC-T043 received an unrelated fixture")
    if fix_data["mode"] == "mutation-suite":
        fix_data["subcases"] = []
        for mutation in (
            "ordinary_message_wrongly_updates_current",
            "material_event_fails_to_update",
            "material_update_missing_required_field",
            "material_update_contains_prohibited_extra_payload",
        ):
            case = _make_GC_T043_fixture("mutation-suite")
            fix_data["subcases"].append({
                "fixture_root": case["base_dir"],
                "observation": _execute_GC_T043_sequence(adapter, case, mutation),
            })
    else:
        fix_data["observation"] = _execute_GC_T043_sequence(adapter, fix_data)

def _GC_T043_conforms(observation: Dict[str, Any]) -> bool:
    if not isinstance(observation, dict):
        return False
    allowed = {
        "task_id", "title", "current_stage_or_checkpoint", "important_refs",
        "pending_Human_decision", "last_material_update",
    }
    decision = observation.get("decision_data") or {}
    stage = observation.get("stage_data") or {}
    return (
        observation.get("initial_bytes") == observation.get("ordinary_bytes")
        and observation.get("decision_bytes") != observation.get("ordinary_bytes")
        and set(decision) == allowed
        and decision.get("pending_Human_decision") is True
        and decision.get("last_material_update") == "decision-1"
        and set(stage) == allowed
        and stage.get("current_stage_or_checkpoint") == "stage04-complete"
        and stage.get("pending_Human_decision") is False
        and stage.get("last_material_update") == "stage-1"
    )

def eval_GC_T043(exc: Exception, fix_data):
    if exc and ("Stage 06" in str(exc) or isinstance(exc, NotImplementedError)):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc is not None:
        raise ValueError(f"Unrelated exception: {exc}")
    if fix_data.get("mode") == "mutation-suite":
        cases = fix_data.get("subcases") or []
        roots = [case.get("fixture_root") for case in cases]
        if len(cases) != 4 or len(set(roots)) != 4:
            raise ValueError("GC-T043 negative subcases were not independently initialized")
        if any(_GC_T043_conforms(case.get("observation")) for case in cases):
            raise ValueError("GC-T043 negative subcase escaped the physical oracle")
        raise ValueError("HUMAN_CURRENT_TRIGGER")
    if not _GC_T043_conforms(fix_data.get("observation")):
        raise ValueError("HUMAN_CURRENT_TRIGGER")
def _make_GC_T044_fixture(mode: str) -> Dict[str, Any]:
    base = tempfile.mkdtemp()
    TEMP_DIRS.append(base)
    human_dir = os.path.join(base, "Human")
    os.makedirs(human_dir)
    current = os.path.join(human_dir, "current.yml")
    initial = {
        "task_id": "t1",
        "title": "t",
        "current_stage_or_checkpoint": "s0",
        "important_refs": [],
        "pending_Human_decision": False,
        "last_material_update": "0",
    }
    with open(current, "w") as f: yaml.dump(initial, f)
    return {"scenario": "GC-T044", "base_dir": base, "current": current, "mode": mode}

def fix_GC_T044(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    return _make_GC_T044_fixture(mode)

def _GC_T044_requests() -> List[Dict[str, Any]]:
    authority = {
        "task_id": "t1",
        "navigation_owner_endpoint_id": "owner-endpoint",
        "can_write_Human_current": True,
    }
    return [
        {
            "current_task_id": "t1",
            "writer_endpoint_id": "executor-endpoint",
            "writer_task_role": "execution",
            "task_navigation_owner_endpoint_id": "owner-endpoint",
            "current_task_authority": authority,
            "explicit_Human_authorization": None,
        },
        {
            "current_task_id": "t1",
            "writer_endpoint_id": "architecture-endpoint",
            "writer_task_role": "architecture_and_decision",
            "task_navigation_owner_endpoint_id": "owner-endpoint",
            "current_task_authority": authority,
            "explicit_Human_authorization": None,
        },
        {
            "current_task_id": "t1",
            "writer_endpoint_id": "owner-endpoint",
            "writer_task_role": "architecture_and_decision",
            "task_navigation_owner_endpoint_id": "owner-endpoint",
            "current_task_authority": authority,
            "explicit_Human_authorization": None,
        },
    ]

def _execute_GC_T044_case(adapter, case: Dict[str, Any], request: Dict[str, Any],
                          bypass_authority: bool = False) -> Dict[str, Any]:
    before = Path(case["current"]).read_bytes()
    payload = dict(request)
    payload.update({
        "current": case["current"],
        "message": {
            "task_id": request["current_task_id"],
            "title": "t",
            "current_stage_or_checkpoint": "s1",
            "important_refs": ["decision.yml"],
            "pending_Human_decision": True,
            "last_material_update": "authority-event-1",
        },
        "bypass_authority": bypass_authority,
    })
    response = adapter.update_Human_current(payload)
    after = Path(case["current"]).read_bytes()
    return {
        "request": request,
        "before_bytes": before,
        "after_bytes": after,
        "after_data": yaml.safe_load(after.decode("utf-8")),
        "adapter_response": response,
    }

def act_GC_T044(adapter, fix_data):
    if fix_data.get("scenario") != "GC-T044":
        raise ValueError("GC-T044 received an unrelated fixture")
    requests = _GC_T044_requests()
    if fix_data["mode"] == "mutation-suite":
        fix_data["subcases"] = []
        for request in requests[:2]:
            case = _make_GC_T044_fixture("mutation-suite")
            fix_data["subcases"].append({
                "fixture_root": case["base_dir"],
                "observation": _execute_GC_T044_case(adapter, case, request, True),
            })
    else:
        fix_data["subcases"] = []
        for request in requests:
            case = _make_GC_T044_fixture("full")
            fix_data["subcases"].append({
                "fixture_root": case["base_dir"],
                "observation": _execute_GC_T044_case(adapter, case, request),
            })

def _GC_T044_case_conforms(observation: Dict[str, Any]) -> bool:
    if not isinstance(observation, dict):
        return False
    request = observation.get("request") or {}
    authority = request.get("current_task_authority") or {}
    explicit = request.get("explicit_Human_authorization") or {}
    ordinary_authorized = (
        request.get("writer_endpoint_id") == request.get("task_navigation_owner_endpoint_id")
        and request.get("writer_task_role") == "architecture_and_decision"
        and authority.get("task_id") == request.get("current_task_id")
        and authority.get("navigation_owner_endpoint_id") == request.get("task_navigation_owner_endpoint_id")
        and authority.get("can_write_Human_current") is True
    )
    explicitly_authorized = (
        explicit.get("task_id") == request.get("current_task_id")
        and explicit.get("writer_endpoint_id") == request.get("writer_endpoint_id")
        and explicit.get("can_write_Human_current") is True
    )
    expected_authorized = ordinary_authorized or explicitly_authorized
    changed = observation.get("before_bytes") != observation.get("after_bytes")
    if not expected_authorized:
        return not changed
    allowed = {
        "task_id", "title", "current_stage_or_checkpoint", "important_refs",
        "pending_Human_decision", "last_material_update",
    }
    data = observation.get("after_data") or {}
    return changed and set(data) == allowed and data.get("task_id") == request.get("current_task_id")

def eval_GC_T044(exc: Exception, fix_data):
    if exc and ("Stage 06" in str(exc) or isinstance(exc, NotImplementedError)):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc is not None:
        raise ValueError(f"Unrelated exception: {exc}")
    cases = fix_data.get("subcases") or []
    roots = [case.get("fixture_root") for case in cases]
    if len(roots) != len(set(roots)):
        raise ValueError("GC-T044 subcases were not independently initialized")
    if fix_data.get("mode") == "mutation-suite":
        if len(cases) != 2 or any(_GC_T044_case_conforms(case.get("observation")) for case in cases):
            raise ValueError("GC-T044 unauthorized write was not derived from structured authority state")
        raise ValueError("HUMAN_CURRENT_OWNER")
    if len(cases) != 3 or not all(_GC_T044_case_conforms(case.get("observation")) for case in cases):
        raise ValueError("HUMAN_CURRENT_OWNER")
def _make_GC_T045_fixture(mode: str) -> Dict[str, Any]:
    base = tempfile.mkdtemp()
    TEMP_DIRS.append(base)
    msg_dir = os.path.join(base, "messages")
    os.makedirs(msg_dir)
    with open(os.path.join(msg_dir, "m1.txt"), "w") as f: f.write("m1")
    with open(os.path.join(msg_dir, "m2.txt"), "w") as f: f.write("m2")
    with open(os.path.join(msg_dir, "m3.txt"), "w") as f: f.write("m3")
    path = os.path.join(base, "index.yml")
    with open(path, "w") as f: yaml.dump(["m1.txt", "m2.txt"], f)
    baseline_path = os.path.join(base, "baseline_index.yml")
    with open(baseline_path, "w") as f: yaml.dump(["m1.txt", "m2.txt"], f)
    return {
        "scenario": "GC-T045",
        "index_file": path,
        "baseline_index_file": baseline_path,
        "msg_dir": msg_dir,
        "mode": mode,
        "base_dir": base,
    }

def fix_GC_T045(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    return _make_GC_T045_fixture(mode)

def _write_GC_T045_state(case: Dict[str, Any], state: Any) -> None:
    with open(case["index_file"], "w", encoding="utf-8") as stream:
        yaml.dump(state, stream, sort_keys=False)

def _run_GC_T045_validator(adapter, case: Dict[str, Any]) -> Exception:
    try:
        adapter.validate_sender_index({
            "scenario": "GC-T045",
            "index_file": case["index_file"],
            "baseline_index_file": case["baseline_index_file"],
            "msg_dir": case["msg_dir"],
        })
    except NotImplementedError:
        raise
    except Exception as error:
        return error
    return None

def act_GC_T045(adapter, fix_data):
    if fix_data.get("scenario") != "GC-T045":
        raise ValueError("GC-T045 received an unrelated fixture")
    if fix_data["mode"] == "mutation-suite":
        invalid_states = (
            ["m1.txt"],
            ["m1.txt", "m4.txt"],
            ["m1.txt", {"m2.txt": "body"}],
            ["m1.txt", "m2.txt", "missing.txt"],
            ["m1.txt", "m2.txt", "m1.txt"],
        )
        fix_data["subcases"] = []
        for state in invalid_states:
            case = _make_GC_T045_fixture("mutation-suite")
            _write_GC_T045_state(case, state)
            fix_data["subcases"].append({
                "fixture_root": case["base_dir"],
                "fixture": case,
                "validator_exception": _run_GC_T045_validator(adapter, case),
            })
    else:
        _write_GC_T045_state(fix_data, ["m1.txt", "m2.txt", "m3.txt"])
        fix_data["validator_exception"] = _run_GC_T045_validator(adapter, fix_data)

def _GC_T045_state_conforms(case: Dict[str, Any]) -> bool:
    with open(case["baseline_index_file"], "r", encoding="utf-8") as stream:
        baseline = yaml.safe_load(stream)
    with open(case["index_file"], "r", encoding="utf-8") as stream:
        current = yaml.safe_load(stream)
    if not isinstance(baseline, list) or not isinstance(current, list):
        return False
    if not all(isinstance(pointer, str) for pointer in current):
        return False
    if current[:len(baseline)] != baseline or len(current) != len(baseline) + 1:
        return False
    if len(set(current)) != len(current):
        return False
    return all(os.path.isfile(os.path.join(case["msg_dir"], pointer)) for pointer in current)

def eval_GC_T045(exc: Exception, fix_data):
    if exc and ("Stage 06" in str(exc) or isinstance(exc, NotImplementedError)):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc is not None:
        raise ValueError(f"Unrelated exception: {exc}")
    if fix_data.get("mode") == "mutation-suite":
        cases = fix_data.get("subcases") or []
        roots = [case.get("fixture_root") for case in cases]
        if len(cases) != 5 or len(set(roots)) != 5:
            raise ValueError("GC-T045 negative subcases were not independently initialized")
        for case in cases:
            if _GC_T045_state_conforms(case["fixture"]):
                raise ValueError("GC-T045 invalid physical index unexpectedly conforms")
            error = case.get("validator_exception")
            if not hasattr(error, "payload") or error.payload.get("failure_code") != "SENDER_INDEX_INTEGRITY":
                raise ValueError("GC-T045 state-only validator did not reject an invalid physical index")
        raise ValueError("SENDER_INDEX_INTEGRITY")
    if fix_data.get("validator_exception") is not None or not _GC_T045_state_conforms(fix_data):
        raise ValueError("SENDER_INDEX_INTEGRITY")
def fix_GC_T046(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text"}
    if mode == "mutation-suite": fix["immutable_correction"] = True
    return fix
def act_GC_T046(adapter, fix_data):
    adapter.publish_message(fix_data)
def eval_GC_T046(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Immutable correction failed" in str(exc): raise ValueError("IMMUTABLE_CORRECTION")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T046", "IMMUTABLE_CORRECTION", fix_GC_T046, act_GC_T046, eval_GC_T046))
def fix_GC_T047(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["identity_boundary"] = True
    return fix
def act_GC_T047(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T047(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Content identity boundary violated" in str(exc): raise ValueError("CONTENT_IDENTITY_BOUNDARY")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T047", "CONTENT_IDENTITY_BOUNDARY", fix_GC_T047, act_GC_T047, eval_GC_T047))
def fix_GC_T048(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text"}
    if mode == "mutation-suite": fix["endpoint_parity"] = True
    return fix
def act_GC_T048(adapter, fix_data):
    adapter.publish_message(fix_data)
def eval_GC_T048(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Endpoint canonical parity mismatch" in str(exc): raise ValueError("ENDPOINT_CANONICAL_PARITY")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T048", "ENDPOINT_CANONICAL_PARITY", fix_GC_T048, act_GC_T048, eval_GC_T048))
def fix_GC_T049(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    fix = {"endpoint_id": "test", "role": "info", "content": "text", "required_refs": []}
    if mode == "mutation-suite": fix["private_reasoning"] = True
    return fix
def act_GC_T049(adapter, fix_data):
    adapter.validate_message(fix_data)
def eval_GC_T049(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    if exc and "Private reasoning prohibited" in str(exc): raise ValueError("PRIVATE_REASONING_PROHIBITED")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T049", "PRIVATE_REASONING_PROHIBITED", fix_GC_T049, act_GC_T049, eval_GC_T049))
def fix_GC_T050(mode: str, root: Path, spec_ref: str, freeze_data: Dict[str, Any]) -> Any:
    stage02 = root / "08_os/_runs/run-20260805-全局通讯机制-001/02_信息收集与提炼"
    packet_path = stage02 / "多模型实验包_v1.yml"
    res1 = stage02 / "antigravity_desktop_executor_01_result.yml"
    res2 = stage02 / "antigravity_desktop_opus_executor_01_result.yml"
    
    base_dir = tempfile.mkdtemp()
    TEMP_DIRS.append(base_dir)
    
    import shutil
    shutil.copy(packet_path, base_dir)
    
    # Blocker 5: Do NOT modify real model results to make conforming.
    # We must use synthetic perfect responses for harness conforming tests,
    # and immutable frozen evidence for scoring the actual experiment.
    
    mutated_res1 = os.path.join(base_dir, "synthetic_model1_result.yml")
    opus_res = os.path.join(base_dir, "synthetic_model2_result.yml")
    
    # Generate perfect synthetic results for conforming/mutation suite harness
    synthetic_perfect = {
        "endpoint": {"endpoint_id": "test-endpoint", "model_or_product": "test", "environment_class": "desktop_local_model"},
        "fixture_results": [
            {
                "fixture_id": "F1-minimal-yaml-index",
                "recovered": {
                    "task_id": "os-v2-global-communication-system-001",
                    "sender_endpoint_id": "chatgpt-web-planner-01",
                    "expected_recipient_endpoint_id": "claude-code-cli-executor-01",
                    "message_type_and_purpose": "request - 执行超出默认角色的受保护发布",
                    "exact_paths_to_read": ["08_os/_runs/run-x/06_执行/发布任务包.yml", "08_os/_runs/run-x/durable/Human_decisions/授权发布.yml"],
                    "authority_interpretation": "Requires authorization ref 08_os/_runs/run-x/durable/Human_decisions/授权发布.yml"
                }
            },
            {
                "fixture_id": "F2-compact-json-index",
                "recovered": {
                    "task_id": "os-v2-global-communication-system-001",
                    "sender_endpoint_id": "chatgpt-web-planner-01",
                    "expected_recipient_endpoint_id": "claude-code-cli-executor-01",
                    "message_type_and_purpose": "request - 执行超出默认角色的受保护发布",
                    "exact_paths_to_read": ["08_os/_runs/run-x/06_执行/发布任务包.yml", "08_os/_runs/run-x/durable/Human_decisions/授权发布.yml"],
                    "authority_interpretation": "Requires authorization"
                }
            },
            {
                "fixture_id": "F3-free-text-pointer",
                "recovered": {
                    "task_id": "os-v2-global-communication-system-001",
                    "sender_endpoint_id": "chatgpt-web-planner-01",
                    "expected_recipient_endpoint_id": "claude-code-cli-executor-01",
                    "message_type_and_purpose": "request - 执行超出默认角色的受保护发布",
                    "exact_paths_to_read": ["08_os/_runs/run-x/06_执行/发布任务包.yml", "08_os/_runs/run-x/durable/Human_decisions/授权发布.yml"],
                    "authority_interpretation": "Requires authorization"
                }
            },
            {
                "fixture_id": "F4-long-content-reference",
                "recovered": {
                    "task_id": "os-v2-global-communication-system-001",
                    "sender_endpoint_id": "claude-code-desktop-reviewer-01",
                    "expected_recipient_endpoint_id": "chatgpt-web-planner-01",
                    "message_type_and_purpose": "response - B结果模型审核意见",
                    "exact_paths_to_read": ["08_os/_runs/run-x/03_结果建模/审核意见_v1.md"],
                    "authority_interpretation": "None required"
                }
            }
        ]
    }
    
    if mode in ["full", "mutation-suite"]:
        with open(mutated_res1, "w", encoding="utf-8") as f:
            yaml.dump(synthetic_perfect, f, allow_unicode=True)
            
        import copy
        synthetic_perfect2 = copy.deepcopy(synthetic_perfect)
        if mode == "mutation-suite":
            synthetic_perfect2["fixture_results"][0]["recovered"]["exact_paths_to_read"] = ["wrong_path.yml"]
            
        with open(opus_res, "w", encoding="utf-8") as f:
            yaml.dump(synthetic_perfect2, f, allow_unicode=True)
            
        result_paths = [mutated_res1, opus_res]
    else:
        # Preimplementation baseline: score the immutable frozen actual model results
        shutil.copy(res1, base_dir)
        shutil.copy(res2, base_dir)
        result_paths = [
            os.path.join(base_dir, "antigravity_desktop_executor_01_result.yml"),
            os.path.join(base_dir, "antigravity_desktop_opus_executor_01_result.yml")
        ]
            
    return {
        "packet_path": os.path.join(base_dir, "多模型实验包_v1.yml"),
        "result_paths": result_paths
    }
def act_GC_T050(adapter, fix_data):
    adapter.score_cross_model(fix_data)
def eval_GC_T050(exc: Exception, fix_data):
    if exc is None: return
    if "Stage 06" in str(exc) or isinstance(exc, NotImplementedError):
        raise ValueError("EXPECTED_FAIL_STAGE06")
    msg = str(exc)
    if "mismatch" in msg or "Missing" in msg or "exact" in msg:
        raise ValueError("CROSS_MODEL_SEMANTIC_RECOVERY")
    raise ValueError(f"Unrelated exception: {exc}")
TESTS.append(TestCase("GC-T050", "CROSS_MODEL_SEMANTIC_RECOVERY", fix_GC_T050, act_GC_T050, eval_GC_T050))
TESTS.append(TestCase("GC-T033", "SAME_PATH_CONFLICT", fix_GC_T033, act_GC_T033, eval_GC_T033))
TESTS.append(TestCase("GC-T034", "NON_FAST_FORWARD", fix_GC_T034, act_GC_T034, eval_GC_T034))
TESTS.append(TestCase("GC-T039", "WHOLE_TASK_ARCHIVE", fix_GC_T039, act_GC_T039, eval_GC_T039))
TESTS.append(TestCase("GC-T040", "PRIVATE_RUNTIME_LEAK", fix_GC_T040, act_GC_T040, eval_GC_T040))
TESTS.append(TestCase("GC-T041", "ARCHIVE_DEFAULT_LOAD", fix_GC_T041, act_GC_T041, eval_GC_T041))
TESTS.append(TestCase("GC-T043", "HUMAN_CURRENT_TRIGGER", fix_GC_T043, act_GC_T043, eval_GC_T043))
TESTS.append(TestCase("GC-T044", "HUMAN_CURRENT_OWNER", fix_GC_T044, act_GC_T044, eval_GC_T044))
TESTS.append(TestCase("GC-T045", "SENDER_INDEX_INTEGRITY", fix_GC_T045, act_GC_T045, eval_GC_T045))

TEST_CASES = {t.test_id: t for t in TESTS}
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--mode", required=True, choices=["full", "mutation-suite", "preimplementation-baseline"])
    parser.add_argument("--adapter", required=True, choices=["synthetic_conforming", "synthetic_mutating", "production"])
    parser.add_argument("--expected-tested-commit", required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    stage04_root = repo_root / "08_os/_runs/run-20260805-全局通讯机制-001/04_测试生成"
    sys.path.insert(0, str(stage04_root / "实现"))
    import synthetic_adapters
    if args.adapter == "synthetic_conforming":
        adapter = synthetic_adapters.SyntheticConformingAdapter(args.mode)
    elif args.adapter == "synthetic_mutating":
        adapter = synthetic_adapters.SyntheticMutatingAdapter(args.mode)
    else:
        adapter = synthetic_adapters.ProductionTestAdapter(args.mode)
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(repo_root)).decode("utf-8").strip()
        if head != args.expected_tested_commit:
            print(
                f"ERROR: Local HEAD {head} does not equal expected tested commit "
                f"{args.expected_tested_commit}.",
                file=sys.stderr,
            )
            sys.exit(1)
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=str(repo_root)
        ).decode("utf-8").strip()
        if not branch:
            print("ERROR: Final evidence runs require the authorized work branch.", file=sys.stderr)
            sys.exit(1)
        remote_line = subprocess.check_output(
            ["git", "ls-remote", "origin", f"refs/heads/{branch}"],
            cwd=str(repo_root),
        ).decode("utf-8").strip()
        remote_head = remote_line.split()[0] if remote_line else None
        if remote_head != head:
            print(
                f"ERROR: Remote branch head {remote_head} does not equal local tested "
                f"commit {head}.",
                file=sys.stderr,
            )
            sys.exit(1)
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=str(repo_root)).decode("utf-8")
        clean_status = [line for line in status.splitlines() if "results/" not in line]
        if clean_status:
            print(f"ERROR: Working tree is dirty. Tests must be run on a clean implementation commit. Dirty files: {clean_status}", file=sys.stderr)
            sys.exit(1)
    except subprocess.CalledProcessError:
        print("ERROR: Could not verify git state.", file=sys.stderr)
        sys.exit(1)
    try:
        cand_path = stage04_root / "冻结测试候选_v1.yml"
        candidate_sha256 = hashlib.sha256(cand_path.read_bytes()).hexdigest()
        
        spec_files = sorted(list((stage04_root / "specs").glob("*.yml")))
        specs_data = b"".join([f.read_bytes() for f in spec_files])
        semantic_specs_sha256 = hashlib.sha256(specs_data).hexdigest()
        
        runner_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except Exception:
        candidate_sha256 = "error"
        semantic_specs_sha256 = "error"
        runner_sha256 = "error"
    with open(stage04_root / "冻结测试候选_v1.yml", "r", encoding="utf-8") as f:
        freeze_data = yaml.safe_load(f)
    results = []
    counts = {"PASS": 0, "EXPECTED_FAIL": 0, "FAIL": 0, "ERROR": 0, "BLOCKED_EXTERNAL": 0}
    for case in TESTS:
        try:
            fixture = case.fixture_factory(args.mode, repo_root, "", freeze_data)
            exc = None
            try:
                case.action(adapter, fixture)
            except Exception as e:
                exc = e
            try:
                case.evaluator(exc, fixture)
                if args.adapter == "synthetic_mutating":
                    status = "FAIL"
                    reason = "Mutation failed to trigger exception"
                else:
                    status = "PASS"
                    reason = None
            except Exception as e:
                err_val = str(e)
                if err_val == "EXPECTED_FAIL_STAGE06" and args.adapter == "production" and args.mode == "preimplementation-baseline":
                    status = "EXPECTED_FAIL"
                    reason = case.failure_code
                elif err_val == case.failure_code:
                    status = "PASS" if args.adapter == "synthetic_mutating" else "FAIL"
                    reason = case.failure_code
                else:
                    status = "FAIL"
                    reason = f"Wrong violation: {e}"
            results.append({
                "test_id": case.test_id,
                "expected": case.failure_code if args.adapter == "synthetic_mutating" else "PASS",
                "observed": status if status in ["PASS", "FAIL", "ERROR"] else ("PASS" if args.adapter == "synthetic_mutating" else "EXPECTED_FAIL"),
                "status": status,
                "failure_code": case.failure_code,
                "reason": reason
            })
            counts[status] += 1
            
        except Exception as e:
            results.append({
                "test_id": case.test_id,
                "expected": "PASS",
                "observed": "ERROR",
                "status": "ERROR",
                "failure_code": case.failure_code,
                "reason": str(e)
            })
            counts["ERROR"] += 1
    output = {
        "tested_commit": head,
        "candidate_sha256": candidate_sha256,
        "semantic_specs_sha256": semantic_specs_sha256,
        "runner_blob_sha256": runner_sha256,
        "runner_identity": "Antigravity_Gemini_v4",
        "remote_branch": branch,
        "remote_tested_commit_verified": remote_head == head,
        "adapter": args.adapter,
        "run_mode": args.mode,
        "command": " ".join(sys.argv),
        "total": 50,
        "counts": counts,
        "results": results
    }
    if args.adapter == "synthetic_mutating":
        output["counts"] = {
            "mutated_cases": 50,
            "exact_frozen_failure_codes_derived_by_evaluators": counts["PASS"],
            "wrong_or_missing_codes": counts["FAIL"],
            "ERROR": counts["ERROR"],
            "exit_code": 1 if counts["FAIL"] > 0 else 0
        }
    else:
        output["counts"]["exit_code"] = 1 if counts["FAIL"] > 0 else 0
        
    if args.adapter == "production":
        output["counts"]["exit_code"] = 1 if (counts["FAIL"] > 0 or counts["ERROR"] > 0) else 0
    output["exit_code"] = output["counts"]["exit_code"]
    
    out_file = stage04_root / "results" / f"{args.mode.replace('-', '_')}_v3.yml"
    if args.adapter == "synthetic_conforming":
        out_file = stage04_root / "results" / "synthetic_conforming_full_v3.yml"
    elif args.adapter == "production":
        out_file = stage04_root / "results" / "preimplementation_baseline_v3.yml"
        
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.dump(output, f, sort_keys=False, allow_unicode=True)
    print(
        json.dumps(
            {
                "result_file": str(out_file),
                "tested_commit": head,
                "counts": output["counts"],
                "exit_code": output["exit_code"],
            },
            ensure_ascii=False,
        ),
        file=sys.stderr,
    )
    sys.exit(output["exit_code"])
if __name__ == "__main__":
    main()
