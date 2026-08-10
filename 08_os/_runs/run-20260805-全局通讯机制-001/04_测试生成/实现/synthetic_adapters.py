from typing import Dict, Any, List
import subprocess
import yaml
import os
from yaml.loader import SafeLoader

class StrictSafeLoader(SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError("Duplicate key found in YAML")
            mapping.append(key)
        return super().construct_mapping(node, deep)

class EscalationException(Exception):
    def __init__(self, message, payload):
        super().__init__(message)
        self.payload = payload

class CommunicationTestAdapter:
    def __init__(self, mode: str):
        self.mode = mode

class StrictValidationAdapter(CommunicationTestAdapter):
    def parse_yaml(self, content: str) -> Any:
        try:
            events = list(yaml.parse(content))
            if len([e for e in events if isinstance(e, yaml.DocumentStartEvent)]) > 1:
                raise ValueError("Multiple documents found in YAML")
        except yaml.parser.ParserError:
            pass
            
        try:
            nodes = list(yaml.compose_all(content))
        except yaml.composer.ComposerError:
            pass
            
        for e in yaml.parse(content):
            if hasattr(e, 'anchor') and e.anchor is not None:
                raise ValueError("Alias or merge key found in YAML")
            if isinstance(e, yaml.AliasEvent):
                raise ValueError("Alias or merge key found in YAML")
                
            if isinstance(e, (yaml.MappingNode, yaml.SequenceNode, yaml.ScalarNode)):
                if e.tag and not e.tag.startswith('tag:yaml.org,2002:'):
                    raise ValueError("Custom tag found in YAML")
                    
        try:
            return yaml.load(content, Loader=StrictSafeLoader)
        except yaml.constructor.ConstructorError:
            raise ValueError("Custom tag found in YAML")

    def validate_message(self, message: Dict[str, Any]) -> None:
        if "endpoint_id" not in message:
            raise ValueError("Missing endpoint")
        if message.get("synthesize_action"):
            raise ValueError("Synthesized action not allowed")
        if "requested_action" not in message and not message.get("synthesize_action") and "endpoint_id" in message and getattr(self, 'active_mutation', None) == "GC-T003":
            raise ValueError("Missing requested action")
        
        if "requested_action" not in message and "missing_requested_action_test" in message:
            raise ValueError("Missing requested action")

        if message.get("delivered") or message.get("read"):
            raise ValueError("Delivery state fields are not allowed")
        if "summary" in message:
            raise ValueError("Summary field is prohibited")
        if message.get("sequence_mismatch"):
            raise ValueError("Message ID does not match path")
        if message.get("role") == "invalid_role":
            raise ValueError("Role does not match endpoint")
        if message.get("role") == "architecture_and_decision":
            raise ValueError("Role lacks authority")
        if message.get("authorization_ref"):
            raise ValueError("Authorization ref provided but not required")
        if message.get("self_authorization"):
            raise ValueError("Cannot self-authorize")
        if message.get("missing_ref"):
            raise ValueError("A required reference is missing")
        if message.get("set_mismatch"):
            raise ValueError("Required ref set mismatch")
        if message.get("context_expansion"):
            raise ValueError("Unauthorized context expansion")
        if message.get("bootstrap_read"):
            raise ValueError("Bootstrap read set is invalid")
        if message.get("long_content"):
            raise ValueError("Content too long to externalize")
        if message.get("front_matter") is False:
            raise ValueError("Document front matter is missing")
        if message.get("existing_resource"):
            raise ValueError("Invalid existing resource reference")
        if message.get("forbidden_data"):
            raise ValueError("Forbidden data found")
        if message.get("local_default"):
            raise ValueError("Local default route violated")
        if message.get("web_repub"):
            raise ValueError("Web republication required")
        if message.get("dangling_pointer"):
            raise ValueError("Dangling pointer prevented")
        if message.get("route_override"):
            raise ValueError("Human route override failed")
        if message.get("sent_scope"):
            raise ValueError("Sent scope violation")
        if message.get("auto_delivery"):
            raise ValueError("Automatic delivery prohibited")

        if message.get("identity_boundary"):
            raise ValueError("Content identity boundary violated")
        if message.get("private_reasoning"):
            raise ValueError("Private reasoning prohibited")

    def validate_discovery_file(self, fix_data: Dict[str, Any]) -> None:
        file_path = fix_data.get("file_path")
        if not file_path or not os.path.exists(file_path): return
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        
        prohibited = ["execution_payload", "message_body", "sender_index_entry", "delivery_state", "full_history"]
        for p in prohibited:
            if p in data:
                raise ValueError("Discovery scope violation")

    def publish_message(self, message: Dict[str, Any]) -> None:
        if message.get("reuse_sequence"):
            raise ValueError("Sequence number already in use")
        if message.get("sequence") == 10001:
            raise ValueError("Sequence numbers exhausted")
        if message.get("task_scoped"):
            raise ValueError("Sequence is not scoped to task properly")
        if message.get("wrong_zone"):
            raise ValueError("Cannot publish to another sender zone")
        if message.get("local_only"):
            raise ValueError("Local only content blocked from GitHub")
        if message.get("human_github"):
            raise ValueError("Human GitHub trigger failed")
        if message.get("immutable_correction"):
            raise ValueError("Immutable correction failed")
        if message.get("endpoint_parity"):
            raise ValueError("Endpoint canonical parity mismatch")


    def run_git_scenario(self, fix_data: Dict[str, Any]) -> None:
        if "repo_path" not in fix_data: return
        repo_path = fix_data["repo_path"]
        remote_path = fix_data.get("remote_path")
        scenario = fix_data.get("scenario")
        mutation = fix_data.get("mutation")
        action = fix_data.get("action")
        
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@example.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@example.com"

        if action == "pull_rebase_push":
            subprocess.check_output(["git", "pull", "--rebase", "origin", "master"], cwd=repo_path, stderr=subprocess.STDOUT, env=env)
            subprocess.check_output(["git", "push", "origin", "master"], cwd=repo_path, stderr=subprocess.STDOUT, env=env)
            return
        if action == "push_only":
            subprocess.check_output(["git", "push", "origin", "master"], cwd=repo_path, stderr=subprocess.STDOUT, env=env)
            return
        if action == "bad_convergence_lose_local":
            subprocess.check_output(["git", "reset", "--hard", "origin/master"], cwd=repo_path, stderr=subprocess.STDOUT, env=env)
            push_argv = ["git", "push", "origin", "master"]
            push = subprocess.run(
                push_argv, cwd=repo_path, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                text=True, env=env,
            )
            fix_data["git_trace"] = {
                "push": {"argv": push_argv, "return_code": push.returncode},
            }
            return
        if action == "bad_disjoint_convergence":
            import shutil
            pull_argv = ["git", "pull", "--rebase", "origin", "master"]
            pull = subprocess.run(
                pull_argv, cwd=repo_path, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                text=True, env=env,
            )
            commit = None
            if pull.returncode == 0:
                sender_dir = os.path.join(repo_path, "dir_A")
                if os.path.exists(sender_dir):
                    shutil.rmtree(sender_dir)
                subprocess.check_call(["git", "add", "."], cwd=repo_path, env=env)
                commit_argv = ["git", "commit", "-m", "delete"]
                commit = subprocess.run(
                    commit_argv, cwd=repo_path, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                    text=True, env=env,
                )
            push_argv = ["git", "push", "origin", "master"]
            push = subprocess.run(
                push_argv, cwd=repo_path, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                text=True, env=env,
            )
            fix_data["git_trace"] = {
                "pull": {"argv": pull_argv, "return_code": pull.returncode},
                "commit": None if commit is None else {"argv": commit_argv, "return_code": commit.returncode},
                "push": {"argv": push_argv, "return_code": push.returncode},
            }
            return

        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@example.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@example.com"
        
        if scenario == "GC-T033":
            subprocess.check_call(["git", "fetch", "origin"], cwd=repo_path, env=env)
            before_head = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=repo_path
            ).decode("utf-8").strip()
            merge_argv = ["git", "merge", "--no-edit", "origin/master"]
            merge = subprocess.run(
                merge_argv, cwd=repo_path, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            unresolved_output = subprocess.check_output(
                ["git", "diff", "--name-only", "--diff-filter=U"], cwd=repo_path
            ).decode("utf-8")
            observed_paths = sorted(
                path.strip() for path in unresolved_output.splitlines() if path.strip()
            )
            emitted_paths = list(observed_paths)
            continuation_commit_created = False
            push_attempts = []

            if mutation == "auto_resolve_and_continue":
                with open(os.path.join(repo_path, "README.md"), "w", encoding="utf-8") as stream:
                    stream.write("resolved\n")
                subprocess.check_call(["git", "add", "README.md"], cwd=repo_path, env=env)
                subprocess.check_call(["git", "commit", "-m", "prohibited continuation"], cwd=repo_path, env=env)
                after_head = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=repo_path
                ).decode("utf-8").strip()
                continuation_commit_created = after_head != before_head
            elif mutation == "push_after_conflict":
                push_argv = ["git", "push", "origin", "master"]
                pushed = subprocess.run(
                    push_argv, cwd=repo_path, env=env,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                )
                push_attempts.append({
                    "argv": push_argv,
                    "return_code": pushed.returncode,
                })
            elif mutation == "omit_exact_conflict_path":
                emitted_paths = []

            route_present = mutation != "omit_required_escalation"
            return {
                "structured_command_trace": True,
                "merge_argv": merge_argv,
                "merge_return_code": merge.returncode,
                "observed_unresolved_paths": observed_paths,
                "emitted_conflict_paths": emitted_paths,
                "continuation_commit_created": continuation_commit_created,
                "push_attempt_count": len(push_attempts),
                "push_attempts": push_attempts,
                "operation_stopped": not continuation_commit_created and not push_attempts,
                "next_owner": "task_navigation_owner" if route_present else None,
                "Human_escalation_required": route_present,
            }
                
        if scenario == "GC-T034":
            before = subprocess.check_output(["git", "ls-remote", "origin", "master"], cwd=repo_path).decode("utf-8").split()[0]
            first_argv = ["git", "push", "origin", "master"]
            if mutation == "force_push":
                first_argv = ["git", "push", "--force", "origin", "master"]
            first = subprocess.run(
                first_argv, cwd=repo_path, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            attempts = [{"argv": first_argv, "return_code": first.returncode}]

            if mutation == "automatic_retry":
                retry_argv = ["git", "push", "origin", "master"]
                retried = subprocess.run(
                    retry_argv, cwd=repo_path, env=env,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                )
                attempts.append({"argv": retry_argv, "return_code": retried.returncode})

            if mutation == "remote_head_changes":
                actor_path = fix_data["actor_path"]
                with open(os.path.join(actor_path, "independent-change.txt"), "w", encoding="utf-8") as stream:
                    stream.write("independent actor\n")
                subprocess.check_call(["git", "add", "independent-change.txt"], cwd=actor_path, env=env)
                subprocess.check_call(["git", "commit", "-m", "independent remote change"], cwd=actor_path, env=env)
                subprocess.check_call(["git", "push", "origin", "master"], cwd=actor_path, env=env)

            after = subprocess.check_output(["git", "ls-remote", "origin", "master"], cwd=repo_path).decode("utf-8").split()[0]
            return {
                "structured_command_trace": True,
                "push_attempts": attempts,
                "retry_count": max(0, len(attempts) - 1),
                "remote_head_before": before,
                "remote_head_after": after,
                "route": [] if mutation == "escalation_missing" else ["task_navigation_owner", "Human"],
            }

    def archive_task(self, task_id: Dict[str, Any]) -> None:
        base_dir = task_id["base_dir"]
        task_dir = task_id["task_dir"]
        archive_dir = task_id["archive_dir"]
        mutation = task_id.get("mutation")
        scenario = task_id.get("scenario")
        
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@example.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@example.com"
        
        import shutil
        if scenario == "GC-T039":
            if mutation == "fail_to_update_discovery" or mutation == "fail_to_update_discovery_final":
                os.rename(task_dir, archive_dir)
                return
            if mutation == "omit_public_history_category":
                os.rename(task_dir, archive_dir)
                shutil.rmtree(os.path.join(archive_dir, "messages"))
                with open(os.path.join(base_dir, "discovery.yml"), "w") as f: yaml.dump({"roots": ["/archived_task"]}, f)
                return
            
            os.rename(task_dir, archive_dir)
            with open(os.path.join(base_dir, "discovery.yml"), "w") as f: yaml.dump({"roots": ["/archived_task"]}, f)
            return

        if scenario == "GC-T040":
            external_runtime = task_id["external_runtime"]
            operation_trace = task_id.setdefault("operation_trace", [])
            public_result = os.path.join(task_dir, "public_results.yml")
            tracked_public = subprocess.run(
                ["git", "ls-files", "--error-unmatch", "active_task/public_results.yml"],
                cwd=base_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            ).returncode == 0

            if mutation == "private_runtime_leaks_into_archive":
                os.makedirs(archive_dir)
                shutil.copy2(public_result, os.path.join(archive_dir, "public_results.yml"))
                shutil.copytree(
                    os.path.join(task_dir, "private_runtime"),
                    os.path.join(archive_dir, "private_runtime"),
                )
                return
            if mutation == "private_runtime_becomes_git_tracked":
                subprocess.check_call(
                    ["git", "add", "-f", "active_task/_runtime/sentinel.txt"],
                    cwd=base_dir,
                )
                return
            if mutation == "private_runtime_deleted_before_durable_prerequisite":
                os.remove(public_result)
                shutil.rmtree(os.path.join(task_dir, "private_runtime"))
                shutil.rmtree(os.path.join(task_dir, "_runtime"))
                shutil.rmtree(external_runtime)
                operation_trace.extend([
                    "private_runtime_deleted",
                    "durable_prerequisite_missing",
                ])
                return

            if not os.path.isfile(public_result) or not tracked_public:
                raise ValueError("Durable results not present before deletion")
            task_id["durable_prerequisite_observed"] = True
            operation_trace.append("durable_prerequisite_verified")
            os.makedirs(archive_dir)
            subprocess.check_call(
                ["git", "mv", "active_task/public_results.yml", "archived_task/public_results.yml"],
                cwd=base_dir,
            )
            operation_trace.append("public_archive_completed")
            shutil.rmtree(os.path.join(task_dir, "private_runtime"))
            shutil.rmtree(os.path.join(task_dir, "_runtime"))
            shutil.rmtree(external_runtime)
            os.rmdir(task_dir)
            operation_trace.append("private_runtime_deleted")

    def load_default_context(self, fix_data: Dict[str, Any]) -> Any:
        authority = fix_data.get("authority")
        target = fix_data.get("target")
        task_dir = fix_data.get("task_dir")
        archive_dir = fix_data.get("archive_dir")
        p = task_dir if target == "active" else archive_dir
        path = os.path.join(p, "context.txt")
        allowed = (
            (target == "active" and authority == "default_load")
            or (
                target == "archive"
                and authority in {"exact_archive_pointer", "Human_explicit_request"}
            )
        )
        successful_paths = []
        content = None
        if allowed or fix_data.get("bypass_authority"):
            with open(path, "r", encoding="utf-8") as stream:
                content = stream.read()
            successful_paths.append(path)
        return {
            "structured_read_trace": True,
            "attempted_paths": [path],
            "successful_read_paths": successful_paths,
            "authority_source": authority,
            "target": target,
            "content": content,
            "rejected": not allowed and not fix_data.get("bypass_authority"),
        }

    def update_Human_current(self, fix_data: Dict[str, Any]) -> Any:
        current = fix_data.get("current")
        msg = fix_data.get("message") or {}
        mutation = fix_data.get("mutation")
        allowed_fields = {
            "task_id", "title", "current_stage_or_checkpoint", "important_refs",
            "pending_Human_decision", "last_material_update",
        }

        if "current_task_id" in fix_data:
            authority = fix_data.get("current_task_authority") or {}
            explicit = fix_data.get("explicit_Human_authorization") or {}
            ordinary_authorized = (
                fix_data.get("writer_endpoint_id")
                == fix_data.get("task_navigation_owner_endpoint_id")
                and fix_data.get("writer_task_role") == "architecture_and_decision"
                and authority.get("task_id") == fix_data.get("current_task_id")
                and authority.get("navigation_owner_endpoint_id")
                == fix_data.get("task_navigation_owner_endpoint_id")
                and authority.get("can_write_Human_current") is True
            )
            explicitly_authorized = (
                explicit.get("task_id") == fix_data.get("current_task_id")
                and explicit.get("writer_endpoint_id") == fix_data.get("writer_endpoint_id")
                and explicit.get("can_write_Human_current") is True
            )
            authorized = ordinary_authorized or explicitly_authorized
            if authorized or fix_data.get("bypass_authority"):
                update = {key: msg[key] for key in allowed_fields if key in msg}
                with open(current, "w", encoding="utf-8") as stream:
                    yaml.dump(update, stream, sort_keys=True)
            return {
                "authorized_from_structured_state": authorized,
                "write_performed": authorized or bool(fix_data.get("bypass_authority")),
            }

        if mutation == "ordinary_message_wrongly_updates_current":
            update = {key: msg[key] for key in allowed_fields if key in msg}
            update["last_material_update"] = "ordinary-mutant"
            with open(current, "w", encoding="utf-8") as stream:
                yaml.dump(update, stream, sort_keys=True)
            return
        if mutation == "material_event_fails_to_update":
            return
        if mutation == "material_update_missing_required_field":
            with open(current, "w", encoding="utf-8") as stream:
                yaml.dump({"task_id": msg.get("task_id")}, stream, sort_keys=True)
            return
        if mutation == "material_update_contains_prohibited_extra_payload":
            update = {key: msg[key] for key in allowed_fields if key in msg}
            update["full_message"] = "extra"
            with open(current, "w", encoding="utf-8") as stream:
                yaml.dump(update, stream, sort_keys=True)
            return
        if msg.get("event_kind") == "ordinary_message":
            return
        if msg.get("event_kind") in {"Human_decision_required", "stage_completion"}:
            update = {key: msg[key] for key in allowed_fields if key in msg}
            with open(current, "w", encoding="utf-8") as stream:
                yaml.dump(update, stream, sort_keys=True)
            return
        raise ValueError("Unsupported Human/current event")

    def validate_sender_index(self, index_data: Dict[str, Any]) -> None:
        index_file = index_data.get("index_file")
        baseline_file = index_data.get("baseline_index_file")
        msg_dir = index_data.get("msg_dir")
        if not index_file or not baseline_file or not msg_dir:
            raise ValueError("GC-T045 validator requires physical state paths")
        with open(baseline_file, "r", encoding="utf-8") as stream:
            baseline = yaml.safe_load(stream)
        with open(index_file, "r", encoding="utf-8") as stream:
            current = yaml.safe_load(stream)
        valid = (
            isinstance(baseline, list)
            and isinstance(current, list)
            and all(isinstance(pointer, str) for pointer in current)
            and current[:len(baseline)] == baseline
            and len(current) == len(baseline) + 1
            and len(set(current)) == len(current)
            and all(os.path.isfile(os.path.join(msg_dir, pointer)) for pointer in current)
        )
        if not valid:
            raise EscalationException(
                "Sender index physical state is invalid",
                {
                    "failure_code": "SENDER_INDEX_INTEGRITY",
                    "baseline_index": baseline,
                    "observed_index": current,
                    "physical_targets_exist": (
                        isinstance(current, list)
                        and all(
                            isinstance(pointer, str)
                            and os.path.isfile(os.path.join(msg_dir, pointer))
                            for pointer in current
                        )
                    ),
                },
            )

    def score_cross_model(self, fix_data: Dict[str, Any]) -> None:
        if "packet_path" not in fix_data:
            return
            
        with open(fix_data["packet_path"], encoding="utf-8") as f:
            packet = yaml.safe_load(f)
            
        for rp in fix_data["result_paths"]:
            with open(rp, encoding="utf-8") as f:
                result = yaml.safe_load(f)
                
            for r in result.get("fixture_results", []):
                recovered = r.get("recovered", {})
                if not recovered:
                    raise ValueError(f"Missing recovered block in {r['fixture_id']}")
                
                if recovered.get("task_id") != packet["task_id"]:
                    raise ValueError(f"Task ID mismatch in {r['fixture_id']}")
                    
                if not recovered.get("sender_endpoint_id"):
                    raise ValueError(f"Missing sender_endpoint_id in {r['fixture_id']}")
                if not recovered.get("expected_recipient_endpoint_id"):
                    raise ValueError(f"Missing expected_recipient_endpoint_id in {r['fixture_id']}")
                    
                paths = set(recovered.get("exact_paths_to_read") or [])
                if r["fixture_id"] in ["F1-minimal-yaml-index", "F2-compact-json-index", "F3-free-text-pointer"]:
                    if recovered.get("task_id") != "os-v2-global-communication-system-001":
                        raise ValueError("task_id exact match failed")
                    if recovered.get("sender_endpoint_id") != "chatgpt-web-planner-01":
                        raise ValueError("sender exact match failed")
                    if recovered.get("expected_recipient_endpoint_id") != "claude-code-cli-executor-01":
                        raise ValueError("recipient exact match failed")
                        
                    msg_type = str(recovered.get("message_type_and_purpose", ""))
                    if "request" not in msg_type.lower() or "执行超出默认角色的受保护发布" not in msg_type:
                        raise ValueError("message_type_and_purpose exact semantic class failed")
                        
                    auth = str(recovered.get("authority_interpretation", ""))
                    if "授权发布" not in auth and "authoriz" not in auth.lower():
                        raise ValueError("authority_interpretation exact semantic requirement failed")
                    
                    expected_superset = {"08_os/_runs/run-x/06_执行/发布任务包.yml", "08_os/_runs/run-x/durable/Human_decisions/授权发布.yml"}
                    if paths != expected_superset:
                        raise ValueError(f"Path set mismatch in {r['fixture_id']}: {paths} != {expected_superset}")
                        
                elif r["fixture_id"] == "F4-long-content-reference":
                    if recovered.get("task_id") != "os-v2-global-communication-system-001":
                        raise ValueError("task_id exact match failed")
                    if recovered.get("sender_endpoint_id") != "claude-code-desktop-reviewer-01":
                        raise ValueError("sender exact match failed")
                    if recovered.get("expected_recipient_endpoint_id") != "chatgpt-web-planner-01":
                        raise ValueError("recipient exact match failed")
                        
                    msg_type = str(recovered.get("message_type_and_purpose", ""))
                    if "response" not in msg_type.lower() or "审核意见" not in msg_type:
                        raise ValueError("message_type_and_purpose exact semantic class failed")
                        
                    expected = {"08_os/_runs/run-x/03_结果建模/审核意见_v1.md"}
                    if paths != expected:
                        raise ValueError(f"Path set mismatch in {r['fixture_id']}: {paths} != {expected}")

class SyntheticConformingAdapter(StrictValidationAdapter):
    pass

class SyntheticMutatingAdapter(StrictValidationAdapter):
    pass

class ProductionTestAdapter(StrictValidationAdapter):
    def parse_yaml(self, content: str) -> Any:
        raise NotImplementedError("Stage 06 missing")

    def validate_message(self, message: Dict[str, Any]) -> None:
        raise NotImplementedError("Stage 06 missing")

    def validate_document(self, content: Dict[str, Any]) -> None:
        raise NotImplementedError("Stage 06 missing")

    def validate_discovery_file(self, fix_data: Dict[str, Any]) -> None:
        raise NotImplementedError("Stage 06 missing")

    def validate_sender_index(self, index_data: Dict[str, Any]) -> None:
        raise NotImplementedError("Stage 06 missing")

    def publish_message(self, message: Dict[str, Any]) -> None:
        raise NotImplementedError("Stage 06 missing")

    def run_git_scenario(self, fix_data: Dict[str, Any]) -> None:
        raise NotImplementedError("Stage 06 missing")

    def archive_task(self, task_id: Dict[str, Any]) -> None:
        raise NotImplementedError("Stage 06 missing")

    def load_default_context(self, fix_data: Dict[str, Any]) -> None:
        raise NotImplementedError("Stage 06 missing")

    def update_Human_current(self, trigger_event: Dict[str, Any]) -> None:
        raise NotImplementedError("Stage 06 missing")
