#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, shutil, tempfile, unittest
from pathlib import Path
import yaml

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("minimum_loop",HERE/"run_minimum_operational_loop.py")
assert SPEC and SPEC.loader
loop=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(loop)
FIXTURE=HERE/"fixtures/pilot_cross_platform_path_guard"

def load(path:Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))
def save(path:Path,value):
    path.write_text(yaml.safe_dump(value,allow_unicode=True,sort_keys=False,width=120),encoding="utf-8",newline="\n")
def rebind(root:Path):
    manifest=load(root/"manifest.yml")
    file_by={item["stage_id"]:item["path"] for item in manifest["artifacts"]}
    pred={
      loop.EXPECTED_STAGE_IDS[0]:[],
      loop.EXPECTED_STAGE_IDS[1]:[loop.EXPECTED_STAGE_IDS[0]],
      loop.EXPECTED_STAGE_IDS[2]:loop.EXPECTED_STAGE_IDS[:2],
      loop.EXPECTED_STAGE_IDS[3]:loop.EXPECTED_STAGE_IDS[:3],
      loop.EXPECTED_STAGE_IDS[4]:[loop.EXPECTED_STAGE_IDS[3]],
      loop.EXPECTED_STAGE_IDS[5]:loop.EXPECTED_STAGE_IDS[3:5],
      loop.EXPECTED_STAGE_IDS[6]:[loop.EXPECTED_STAGE_IDS[2],loop.EXPECTED_STAGE_IDS[3],loop.EXPECTED_STAGE_IDS[5]],
    }
    hashes={}
    versions={}
    for sid in loop.EXPECTED_STAGE_IDS:
        path=root/file_by[sid]
        data=load(path)
        data["input_refs"]=[{"stage_id":p,"path":file_by[p],"artifact_version":versions[p],"sha256":hashes[p]} for p in pred[sid]]
        save(path,data)
        hashes[sid]=hashlib.sha256(path.read_bytes()).hexdigest()
        versions[sid]=data["artifact_version"]
    for item in manifest["artifacts"]:
        item["sha256"]=hashes[item["stage_id"]]
    save(root/"manifest.yml",manifest)

