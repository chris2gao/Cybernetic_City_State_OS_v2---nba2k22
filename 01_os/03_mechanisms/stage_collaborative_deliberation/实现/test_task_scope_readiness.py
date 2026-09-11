"""Author regression tests, not independent acceptance or action authorization."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROFILE = "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profiles_v1.yml"
POLICY = "01_os/05_registry/repository_publisher_authority_v1.yml"
# The validator reads the feasibility basis table from this blob at the exact
# candidate, so the synthetic repository must carry it like the profile set.
CONTRACT = "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profile契约_v1.yml"
PACKET = "scope/task_packet.yml"
BASELINE = "b0473587877d1dfca445a92ed5429f71202c7314"
spec = importlib.util.spec_from_file_location("scope_subject", HERE / "verify_stage_collaborative_deliberation.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
PROFILES = yaml.safe_load((ROOT / PROFILE).read_text(encoding="utf-8"))["profiles"]


def git(repo, *args, input=None):
    result = subprocess.run(["git", "-c", "core.autocrlf=false", *args], cwd=repo,
                            input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    return result.stdout.decode("utf-8").strip()


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(yaml.safe_dump(data, allow_unicode=True, sort_keys=False).encode("utf-8"))


def blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def build_instance(candidate, packet_blob, profile, *, task_id="scope-test", action_id="work", paths=None):
    """External driver: construct complete declared model; it does not run work."""
    data = yaml.safe_load((HERE / "fixtures/instance/task_scope_cases_v1.yml").read_text(encoding="utf-8"))["instance"]
    data["task_scope"] = {"schema_version": 1, "task_id": task_id, "candidate": candidate,
                          "task_packet": {"path": PACKET, "blob_sha": packet_blob}, "action_id": action_id,
                          "stage_id": profile["profile_id"], "paths": paths or ["scope/result.txt"]}
    model = data["current_model"]
    model.update(task_id=task_id, stage_id=profile["profile_id"], current_exact_model_version=candidate)
    # The allowed feasibility basis kinds differ by stage, so one template cannot
    # serve all seven. Read the allowed kinds from the contract rather than
    # restating them here, so this driver cannot drift from what it validates.
    kinds = (v.load_profile_contract()["common_task_stage_model"]
             ["feasibility_basis_contract"]["basis_kinds_by_stage"][profile["profile_id"]])
    model["feasibility_support"] = {
        "value": model["feasibility_support"]["value"],
        "basis": {"kind": kinds[0], "ref": "synthetic-fixture-basis-001"},
    }
    model["stage_specific_model_elements"] = {field: {"disposition": v.REPRESENTED,
                                                      "value": "Synthetic supported value for " + field}
                                               for field in profile["required_model_fields"]}
    data["receipt"]["profile_id_and_version"] = f'{profile["profile_id"]}@{profile["profile_version"]}'
    data["receipt"]["exact_candidate_version"] = candidate
    return data


class Source:
    def __init__(self, folder):
        self.repo = folder / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "codex/scope-test")
        # Identity/config are scoped to this new temporary repository only.
        git(self.repo, "config", "user.name", "Synthetic scope fixture")
        git(self.repo, "config", "user.email", "scope-fixture@example.invalid")
        for path in (PROFILE, POLICY, CONTRACT):
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / path).read_bytes())
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "synthetic base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.packet = {"task_id": "scope-test", "branch": "codex/scope-test", "exact_base_sha": self.base,
                       "allowed_changed_paths": ["scope/**"], "required_tests": ["scope-test"], "prohibitions": [],
                       "stage_actions": [{"action_id": "work", "kind": "ordinary_task_work", "target": "refs/heads/codex/scope-test",
                                          "expected_target_head": None, "stage_ids": [p["profile_id"] for p in PROFILES],
                                          "paths": ["scope/result.txt"], "confirmation": None}]}
        self.commit()

    def commit(self):
        write_yaml(self.repo / PACKET, {"task_packet": self.packet})
        git(self.repo, "add", ".")
        self.commit_index()

    def commit_index(self):
        """Commit the exact synthetic index, including deliberately bad blobs."""
        git(self.repo, "commit", "--allow-empty", "-m", "synthetic candidate")
        self.candidate = git(self.repo, "rev-parse", "HEAD")
        self.packet_blob = git(self.repo, "rev-parse", f"HEAD:{PACKET}")

    def raw_packet(self, raw):
        (self.repo / PACKET).write_bytes(raw)
        git(self.repo, "add", PACKET)
        self.commit_index()

    def instance(self, profile=None):
        return build_instance(self.candidate, self.packet_blob, profile or PROFILES[5])

    def protected(self, *, confirmation=True, kind="publish_or_merge_to_master"):
        action = self.packet["stage_actions"][0]
        action.update(kind=kind, target="refs/heads/master", expected_target_head=self.base)
        if confirmation:
            record = {"actor_class": "current_Human", "kind": "explicit_statement", "task_id": self.packet["task_id"],
                      "action_id": action["action_id"], "exact_base_sha": self.base, "target": action["target"],
                      "expected_target_head": action["expected_target_head"], "stage_ids": action["stage_ids"],
                      "paths": action["paths"], "stale": False, "revoked": False}
            path = self.repo / "scope/confirmation.yml"
            write_yaml(path, record)
            action["confirmation"] = dict(record, source_ref={"path": "scope/confirmation.yml", "blob_sha": blob(path.read_bytes())})
        self.commit()


@pytest.fixture
def source(tmp_path):
    return Source(tmp_path)


def run_cli(source, data, tmp_path, *, version="v2", mode="instance", raw=None, candidate=None, env=None):
    target = tmp_path / "external-instance.json"
    target.write_bytes(raw if raw is not None else json.dumps(data).encode("utf-8"))
    script = HERE / ("verify_stage_collaborative_deliberation_v2.py" if version == "v2" else "verify_stage_collaborative_deliberation.py")
    result = subprocess.run([sys.executable, "-B", str(script), mode, str(target), "--repo-root", str(source.repo),
                             "--candidate", candidate or source.candidate, "--json-output"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, env=env)
    assert result.stdout, result.stderr.decode("utf-8", errors="replace")
    assert json.loads(result.stdout)["exit_code"] == result.returncode
    return result.returncode


@pytest.mark.parametrize("version", ["v1", "v2"])
@pytest.mark.parametrize("mode", ["dormant", "full", "incremental"])
@pytest.mark.parametrize("profile", PROFILES, ids=lambda p: p["profile_id"])
def test_actual_cli_all_stages_modes(source, tmp_path, version, mode, profile):
    data = source.instance(profile)
    data["activation_mode"] = mode
    assert run_cli(source, data, tmp_path, version=version) == 0


def test_all_profile_obligations_remain_required(source):
    for profile in PROFILES:
        data = source.instance(profile)
        for field in profile["required_model_fields"]:
            removed = copy.deepcopy(data)
            del removed["current_model"]["stage_specific_model_elements"][field]
            assert v.validate_task_scope_instance(removed, source.repo, source.candidate) == 16, field


@pytest.mark.parametrize("mutation", [
    lambda d: d["task_scope"].update(task_id="wrong"),
    lambda d: d["task_scope"].update(candidate="0" * 40),
    lambda d: d["task_scope"]["task_packet"].update(blob_sha="0" * 40),
    lambda d: d["task_scope"].update(action_id="undeclared"),
    lambda d: d["task_scope"].update(stage_id="wrong"),
    lambda d: d["current_model"].update(task_id="wrong"),
    lambda d: d["current_model"].update(stage_id="wrong"),
    lambda d: d["current_model"].update(current_exact_model_version="wrong"),
    lambda d: d["receipt"].update(exact_candidate_version="wrong"),
    lambda d: d["receipt"].update(profile_id_and_version="wrong@1"),
    lambda d: d["receipt"]["validator_mode_and_exit_code"].update(exit_code=False),
    lambda d: d["receipt"]["gate_results"].update(start="fail"),
    lambda d: d["receipt"].update(missing_partial_or_stale_paths=["missing"]),
    lambda d: d["receipt"].update(loaded_paths=False),
    lambda d: d.update(seven_stage_child="false"),
    lambda d: d.update(task_scope=False),
    lambda d: d.update(activation_mode=[]),
    lambda d: d.update(ordinary=True),
    lambda d: d.update(completion_pointer=False),
    lambda d: d["current_model"].update(completion=False),
    lambda d: d["current_model"].update(completion=[]),
    lambda d: d["current_model"].update(Human_confirmation={}),
    lambda d: d["current_model"].update(open_load_bearing_items=False),
    lambda d: d["current_model"].update(open_load_bearing_items=[{"load_bearing": True, "disposition": "resolved", "Human_basis": "yes"}]),
    lambda d: d["current_model"].update(open_load_bearing_items=[{"load_bearing": True, "disposition": "unresolved"}]),
    lambda d: d["current_model"].update(open_load_bearing_items=[{"load_bearing": True, "disposition": "deferred_non_blocking", "revisit_trigger": "later"}]),
])
def test_actual_cli_rejects_mismatches_and_falsey_types(source, tmp_path, mutation):
    data = source.instance()
    mutation(data)
    assert run_cli(source, data, tmp_path) != 0


@pytest.mark.parametrize("path", ["../x", "/x", "C:/x", "scope\\x", "scope//x", "scope/./x", ".git/config", ":(glob)*", "scope/*"])
def test_path_escape(source, tmp_path, path):
    data = source.instance()
    data["task_scope"]["paths"] = [path]
    assert run_cli(source, data, tmp_path) != 0


@pytest.mark.parametrize("kind", ["missing", "tree", "blob", "invalid"])
def test_git_candidate_is_exact_commit(source, tmp_path, kind):
    candidate = {"missing": "0" * 40, "tree": git(source.repo, "rev-parse", "HEAD^{tree}"),
                 "blob": source.packet_blob, "invalid": "HEAD"}[kind]
    data = source.instance()
    data["task_scope"]["candidate"] = candidate
    assert run_cli(source, data, tmp_path, candidate=candidate) != 0


@pytest.mark.parametrize("path", ["scope", "scope/missing.yml", POLICY])
def test_packet_source_not_regular_matching_packet(source, tmp_path, path):
    data = source.instance()
    data["task_scope"]["task_packet"]["path"] = path
    assert run_cli(source, data, tmp_path) != 0


def test_actual_whole_candidate_diff_checked(source, tmp_path):
    (source.repo / "outside.txt").write_text("not allowed", encoding="utf-8")
    source.commit()
    assert run_cli(source, source.instance(), tmp_path) == 15


def test_ordinary_cannot_choose_master(source, tmp_path):
    source.packet["stage_actions"][0]["target"] = "refs/heads/master"
    source.commit()
    assert run_cli(source, source.instance(), tmp_path) == 15


@pytest.mark.parametrize("confirmation", [False, True])
def test_protected_requires_resolved_simple_confirmation(source, tmp_path, confirmation):
    source.protected(confirmation=confirmation)
    result = run_cli(source, source.instance(), tmp_path)
    assert (result == 0) is confirmation


@pytest.mark.parametrize("field,value", [("stale", True), ("revoked", True), ("actor_class", "executor"),
                                        ("action_id", "other"), ("target", "refs/heads/other"),
                                        ("expected_target_head", "0" * 40)])
def test_protected_confirmation_bound(source, tmp_path, field, value):
    source.protected()
    source.packet["stage_actions"][0]["confirmation"][field] = value
    source.commit()
    assert run_cli(source, source.instance(), tmp_path) != 0


def test_protected_confirmation_source_is_read_not_claimed(source, tmp_path):
    source.protected()
    path = source.repo / "scope/confirmation.yml"
    path.write_bytes(b"actor_class: executor\n")
    source.packet["stage_actions"][0]["confirmation"]["source_ref"]["blob_sha"] = blob(path.read_bytes())
    source.commit()
    assert run_cli(source, source.instance(), tmp_path) == 15


def test_covered_protected_action_spans_stages_without_new_confirmation(source, tmp_path):
    source.protected()
    for profile in PROFILES:
        assert run_cli(source, source.instance(profile), tmp_path) == 0


def test_core_history_rewrite_never_confirmable(source, tmp_path):
    source.protected(kind="rewrite_published_history")
    assert run_cli(source, source.instance(), tmp_path) == 15


def test_child_scope_alignment_and_base_receipt(source, tmp_path):
    data = source.instance()
    data["seven_stage_child"] = True
    scope = data["task_scope"]
    data["receipt"]["alignment_binding"] = {"bound_model_version": source.candidate, "task_id": scope["task_id"],
                                              "action_id": scope["action_id"], "task_packet": scope["task_packet"]}
    data["receipt"]["profile_binding"] = {"profile_id_and_version": data["receipt"]["profile_id_and_version"],
                                            "mechanism_ref": PROFILES[5]["mechanism_ref"]}
    assert run_cli(source, data, tmp_path) == 0
    data["receipt"]["alignment_binding"]["task_id"] = "wrong"
    assert run_cli(source, data, tmp_path) == 17


@pytest.mark.parametrize("raw", [b'{"task_scope": false, "task_scope": {}}', b'{"x": NaN}', b'{"x": 1e999}', b'\xff'])
def test_actual_cli_strict_raw_input(source, tmp_path, raw):
    assert run_cli(source, None, tmp_path, raw=raw) != 0


def test_profile_source_not_mutable_checkout(source, tmp_path):
    path = source.repo / PROFILE
    path.write_text("profiles: []\n", encoding="utf-8")
    assert run_cli(source, source.instance(), tmp_path) == 0
    source.packet["allowed_changed_paths"].append(PROFILE)
    source.commit()
    assert run_cli(source, source.instance(), tmp_path) == 16


def test_real_baseline_rejects_same_ordinary_payload(source, tmp_path):
    old = tmp_path / "baseline"
    old.mkdir()
    for name in ("verify_stage_collaborative_deliberation.py", "verify_stage_collaborative_deliberation_v2.py"):
        relative = (HERE / name).relative_to(ROOT).as_posix()
        result = subprocess.run(["git", "show", f"{BASELINE}:{relative}"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode == 0
        (old / name).write_bytes(result.stdout)
    target = tmp_path / "ordinary-baseline.json"
    target.write_text(json.dumps(source.instance()), encoding="utf-8")
    result = subprocess.run([sys.executable, "-B", str(old / "verify_stage_collaborative_deliberation_v2.py"),
                             "instance", str(target), "--json-output"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 15
    assert run_cli(source, source.instance(), tmp_path) == 0


def test_historical_helper_api_and_no_implicit_legacy_route(source, tmp_path):
    helper_path = ROOT / "01_os/06_execution/boot/stage_collaborative_deliberation/human_challenge_verify.py"
    helper_spec = importlib.util.spec_from_file_location("synthetic_challenge_helper", helper_path)
    helper = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper)
    loaded = helper.load_validator()
    bound = {key: "synthetic-" + key for key in loaded.LEGACY_COMMITMENT_BOUND_FIELDS}
    record = dict(bound, nonce_commitment={"scheme": loaded.LEGACY_HUMAN_AUTHORITY_SCHEME,
                   "algorithm": "sha256", "digest": loaded.compute_legacy_commitment(bound, "SYNTHETIC-NOT-A-SECRET")})
    assert loaded.validate_authority_record_commitments(record) == 0
    assert loaded.verify_human_challenge(record, "SYNTHETIC-NOT-A-SECRET")[0] is True
    assert loaded.verify_human_challenge(record, "SYNTHETIC-WRONG")[0] is False
    data = source.instance()
    del data["task_scope"]
    assert run_cli(source, data, tmp_path) != 0
    assert run_cli(source, data, tmp_path, mode="legacy_instance") == 15


def test_legal_merge_fixtures_unchanged_and_accepted_by_strict_reader():
    for name in ("positive_cases_v1.yml", "readiness_counterexamples_v1.yml"):
        path = HERE / "fixtures/instance" / name
        baseline = subprocess.run(["git", "show", f"{BASELINE}:{path.relative_to(ROOT).as_posix()}"],
                                  cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert baseline.returncode == 0
        assert path.read_bytes() == baseline.stdout
        assert v.load_task_scope_doc(path) == yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("field,value", [
    ("task_id", False), ("branch", []), ("exact_base_sha", False),
    ("allowed_changed_paths", False), ("required_tests", False),
    ("prohibitions", False), ("publisher", False), ("stage_actions", {}),
    ("stage_actions", []), ("stage_actions", [False]),
])
def test_packet_consumed_fields_reject_falsey_wrong_types(source, tmp_path, field, value):
    source.packet[field] = value
    source.commit()
    assert run_cli(source, source.instance(), tmp_path) != 0


@pytest.mark.parametrize("field,value", [
    ("action_id", False), ("kind", False), ("kind", "invented_action"),
    ("target", []), ("expected_target_head", False), ("stage_ids", False),
    ("stage_ids", [PROFILES[5]["profile_id"], "invented_stage"]),
    ("paths", False), ("confirmation", False), ("allow_skip", True),
])
def test_action_schema_rejects_unknown_and_falsey_types(source, tmp_path, field, value):
    source.packet["stage_actions"][0][field] = value
    source.commit()
    assert run_cli(source, source.instance(), tmp_path) != 0


def test_unselected_action_is_not_a_place_to_hide_unknown_stage(source, tmp_path):
    extra = copy.deepcopy(source.packet["stage_actions"][0])
    extra.update(action_id="hidden-invalid-action", stage_ids=["invented_stage"])
    source.packet["stage_actions"].append(extra)
    source.commit()
    assert run_cli(source, source.instance(), tmp_path) != 0


def test_duplicate_action_ids_are_rejected(source, tmp_path):
    source.packet["stage_actions"].append(copy.deepcopy(source.packet["stage_actions"][0]))
    source.commit()
    assert run_cli(source, source.instance(), tmp_path) != 0


@pytest.mark.parametrize("kind", ["wrapper_unknown", "packet_duplicate", "action_duplicate", "bad_utf8"])
def test_committed_packet_raw_source_errors(source, tmp_path, kind):
    raw = (source.repo / PACKET).read_bytes()
    if kind == "wrapper_unknown":
        raw += b"unexpected_root: true\n"
    elif kind == "packet_duplicate":
        raw = raw.replace(b"  task_id: scope-test\n", b"  task_id: scope-test\n  task_id: scope-test\n", 1)
    elif kind == "action_duplicate":
        raw = raw.replace(b"  - action_id: work\n", b"  - action_id: work\n    action_id: work\n", 1)
    else:
        raw += b"\n# invalid UTF-8 byte: \xff\n"
    assert raw != (source.repo / PACKET).read_bytes()
    source.raw_packet(raw)
    assert run_cli(source, source.instance(), tmp_path) != 0


def test_committed_packet_symlink_mode_rejected(source, tmp_path):
    # Construct a real Git symlink entry without requiring Windows symlink rights.
    git(source.repo, "update-index", "--cacheinfo", f"120000,{source.packet_blob},{PACKET}")
    source.commit_index()
    assert git(source.repo, "ls-tree", "HEAD", PACKET).startswith("120000 blob ")
    assert run_cli(source, source.instance(), tmp_path) == 13


def test_committed_packet_tree_mode_rejected(source, tmp_path):
    data = source.instance()
    data["task_scope"]["task_packet"] = {"path": "scope", "blob_sha": git(source.repo, "rev-parse", "HEAD:scope")}
    assert git(source.repo, "ls-tree", "HEAD", "scope").startswith("040000 tree ")
    assert run_cli(source, data, tmp_path) == 13


@pytest.mark.parametrize("mode", ["120000", "160000"])
def test_action_path_cannot_traverse_committed_symlink_parent(source, tmp_path, mode):
    oid = (git(source.repo, "hash-object", "-w", "--stdin", input=b"../../outside")
           if mode == "120000" else source.base)
    git(source.repo, "update-index", "--add", "--cacheinfo", f"{mode},{oid},scope/link")
    source.packet["stage_actions"][0]["paths"] = ["scope/link/result.txt"]
    write_yaml(source.repo / PACKET, {"task_packet": source.packet})
    git(source.repo, "add", PACKET)
    source.commit_index()
    data = source.instance()
    data["task_scope"]["paths"] = ["scope/link/result.txt"]
    assert run_cli(source, data, tmp_path) != 0


@pytest.mark.parametrize("path", ["scope/.GIT/config", "scope/.Git/config", "scope/x./result.txt", "scope/x /result.txt"])
def test_action_paths_reject_windows_aliases(source, tmp_path, path):
    source.packet["stage_actions"][0]["paths"] = [path]
    source.commit()
    data = source.instance()
    data["task_scope"]["paths"] = [path]
    assert run_cli(source, data, tmp_path) != 0


def test_actual_cli_missing_git_is_source_error_not_success(source, tmp_path):
    env = dict(os.environ, PATH="")
    assert run_cli(source, source.instance(), tmp_path, env=env) == 13


def test_git_not_a_tree_error_is_never_absence(source, monkeypatch):
    support = v.task_scope_support()
    original = support.git

    def broken(repo, *args):
        if args[:1] == ("ls-tree",):
            raise support.VerificationError("fatal: not a tree object")
        return original(repo, *args)

    monkeypatch.setattr(support, "git", broken)
    assert v.validate_task_scope_instance(source.instance(), source.repo, source.candidate) == 13


def test_fabricated_load_bearing_Human_basis_ref_rejected(source, tmp_path):
    data = source.instance()
    data["current_model"]["open_load_bearing_items"] = [{"load_bearing": True, "disposition": "resolved",
        "Human_basis": {"actor_class": "current_Human", "kind": "explicit_statement", "stale": False,
                        "ref": "scope/nonexistent-confirmation.yml"}}]
    assert run_cli(source, data, tmp_path) != 0


@pytest.mark.parametrize("verification", [True, "pass", ["pass"], {"passed": False}, {"exit_code": False}])
def test_completion_verification_cannot_be_truthy_malformed(source, tmp_path, verification):
    data = source.instance()
    data["current_model"]["current_exact_output_version"] = source.candidate
    # Closure fields are supplied so this case still fails for the malformed
    # verification reference it is named for, not for a missing closure field.
    data["current_model"]["completion"] = {"progression_requested": True, "actual_result": "declared output",
        "bound_output_version": source.candidate, "verification_result": verification, **CLOSURE}
    assert run_cli(source, data, tmp_path) != 0


@pytest.mark.parametrize("pointer", [
    {"append_only": True}, {"append_only": True, "bound_candidate_version": "wrong"},
    {"append_only": True, "bound_candidate_version": False},
    {"append_only": True, "bound_candidate_version": "0" * 40, "supersedes": False},
    {"append_only": True, "bound_candidate_version": "0" * 40, "supersedes_record_ref": False},
])
def test_completion_pointer_requires_exact_candidate_and_typed_fields(source, tmp_path, pointer):
    data = source.instance()
    data["completion_pointer"] = pointer
    assert run_cli(source, data, tmp_path) != 0


def decision_basis(source, kind, decision_id="design-D"):
    action = source.packet["stage_actions"][0]
    if kind == "current_task_scope":
        action["covered_decision_ids"] = [decision_id]
        source.commit()
        return {"kind": kind, "decision_id": decision_id, "task_packet": {"path": PACKET, "blob_sha": source.packet_blob},
                "action_id": action["action_id"]}
    record = {"actor_class": "current_Human", "kind": "explicit_statement", "decision_id": decision_id,
              "task_id": source.packet["task_id"], "action_id": action["action_id"], "exact_base_sha": source.base,
              "target": action["target"], "expected_target_head": action["expected_target_head"],
              "stage_ids": action["stage_ids"], "paths": action["paths"], "stale": False, "revoked": False}
    path = source.repo / "scope/decision.yml"
    write_yaml(path, record)
    source.commit()
    return {"kind": kind, "decision_id": decision_id,
            "source_ref": {"path": "scope/decision.yml", "blob_sha": blob(path.read_bytes())}}


def resolved_decision(data, basis):
    data["current_model"]["open_load_bearing_items"] = [{"decision_id": "design-D", "load_bearing": True,
        "disposition": "resolved", "Human_basis": basis}]


@pytest.mark.parametrize("kind", ["current_task_scope", "explicit_statement"])
@pytest.mark.parametrize("version", ["v1", "v2"])
def test_real_bound_decision_is_reusable_across_all_stages(source, tmp_path, kind, version):
    basis = decision_basis(source, kind)
    for profile in PROFILES:
        data = source.instance(profile)
        resolved_decision(data, basis)
        assert run_cli(source, data, tmp_path, version=version) == 0


@pytest.mark.parametrize("mutation", [
    lambda b: b.update(decision_id="other"),
    lambda b: b.update(action_id="other"),
    lambda b: b["task_packet"].update(blob_sha="0" * 40),
    lambda b: b.update(ignored_override=True),
])
def test_task_scope_decision_basis_is_exact(source, tmp_path, mutation):
    basis = decision_basis(source, "current_task_scope")
    mutation(basis)
    data = source.instance()
    resolved_decision(data, basis)
    assert run_cli(source, data, tmp_path) != 0


@pytest.mark.parametrize("coverage", [None, False, [], ["other"], ["design-D", "design-D"], [False]])
def test_load_bearing_decision_must_be_in_selected_action_coverage(source, tmp_path, coverage):
    basis = decision_basis(source, "current_task_scope")
    action = source.packet["stage_actions"][0]
    if coverage is None:
        del action["covered_decision_ids"]
    else:
        action["covered_decision_ids"] = coverage
    source.commit()
    basis["task_packet"]["blob_sha"] = source.packet_blob
    data = source.instance()
    resolved_decision(data, basis)
    assert run_cli(source, data, tmp_path) != 0


@pytest.mark.parametrize("field,value", [
    ("actor_class", "executor"), ("kind", "silence"), ("decision_id", "other"), ("task_id", "other"),
    ("action_id", "other"), ("exact_base_sha", "0" * 40), ("target", "refs/heads/master"),
    ("expected_target_head", False), ("stage_ids", []), ("paths", ["scope/other.txt"]),
    ("stale", True), ("stale", 0), ("revoked", True), ("revoked", 0), ("ignore", True),
])
def test_explicit_decision_record_contents_are_checked(source, tmp_path, field, value):
    basis = decision_basis(source, "explicit_statement")
    path = source.repo / basis["source_ref"]["path"]
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    record[field] = value
    write_yaml(path, record)
    source.commit()
    basis["source_ref"]["blob_sha"] = blob(path.read_bytes())
    data = source.instance()
    resolved_decision(data, basis)
    assert run_cli(source, data, tmp_path) != 0


@pytest.mark.parametrize("kind", ["current_task_scope", "explicit_statement"])
def test_unknown_stage_field_requires_bound_decision_not_bare_actor(source, tmp_path, kind):
    basis = decision_basis(source, kind)
    data = source.instance()
    field = PROFILES[5]["required_model_fields"][0]
    element = {"disposition": v.UNKNOWN_DISPOSED, "blocking": False, "load_bearing": True,
        "Human_decision_boundary": True, "deferral": "deferred_nonblocking", "reason_and_scope": "Synthetic scoped deferral",
        "revisit_trigger": "new relevant evidence", "decision_id": "design-D", "Human_basis": basis,
        "downstream_impact_assessment": {dimension: False for dimension in v.DOWNSTREAM_IMPACT_DIMENSIONS}}
    data["current_model"]["stage_specific_model_elements"][field] = element
    assert run_cli(source, data, tmp_path) == 0
    element["Human_basis"] = {"actor_class": "current_Human"}
    assert run_cli(source, data, tmp_path) != 0


@pytest.mark.parametrize("path", [PROFILE, POLICY])
@pytest.mark.parametrize("kind", ["bad_utf8", "duplicate_key", "symlink"])
def test_profile_and_policy_source_failures_are_not_empty_defaults(source, tmp_path, path, kind):
    source.packet["allowed_changed_paths"].append(path)
    if kind == "bad_utf8":
        (source.repo / path).write_bytes(b"# malformed source byte \xff\n")
        source.commit()
    elif kind == "duplicate_key":
        (source.repo / path).write_bytes(b"schema_version: 1\nschema_version: 1\n")
        source.commit()
    else:
        source.commit()
        oid = git(source.repo, "rev-parse", f"HEAD:{path}")
        git(source.repo, "update-index", "--cacheinfo", f"120000,{oid},{path}")
        source.commit_index()
    assert run_cli(source, source.instance(), tmp_path) != 0


@pytest.mark.parametrize("field", v.SUBSTANTIVE_COMMON_FIELDS + v.NULLABLE_COMMON_FIELDS)
def test_current_common_model_fields_still_required_in_dormant_mode(source, tmp_path, field):
    data = source.instance()
    del data["current_model"][field]
    assert run_cli(source, data, tmp_path) != 0


def verification_record(source, profile=None, *, record_change=None, raw=None):
    """A later evidence commit binds the prior candidate; no self-SHA cycle."""
    profile = profile or PROFILES[5]
    record = {"schema_version": "stage_verification_result.v1", "candidate": source.candidate,
              "task_id": source.packet["task_id"], "stage_id": profile["profile_id"], "status": "verified"}
    if record_change:
        record.update(record_change)
    payload = raw if raw is not None else yaml.safe_dump(record, sort_keys=False).encode("utf-8")
    oid = git(source.repo, "hash-object", "-w", "--stdin", input=payload)
    tree = git(source.repo, "mktree", input=f"100644 blob {oid}\tverification.yml\n".encode("ascii"))
    commit = git(source.repo, "commit-tree", tree, "-p", source.candidate, input=b"synthetic later evidence\n")
    assert git(source.repo, "rev-parse", "HEAD") == source.candidate
    assert commit != source.candidate
    return {"commit": commit, "path": "verification.yml", "blob_sha": oid}


CLOSURE = {"plan_vs_actual_delta": "none_material", "material_deviation": "none_material",
           "residual_risk": "none_material", "downstream_baseline": "synthetic next-stage baseline"}


def completed_model(data, source, result):
    data["current_model"]["current_exact_output_version"] = source.candidate
    data["current_model"]["completion"] = {"progression_requested": True, "actual_result": "synthetic declared result",
        "bound_output_version": source.candidate, "verification_result": result, **CLOSURE}
    data["completion_pointer"] = {"append_only": True, "bound_candidate_version": source.candidate}


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_later_evidence_commit_binds_candidate_without_self_reference(source, tmp_path, version):
    for profile in PROFILES:
        data = source.instance(profile)
        result = verification_record(source, profile)
        completed_model(data, source, result)
        assert run_cli(source, data, tmp_path, version=version) == 0


@pytest.mark.parametrize("field,value", [
    ("schema_version", False), ("candidate", "0" * 40), ("task_id", "other"),
    ("stage_id", "other"), ("status", "failed"), ("status", True), ("ignore", True),
])
def test_verification_record_exact_contents_required(source, tmp_path, field, value):
    data = source.instance()
    completed_model(data, source, verification_record(source, record_change={field: value}))
    assert run_cli(source, data, tmp_path) != 0


@pytest.mark.parametrize("kind", ["missing_commit", "tree_commit", "blob_commit", "symbolic_commit", "boolean_commit",
                                 "missing_path", "wrong_blob", "unknown_field", "bad_utf8", "duplicate_key"])
def test_verification_evidence_source_is_read_exactly(source, tmp_path, kind):
    data = source.instance()
    if kind in {"bad_utf8", "duplicate_key"}:
        raw = b"# invalid UTF8 \xff\n" if kind == "bad_utf8" else b"candidate: x\ncandidate: x\n"
        result = verification_record(source, raw=raw)
    else:
        result = verification_record(source)
        if kind == "missing_commit":
            result["commit"] = "0" * 40
        elif kind == "tree_commit":
            result["commit"] = git(source.repo, "rev-parse", "HEAD^{tree}")
        elif kind == "blob_commit":
            result["commit"] = source.packet_blob
        elif kind == "symbolic_commit":
            result["commit"] = "HEAD"
        elif kind == "boolean_commit":
            result["commit"] = False
        elif kind == "missing_path":
            result["path"] = "missing.yml"
        elif kind == "wrong_blob":
            result["blob_sha"] = "0" * 40
        else:
            result["ignore"] = True
    completed_model(data, source, result)
    assert run_cli(source, data, tmp_path) != 0


def test_supplied_verification_must_be_valid_even_without_progression(source, tmp_path):
    data = source.instance()
    data["current_model"]["completion"] = {"progression_requested": False, "verification_result": False}
    assert run_cli(source, data, tmp_path) != 0