class MinimumLoopTests(unittest.TestCase):
    def copy_contract(self,repo):
        source=HERE.parents[3]
        contract=load(source/loop.CONTRACT_PATH)
        for rel in [loop.CONTRACT_PATH]+[stage["schema_path"] for stage in contract["stage_order"]]:
            target=repo/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/rel,target)
    def copy_fixture(self)->Path:
        temp=Path(tempfile.mkdtemp());self.addCleanup(lambda:shutil.rmtree(temp,ignore_errors=True))
        shutil.copytree(FIXTURE,temp/"run");return temp/"run"
    def mutate(self,name,fn):
        root=self.copy_fixture();p=root/name;data=load(p);fn(data);save(p,data);rebind(root);return root
    def test_positive_fixture(self):self.assertEqual(loop.validate_structure(FIXTURE)[0],0)
    def test_every_schema_required_payload_field_is_consumed(self):
        repo=HERE.parents[3]
        contract=load(repo/loop.CONTRACT_PATH)
        for stage in contract["stage_order"]:
            schema=load(repo/stage["schema_path"])
            for field in schema["payload_required_fields"]:
                with self.subTest(stage=stage["stage_id"],field=field):
                    root=self.mutate(stage["artifact_filename"],lambda d:d["payload"].pop(field))
                    code,findings=loop.validate_structure(root)
                    self.assertEqual(code,33)
                    self.assertIn(f"payload_required:{stage['stage_id']}:{field}",findings)
    def test_payload_must_be_mapping(self):
        for value in (None,False,0,"",[],"payload"):
            with self.subTest(value=value):
                root=self.mutate("06_execution.yml",lambda d:d.update(payload=value))
                self.assertEqual(loop.validate_structure(root)[0],33)
    def test_execution_and_verification_field_types_fail_closed(self):
        cases=[
            ("06_execution.yml","executor_role",[None,False,0,"",[],{},["executor"]]),
            ("06_execution.yml","allowed_write_paths",[None,False,0,"",{},[[]],[False]]),
            ("06_execution.yml","actual_write_paths",[None,False,0,"",{},[[]],[False]]),
            ("06_execution.yml","attempts",[None,False,0,"",{},[False]]),
            ("06_execution.yml","unauthorized_write_attempts",[None,False,0,"",{}]),
            ("07_verification.yml","reviewer_role",[None,False,0,"",[],{}]),
            ("07_verification.yml","verdict",[None,False,0,"",[],{}]),
            ("07_verification.yml","test_results",[None,False,0,"",{},[False]]),
            ("07_verification.yml","implementation_claims",[None,False,0,"",{},[False]]),
            ("07_verification.yml","upstream_invalidation",[False,0,"",[]]),
            ("07_verification.yml","completion",[None,0,1,"true",[],{}]),
        ]
        for name,field,values in cases:
            for value in values:
                with self.subTest(name=name,field=field,value=value):
                    root=self.mutate(name,lambda d:d["payload"].update({field:value}))
                    code,findings=loop.validate_structure(root)
                    self.assertNotEqual(code,0)
                    self.assertTrue(findings)
    def test_execution_attempt_boolean_is_not_integer(self):
        root=self.mutate("06_execution.yml",lambda d:d["payload"]["attempts"][0].update(attempt=True))
        self.assertEqual(loop.validate_structure(root)[0],37)
    def test_implementation_claim_references_must_be_string_lists(self):
        for field in ("result_claim_ids","evidence_claim_ids"):
            for value in (None,False,0,"",{},[[]],[False]):
                with self.subTest(field=field,value=value):
                    root=self.mutate("07_verification.yml",lambda d:d["payload"]["implementation_claims"][0].update({field:value}))
                    self.assertNotEqual(loop.validate_structure(root)[0],0)
    def test_missing_schema_source_is_structured_failure(self):
        temp=Path(tempfile.mkdtemp());self.addCleanup(lambda:shutil.rmtree(temp,ignore_errors=True))
        code,findings=loop.validate_structure(FIXTURE,temp)
        self.assertEqual(code,33)
        self.assertTrue(findings[0].startswith("payload_schema_source:"))
    def test_malformed_earlier_payload_is_structured_failure(self):
        root=self.mutate("02_evidence.yml",lambda d:d["payload"].update(claims=[None]))
        self.assertEqual(loop.validate_structure(root)[0],33)
    def test_empty_claim_list_is_not_replaced_with_missing_field(self):
        # The proposition is that an empty list is not misread as an absent field.
        # It used to be written as findings == [], which stopped being true when
        # the runner began reporting that the deliberation instance was not
        # validated. Asserting the claim rather than the old shape.
        root=self.mutate("07_verification.yml",lambda d:d["payload"].update(implementation_claims=[]))
        code,findings=loop.validate_structure(root)
        self.assertEqual(code,0)
        self.assertFalse([f for f in findings if "implementation_claims" in f],findings)
    def test_missing_artifact(self):
        root=self.copy_fixture();(root/"03_result.yml").unlink();self.assertEqual(loop.validate_structure(root)[0],30)
    def test_hash_mismatch(self):
        root=self.copy_fixture();p=root/"02_evidence.yml";p.write_text(p.read_text(encoding="utf-8")+"\n# drift\n",encoding="utf-8");self.assertEqual(loop.validate_structure(root)[0],31)
    def test_stage_order(self):
        root=self.copy_fixture();m=load(root/"manifest.yml");m["artifacts"][0],m["artifacts"][1]=m["artifacts"][1],m["artifacts"][0];save(root/"manifest.yml",m);self.assertEqual(loop.validate_structure(root)[0],32)
    # Receipt semantics moved to their owner.
    #
    # test_dormant_receipt_cannot_have_session, test_full_receipt_requires_authority
    # and test_receipt_mechanism_id used to assert that this runner rejected a bad
    # receipt. It no longer judges receipts: the deliberation mechanism does, and
    # its own suite covers those three cases against its twenty-field contract
    # rather than the runner's former ten-line copy. Keeping them here would have
    # meant keeping the copy alive to satisfy the tests.
    #
    # What replaces them is the boundary this runner is responsible for: that a run
    # validated without a candidate says so instead of appearing checked.
    def test_full_validation_without_a_candidate_refuses(self):
        """Not validated is not a pass.

        Reporting it as exit 0 with an explanatory finding was the earlier defect:
        anything reading only the exit code would have taken never ran the
        authoritative validator for success.
        """
        code,findings=loop.validate_run(FIXTURE)
        self.assertEqual(code,41,findings)
        self.assertTrue(any("deliberation_not_validated" in f for f in findings),findings)

    def test_structural_pass_is_not_a_governed_run_verdict(self):
        """The two entries answer different questions and must not be conflated."""
        self.assertEqual(loop.validate_structure(FIXTURE)[0],0)
        self.assertEqual(loop.validate_run(FIXTURE)[0],41)
    def test_unfrozen_tests(self):
        self.assertEqual(loop.validate_structure(self.mutate("04_tests.yml",lambda d:d["payload"].update(frozen=False)))[0],35)
    def test_test_digest_drift(self):
        def f(d):d["payload"]["tests"][0]["expected"]="weakened"
        self.assertEqual(loop.validate_structure(self.mutate("04_tests.yml",f))[0],35)
    def test_execution_allowlist(self):
        def f(d):d["payload"]["actual_write_paths"].append("unrelated.txt")
        self.assertEqual(loop.validate_structure(self.mutate("06_execution.yml",f))[0],36)
    def test_retry_budget(self):
        def f(d):d["payload"]["attempts"][0]["attempt"]=4
        self.assertEqual(loop.validate_structure(self.mutate("06_execution.yml",f))[0],37)
    def test_review_independence(self):
        self.assertEqual(loop.validate_structure(self.mutate("07_verification.yml",lambda d:d["payload"].update(reviewer_role="current_project_lead_model")))[0],38)
    def test_failed_test(self):
        def f(d):d["payload"]["test_results"][0]["status"]="failed"
        self.assertEqual(loop.validate_structure(self.mutate("07_verification.yml",f))[0],38)
    def test_invalidation_blocks_completion(self):
        self.assertEqual(loop.validate_structure(self.mutate("07_verification.yml",lambda d:d["payload"].update(upstream_invalidation={"target":"workflow_stage_03_result_modeling"})))[0],39)
    def test_materialize_pilot(self):
        temp=Path(tempfile.mkdtemp());self.addCleanup(lambda:shutil.rmtree(temp,ignore_errors=True))
        repo=temp/"repo";repo.mkdir();self.copy_contract(repo);src=repo/loop.PILOT_PATH;src.parent.mkdir(parents=True);shutil.copytree(FIXTURE,src)
        code,findings=loop.materialize_pilot(repo,temp/"out");self.assertEqual((code,findings),(0,[]));self.assertTrue((temp/"out/workflow_completion.yml").is_file())
    def test_prohibited_canonical_output(self):
        temp=Path(tempfile.mkdtemp());self.addCleanup(lambda:shutil.rmtree(temp,ignore_errors=True))
        repo=temp/"repo";repo.mkdir();src=repo/loop.PILOT_PATH;src.parent.mkdir(parents=True);shutil.copytree(FIXTURE,src)
        self.assertEqual(loop.materialize_pilot(repo,repo/"01_os/01_workflow/_runtime")[0],40)
    def test_manifest_identity(self):
        root=self.copy_fixture();m=load(root/"manifest.yml");m["workflow_id"]="wrong";save(root/"manifest.yml",m);self.assertEqual(loop.validate_structure(root)[0],33)
    def test_step_dependency_cycle(self):
        def f(d):d["payload"]["steps"][0]["depends_on"]=["S-3"]
        self.assertEqual(loop.validate_structure(self.mutate("05_steps.yml",f))[0],37)
    def test_attempt_coverage(self):
        def f(d):d["payload"]["attempts"]=d["payload"]["attempts"][:-1]
        self.assertEqual(loop.validate_structure(self.mutate("06_execution.yml",f))[0],37)
    def test_review_claim_binding(self):
        def f(d):d["payload"]["implementation_claims"][0]["result_claim_ids"]=["UNKNOWN"]
        self.assertEqual(loop.validate_structure(self.mutate("07_verification.yml",f))[0],38)
    def test_contract_paths_are_forward_slash(self):
        contract=load(HERE.parents[2]/"01_workflow/实现/七阶段最小运行契约_v1.yml")
        self.assertFalse(any("\\" in item["schema_path"] for item in contract["stage_order"]))

if __name__=="__main__":unittest.main()
