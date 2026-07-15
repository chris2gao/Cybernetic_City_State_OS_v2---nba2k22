"""Deterministic repository-level Human-AI communication compliance gate.

The gate validates durable C1/C2 artifacts and transition eligibility.  It does
not intercept live model output, execute transitions, or grant Human authority.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable

try:
    import yaml
except Exception:  # pragma: no cover - exercised by dependency error contract
    yaml = None

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover - exercised by dependency error contract
    Draft202012Validator = None


VALIDATOR_VERSION = "1.0.0"
EXIT_PASS = 0
EXIT_COMPLIANCE_FAIL = 1
EXIT_INVOCATION = 2
EXIT_INPUT = 3
EXIT_CONFIG = 4
EXIT_INTERNAL = 5
MAX_INPUT_BYTES = 2_000_000
ZERO_SHA256 = "0" * 64
ZERO_SHA1 = "0" * 40
HERE = Path(__file__).resolve().parent
DEFAULT_POLICY = HERE / "material_event_policy.yml"
DEFAULT_FIXTURE_SUITE = HERE / "fixtures" / "fixture_suite.json"


class ComplianceError(Exception):
    """Base class for stable, user-facing gate failures."""


class InvocationError(ComplianceError):
    pass


class InputDocumentError(ComplianceError):
    pass


class ConfigurationError(ComplianceError):
    pass


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # pragma: no cover - argparse path
        del message
        raise InvocationError("invalid command-line invocation")


if yaml is not None:

    class StrictSafeLoader(yaml.SafeLoader):
        """Safe loader that rejects duplicate and merge keys."""


    def _construct_unique_mapping(
        loader: StrictSafeLoader, node: Any, deep: bool = False
    ) -> dict[Any, Any]:
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            if getattr(key_node, "value", None) == "<<":
                raise InputDocumentError("YAML merge keys are forbidden")
            key = loader.construct_object(key_node, deep=deep)
            if key in mapping:
                raise InputDocumentError("duplicate mapping key")
            mapping[key] = loader.construct_object(value_node, deep=deep)
        return mapping


    StrictSafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        _construct_unique_mapping,
    )


def _json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InputDocumentError("duplicate mapping key")
        result[key] = value
    return result


def _reject_yaml_indirection(text: str) -> None:
    if yaml is None:
        raise ConfigurationError("PyYAML is required by the compliance gate")
    document_starts = 0
    try:
        for token in yaml.scan(text):
            name = type(token).__name__
            if name == "DocumentStartToken":
                document_starts += 1
            if name in {"AnchorToken", "AliasToken", "TagToken"}:
                raise InputDocumentError("YAML anchors, aliases, and tags are forbidden")
    except InputDocumentError:
        raise
    except Exception as exc:
        raise InputDocumentError("invalid YAML document") from exc
    if document_starts > 1:
        raise InputDocumentError("multiple YAML documents are forbidden")


def load_text_document(text: str, suffix: str = ".json") -> Any:
    if len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        raise InputDocumentError("input exceeds the deterministic size limit")
    if suffix.lower() == ".json":
        try:
            return json.loads(text, object_pairs_hook=_json_pairs)
        except InputDocumentError:
            raise
        except Exception as exc:
            raise InputDocumentError("invalid JSON document") from exc
    if yaml is None:
        raise ConfigurationError("PyYAML is required by the compliance gate")
    _reject_yaml_indirection(text)
    try:
        documents = list(yaml.load_all(text, Loader=StrictSafeLoader))
    except InputDocumentError:
        raise
    except Exception as exc:
        raise InputDocumentError("invalid YAML document") from exc
    if len(documents) != 1:
        raise InputDocumentError("exactly one YAML document is required")
    return documents[0]


def load_document(path: Path) -> Any:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise InputDocumentError("input file cannot be read") from exc
    if len(data) > MAX_INPUT_BYTES:
        raise InputDocumentError("input exceeds the deterministic size limit")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputDocumentError("input must be UTF-8") from exc
    return load_text_document(text, path.suffix)


def canonical_bytes(value: Any, *, preserve_mapping_order: bool = True) -> bytes:
    def transform(item: Any) -> Any:
        if isinstance(item, dict):
            pairs = [[str(key), transform(val)] for key, val in item.items()]
            if not preserve_mapping_order:
                pairs.sort(key=lambda pair: pair[0])
            return {"__ordered_mapping__": pairs}
        if isinstance(item, list):
            return [transform(value) for value in item]
        return item

    return json.dumps(
        transform(value), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def digest_object(value: Any, *, preserve_mapping_order: bool = True) -> str:
    return hashlib.sha256(
        canonical_bytes(value, preserve_mapping_order=preserve_mapping_order)
    ).hexdigest()


def serialize_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def finding(code: str, path: str, message: str, severity: str = "error") -> dict[str, str]:
    return {"code": code, "path": path, "message": message, "severity": severity}


def sorted_findings(items: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    unique: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for item in items:
        key = (item["code"], item["path"], item["message"], item["severity"])
        unique[key] = item
    return [unique[key] for key in sorted(unique)]


def nullable_string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def normalized_event_class(value: Any) -> str:
    return (
        value
        if isinstance(value, str) and value in {"C0", "C1", "C2", "unknown"}
        else "unknown"
    )


def nullable_sha256(value: Any) -> str | None:
    return value if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) else None


def safe_repo_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\x00" in value:
        return None
    if "\\" in value or ":" in value or value.startswith("/"):
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path.as_posix()


def _run_git(repo_root: Path, arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        shell=False,
    )


@lru_cache(maxsize=512)
def _git_blob(repo_root: Path, commit: str, path: str) -> tuple[str, bytes] | None:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        return None
    tree = _run_git(repo_root, ["ls-tree", "-z", commit, "--", path])
    if tree.returncode != 0 or not tree.stdout.endswith(b"\x00"):
        return None
    entries = [entry for entry in tree.stdout.split(b"\x00") if entry]
    if len(entries) != 1 or b"\t" not in entries[0]:
        return None
    metadata, encoded_path = entries[0].split(b"\t", 1)
    try:
        actual_path = encoded_path.decode("utf-8")
        mode, object_type, object_sha = metadata.decode("ascii").split()
    except (UnicodeDecodeError, ValueError):
        return None
    if actual_path != path or object_type != "blob" or mode in {"120000", "160000"}:
        return None
    content = _run_git(repo_root, ["cat-file", "blob", object_sha])
    if content.returncode != 0:
        return None
    return object_sha, content.stdout


@lru_cache(maxsize=512)
def _fixture_blob(repo_root: Path, path: str) -> tuple[str, bytes] | None:
    candidate = repo_root.joinpath(*PurePosixPath(path).parts)
    try:
        resolved_root = repo_root.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError):
        return None
    current = candidate
    while current != repo_root.parent and current != repo_root:
        if current.is_symlink():
            return None
        current = current.parent
    if not resolved.is_file():
        return None
    try:
        content = resolved.read_bytes()
    except OSError:
        return None
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest(), content


def resolve_reference(
    repo_root: Path,
    reference: Any,
    *,
    test_mode: bool,
) -> tuple[dict[str, Any], bytes | None, list[dict[str, str]]]:
    violations: list[dict[str, str]] = []
    if not isinstance(reference, dict):
        violations.append(
            finding("REFERENCE_INVALID", "required_refs", "reference must be an object")
        )
        return (
            {
                "kind": "git_blob",
                "commit": None,
                "path": "",
                "blob_sha": None,
                "status": "unresolved",
                "content_sha256": ZERO_SHA256,
            },
            None,
            violations,
        )
    kind = reference.get("kind")
    path = safe_repo_path(reference.get("path"))
    expected_sha = reference.get("content_sha256")
    if kind not in {"git_blob", "test_fixture_blob"}:
        violations.append(
            finding("REFERENCE_KIND_INVALID", "required_refs.kind", "reference kind is not allowed")
        )
        kind = "git_blob"
    if path is None:
        violations.append(
            finding("REFERENCE_PATH_INVALID", "required_refs.path", "reference path is unsafe")
        )
        path = ""
    if not isinstance(expected_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        violations.append(
            finding(
                "REFERENCE_DIGEST_INVALID",
                "required_refs.content_sha256",
                "reference digest must be a lowercase SHA-256",
            )
        )
        expected_sha = ZERO_SHA256

    commit: str | None = None
    resolved: tuple[str, bytes] | None = None
    if kind == "git_blob":
        commit = reference.get("commit")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            violations.append(
                finding(
                    "REFERENCE_COMMIT_INVALID",
                    "required_refs.commit",
                    "git reference requires an immutable full commit SHA",
                )
            )
            commit = None
        elif path:
            resolved = _git_blob(repo_root, commit, path)
    else:
        if not test_mode or reference.get("test_only") is not True:
            violations.append(
                finding(
                    "TEST_REFERENCE_FORBIDDEN",
                    "required_refs.kind",
                    "test fixture references are forbidden outside explicit test mode",
                )
            )
        elif path:
            resolved = _fixture_blob(repo_root, path)

    if resolved is None:
        violations.append(
            finding("REFERENCE_UNRESOLVED", "required_refs", "required reference did not resolve")
        )
        return (
            {
                "kind": kind,
                "commit": commit,
                "path": path,
                "blob_sha": None,
                "status": "unresolved",
                "content_sha256": expected_sha,
            },
            None,
            violations,
        )
    blob_sha, content = resolved
    actual_sha = hashlib.sha256(content).hexdigest()
    if actual_sha != expected_sha:
        violations.append(
            finding(
                "REFERENCE_DIGEST_MISMATCH",
                "required_refs.content_sha256",
                "resolved content does not match the declared digest",
            )
        )
    status = "resolved" if not violations else "unresolved"
    return (
        {
            "kind": kind,
            "commit": commit,
            "path": path,
            "blob_sha": blob_sha,
            "status": status,
            "content_sha256": actual_sha,
        },
        content,
        violations,
    )


def load_policy(path: Path) -> tuple[dict[str, Any], str]:
    if yaml is None or Draft202012Validator is None:
        raise ConfigurationError("PyYAML and jsonschema are required")
    policy = load_document(path)
    if not isinstance(policy, dict):
        raise ConfigurationError("material-event policy must be a mapping")
    required = {
        "policy_version",
        "validator_version",
        "protocol_head",
        "wire_schemas",
        "role_mapping",
        "event_classes",
        "transitions",
    }
    if not required.issubset(policy):
        raise ConfigurationError("material-event policy is incomplete")
    if policy.get("validator_version") != VALIDATOR_VERSION:
        raise ConfigurationError("policy and validator versions differ")
    if not re.fullmatch(r"[0-9a-f]{40}", str(policy.get("protocol_head", ""))):
        raise ConfigurationError("policy protocol head is invalid")
    return policy, digest_object(policy, preserve_mapping_order=False)


def load_schema(name: str) -> dict[str, Any]:
    if Draft202012Validator is None:
        raise ConfigurationError("jsonschema is required")
    value = load_document(HERE / name)
    if not isinstance(value, dict):
        raise ConfigurationError("schema document must be an object")
    try:
        Draft202012Validator.check_schema(value)
    except Exception as exc:
        raise ConfigurationError("invalid JSON Schema configuration") from exc
    return value


def schema_findings(
    instance: Any,
    schema_name: str,
    label: str,
) -> list[dict[str, str]]:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: (
            tuple(str(item) for item in error.absolute_path),
            str(error.validator),
        ),
    )
    findings: list[dict[str, str]] = []
    for error in errors[:20]:
        path = ".".join(str(item) for item in error.absolute_path)
        findings.append(
            finding(
                f"{label}_SCHEMA_INVALID",
                path,
                f"{label.lower().replace('_', ' ')} does not conform to its v1 schema",
            )
        )
    return findings


def classify_event(event_type: Any, policy: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    if not isinstance(event_type, str):
        return "unknown", [
            finding("EVENT_TYPE_INVALID", "event_type", "event type must be a string")
        ]
    matches = [
        class_name
        for class_name, config in policy["event_classes"].items()
        if event_type in config.get("event_types", [])
    ]
    if len(matches) != 1:
        return "unknown", [
            finding(
                "UNKNOWN_EVENT_TYPE",
                "event_type",
                "unknown events fail closed and cannot self-classify as C0",
            )
        ]
    return matches[0], []


def _validate_schema_to(
    value: Any,
    schema_name: str,
    label: str,
    violations: list[dict[str, str]],
) -> bool:
    found = schema_findings(value, schema_name, label)
    violations.extend(found)
    return not found


def validate_bootstrap_receipt(
    receipt: Any,
    repo_root: Path,
    policy: dict[str, Any],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    violations: list[dict[str, str]] = []
    resolved_refs: list[dict[str, Any]] = []
    if not _validate_schema_to(
        receipt, "bootstrap_receipt.schema.json", "BOOTSTRAP_RECEIPT", violations
    ):
        return violations, resolved_refs
    assert isinstance(receipt, dict)
    if receipt["protocol_head"] != policy["protocol_head"]:
        violations.append(
            finding(
                "BOOTSTRAP_PROTOCOL_HEAD_STALE",
                "bootstrap_receipt.protocol_head",
                "bootstrap receipt is bound to a different protocol head",
            )
        )
    expected_role = policy["role_mapping"].get(receipt["provider"])
    if not expected_role or expected_role["occupied_role"] != receipt["occupied_role"]:
        violations.append(
            finding(
                "BOOTSTRAP_ROLE_MISMATCH",
                "bootstrap_receipt.occupied_role",
                "provider and occupied role do not match the provider-neutral role map",
            )
        )
    if expected_role and expected_role["wire_schema"] != receipt["wire_schema"]:
        violations.append(
            finding(
                "BOOTSTRAP_WIRE_SCHEMA_MISMATCH",
                "bootstrap_receipt.wire_schema",
                "occupied role uses the wrong frozen wire schema",
            )
        )

    loaded_paths: list[str] = []
    for loaded in receipt["loaded_files"]:
        loaded_paths.append(loaded["path"])
        if loaded["commit"] != receipt["protocol_head"]:
            violations.append(
                finding(
                    "BOOTSTRAP_LOADED_FILE_HEAD_MISMATCH",
                    "bootstrap_receipt.loaded_files",
                    "bootstrap file evidence must resolve at the receipt protocol head",
                )
            )
        ref = {"kind": "git_blob", **loaded}
        resolved, _content, ref_violations = resolve_reference(
            repo_root, ref, test_mode=False
        )
        resolved_refs.append(resolved)
        for item in ref_violations:
            item = dict(item)
            item["code"] = "BOOTSTRAP_" + item["code"]
            item["path"] = "bootstrap_receipt.loaded_files"
            violations.append(item)
    if len(loaded_paths) != len(set(loaded_paths)):
        violations.append(
            finding(
                "BOOTSTRAP_LOADED_FILE_DUPLICATE",
                "bootstrap_receipt.loaded_files",
                "loaded file claims must be unique",
            )
        )
    missing = set(policy.get("bootstrap_required_loaded_files", [])) - set(loaded_paths)
    if missing:
        violations.append(
            finding(
                "BOOTSTRAP_REQUIRED_FILE_MISSING",
                "bootstrap_receipt.loaded_files",
                "bootstrap receipt omits a required always-loaded file",
            )
        )
    on_demand = {item["path"]: item for item in receipt["inherited_on_demand"]}
    for required_path in policy.get("bootstrap_on_demand_requirements", {}).get(
        receipt["occupied_role"], []
    ):
        item = on_demand.get(required_path)
        if item is None or item.get("loaded") is not True or required_path not in loaded_paths:
            violations.append(
                finding(
                    "BOOTSTRAP_ON_DEMAND_FILE_NOT_LOADED",
                    "bootstrap_receipt.inherited_on_demand",
                    "role-triggered inherited protocol is not verifiably loaded",
                )
            )
    return sorted_findings(violations), sorted_resolved_refs(resolved_refs)


def sorted_resolved_refs(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            str(item.get("kind")),
            str(item.get("commit")),
            str(item.get("path")),
            str(item.get("content_sha256")),
        ),
    )


def validate_pointer(
    pointer: Any,
    expected_wire: str | None,
    policy: dict[str, Any],
    *,
    proposed_transition: Any,
) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    if not isinstance(pointer, dict):
        return [finding("POINTER_REQUIRED", "pointer", "machine consumer requires a pointer")]
    allowed_outer = {"wire_schema", "data", "extra_text"}
    if set(pointer) != allowed_outer:
        violations.append(
            finding(
                "POINTER_ENVELOPE_INVALID",
                "pointer",
                "pointer envelope must contain only wire_schema, data, and extra_text",
            )
        )
    wire = pointer.get("wire_schema")
    if wire != expected_wire or wire not in policy["wire_schemas"]:
        violations.append(
            finding(
                "POINTER_WIRE_SCHEMA_MISMATCH",
                "pointer.wire_schema",
                "pointer wire schema does not match the occupied role",
            )
        )
        return violations
    data = pointer.get("data")
    if not isinstance(data, dict):
        violations.append(
            finding("POINTER_DATA_INVALID", "pointer.data", "pointer data must be one mapping")
        )
        return violations
    spec = policy["wire_schemas"][wire]
    actual_keys = list(data.keys())
    core = spec["core_keys"]
    optional_tail = spec.get("optional_tail_keys", [])
    valid_key_sequences = [core]
    if optional_tail:
        valid_key_sequences.append(core + optional_tail)
    if actual_keys not in valid_key_sequences:
        missing = [key for key in core if key not in data]
        extras = [key for key in actual_keys if key not in core + optional_tail]
        order_only = not missing and not extras and set(actual_keys) == set(core)
        code = "POINTER_KEY_ORDER_INVALID" if order_only else "POINTER_FIELDS_INVALID"
        violations.append(
            finding(
                code,
                "pointer.data",
                "pointer keys must exactly match the frozen key names and order",
            )
        )
    if pointer.get("extra_text") not in {None, ""}:
        violations.append(
            finding(
                "POINTER_PROSE_CONTAMINATION",
                "pointer.extra_text",
                "machine pointer cannot contain prose before or after the canonical mapping",
            )
        )
    for key, value in data.items():
        if key.endswith("_ref") and value is not None and safe_repo_path(value) is None:
            violations.append(
                finding(
                    "POINTER_REF_INVALID",
                    f"pointer.data.{key}",
                    "pointer reference must be null or a safe repository-relative path",
                )
            )
    for key in core:
        if key.endswith("_ref") or key in {"source_head", "review_branch_head"}:
            continue
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            violations.append(
                finding(
                    "POINTER_VALUE_INVALID",
                    f"pointer.data.{key}",
                    "canonical non-reference pointer values must be non-empty strings",
                )
            )
    if "source_head" in data and not re.fullmatch(
        r"[0-9a-f]{40}", str(data.get("source_head", ""))
    ):
        violations.append(
            finding(
                "POINTER_SOURCE_HEAD_INVALID",
                "pointer.data.source_head",
                "pointer source head must be an immutable full commit SHA",
            )
        )
    review_head = data.get("review_branch_head")
    if "review_branch_head" in data:
        if review_head != "self" and not re.fullmatch(r"[0-9a-f]{40}", str(review_head or "")):
            violations.append(
                finding(
                    "POINTER_REVIEW_HEAD_INVALID",
                    "pointer.data.review_branch_head",
                    "review branch head must be self or an immutable full commit SHA",
                )
            )
        if review_head == "self" and proposed_transition is not None:
            violations.append(
                finding(
                    "POINTER_SELF_UNRESOLVED",
                    "pointer.data.review_branch_head",
                    "self must be resolved to a concrete review head before transition validation",
                )
            )
    return violations


def sentence_count(text: str) -> int:
    return len(re.findall(r"(?:[。！？]+|[.!?]+(?:\s|$))", text.strip()))


def contains_cot_request(text: str) -> bool:
    patterns = [
        (
            r"\b(show|provide|reveal|write|store|include|display|expose)\b.{0,60}"
            r"\b(chain[- ]of[- ]thought|private reasoning|hidden reasoning|internal reasoning)\b"
        ),
        r"(展示|提供|披露|记录|存储|输出).{0,30}(思维链|隐藏推理|私有推理|内部推理)",
    ]
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns)


def contains_authorization_claim(text: str) -> bool:
    lowered = text.lower()
    patterns = [
        r"\b(i|we|this expression)\s+(authorize|approve|grant permission)\b",
        r"\bpermission\s+(is\s+)?granted\b",
        r"\bapproved\s+to\s+(push|merge|rebase|activate|change|publish)\b",
        r"(我|我们|本表达).{0,8}(授权|批准|准许).{0,20}(推送|合并|发布|激活|改变目标|路由)",
    ]
    negative_markers = [
        "does not authorize",
        "cannot authorize",
        "is not authorization",
        "no permission is granted",
        "不授权",
        "不能授权",
        "不是授权",
    ]
    if any(marker in lowered for marker in negative_markers):
        scrubbed = lowered
        for marker in negative_markers:
            scrubbed = scrubbed.replace(marker, "")
    else:
        scrubbed = lowered
    return any(re.search(pattern, scrubbed, flags=re.IGNORECASE) for pattern in patterns)


def validate_expression(
    expression: Any,
    policy: dict[str, Any],
    *,
    path: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]], bool, str]:
    violations: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(expression, dict):
        return (
            [finding("INDEPENDENT_EXPRESSION_REQUIRED", path, "material event requires independent expression")],
            warnings,
            False,
            "",
        )
    if set(expression) != {"heading", "text", "separated_from_authority"}:
        violations.append(
            finding(
                "INDEPENDENT_EXPRESSION_FIELDS_INVALID",
                path,
                "independent expression contains unsupported structured fields",
            )
        )
    if expression.get("heading") != policy["expression_policy"]["heading"]:
        violations.append(
            finding(
                "INDEPENDENT_EXPRESSION_HEADING_INVALID",
                f"{path}.heading",
                "independent expression must use the canonical visible heading",
            )
        )
    text = expression.get("text")
    if not isinstance(text, str) or not text.strip():
        violations.append(
            finding(
                "INDEPENDENT_EXPRESSION_EMPTY",
                f"{path}.text",
                "independent expression text is empty",
            )
        )
        text = ""
    count = sentence_count(text)
    minimum = policy["expression_policy"]["minimum_sentences"]
    maximum = policy["expression_policy"]["maximum_sentences"]
    if count < minimum or count > maximum:
        violations.append(
            finding(
                "INDEPENDENT_EXPRESSION_SENTENCE_COUNT",
                f"{path}.text",
                "independent expression must contain two to five visible sentences",
            )
        )
    if expression.get("separated_from_authority") is not True:
        violations.append(
            finding(
                "INDEPENDENT_EXPRESSION_NOT_SEPARATED",
                path,
                "independent expression must be separated from evidence and authority",
            )
        )
    if contains_authorization_claim(text):
        violations.append(
            finding(
                "EXPRESSION_FALSE_AUTHORIZATION",
                f"{path}.text",
                "independent expression cannot grant a protected permission",
            )
        )
    if contains_cot_request(text):
        violations.append(
            finding(
                "HIDDEN_REASONING_REQUEST",
                f"{path}.text",
                "visible content requests or discloses hidden reasoning",
            )
        )
    lowered = text.lower()
    if any(phrase in lowered for phrase in policy["expression_policy"]["generic_warning_phrases"]):
        warnings.append(
            finding(
                "EXPRESSION_GENERIC_WARNING",
                f"{path}.text",
                "expression may need foreground semantic review for low information value",
                "warning",
            )
        )
    return violations, warnings, not violations, text


def validate_recommendation(
    recommendation: Any,
    policy: dict[str, Any],
    resolved_refs: list[dict[str, Any]],
    *,
    path: str,
) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    expected = policy["execution_recommendation_fields"]
    if not isinstance(recommendation, dict):
        return [
            finding(
                "EXECUTION_RECOMMENDATION_REQUIRED",
                path,
                "backend dispatch requires a complete execution recommendation",
            )
        ]
    if set(recommendation) != set(expected):
        violations.append(
            finding(
                "EXECUTION_RECOMMENDATION_FIELDS_INVALID",
                path,
                "execution recommendation must contain all seven fields and no extras",
            )
        )
    for key in expected:
        value = recommendation.get(key)
        if value is None or value == "" or value == [] or value == {}:
            violations.append(
                finding(
                    "EXECUTION_RECOMMENDATION_FIELD_EMPTY",
                    f"{path}.{key}",
                    "execution recommendation field cannot be omitted or empty",
                )
            )
    task_ref = recommendation.get("task_ref_or_plan_ref")
    matching = {
        (
            item.get("kind"),
            item.get("commit"),
            item.get("path"),
            item.get("content_sha256"),
        )
        for item in resolved_refs
        if item.get("path") == task_ref and item.get("status") == "resolved"
    }
    if not isinstance(task_ref, str) or len(matching) != 1:
        violations.append(
            finding(
                "EXECUTION_RECOMMENDATION_REF_UNRESOLVED",
                f"{path}.task_ref_or_plan_ref",
                "task_ref_or_plan_ref must resolve to exactly one durable artifact",
            )
        )
    return violations


def _section(text: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)"
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        return None
    return matches[0].strip()


def _yaml_fence(section: str | None) -> Any:
    if section is None:
        return None
    match = re.search(r"(?ms)^```yaml\s*$\n(.*?)^```\s*$", section)
    if not match:
        return None
    return load_text_document(match.group(1), ".yml")


def parse_human_brief(content: bytes) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    violations: list[dict[str, str]] = []
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None, [finding("BRIEF_ENCODING_INVALID", "brief", "Human Brief must be UTF-8")]
    if not re.search(r"(?m)^# Human Brief\s*$", text):
        violations.append(
            finding("BRIEF_TITLE_MISSING", "brief", "durable fallback is not a Human Brief")
        )
    factual = _section(text, "Factual status")
    if not factual:
        violations.append(
            finding("BRIEF_FACTUAL_STATUS_MISSING", "brief", "Human Brief lacks factual status")
        )
    try:
        recommendation = _yaml_fence(_section(text, "Execution recommendation"))
        preflight = _yaml_fence(_section(text, "Human-response preflight"))
    except InputDocumentError:
        recommendation = None
        preflight = None
        violations.append(
            finding("BRIEF_YAML_INVALID", "brief", "Human Brief contains invalid structured content")
        )
    expression_section = _section(text, "Independent expression")
    expression = None
    if expression_section is not None:
        expression = {
            "heading": "Independent expression",
            "text": expression_section,
            "separated_from_authority": True,
        }
    return (
        {
            "factual_status": factual or "",
            "execution_recommendation": recommendation,
            "preflight": preflight,
            "independent_expression": expression,
        },
        violations,
    )


def validate_human_content(
    content: Any,
    policy: dict[str, Any],
    resolved_refs: list[dict[str, Any]],
    *,
    dispatch: bool,
    pointer_present: bool,
    pointer_applicable: bool,
    all_refs_resolved: bool,
    path: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    violations: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(content, dict):
        return [
            finding(
                "HUMAN_CONTENT_REQUIRED",
                path,
                "material Human-facing content is required",
            )
        ], warnings
    if set(content) != {
        "factual_status",
        "execution_recommendation",
        "preflight",
        "independent_expression",
    }:
        violations.append(
            finding(
                "HUMAN_CONTENT_FIELDS_INVALID",
                path,
                "Human operational content contains unsupported structured fields",
            )
        )
    factual = content.get("factual_status")
    if not isinstance(factual, str) or not factual.strip():
        violations.append(
            finding(
                "FACTUAL_STATUS_MISSING",
                f"{path}.factual_status",
                "material Human-facing content requires factual status",
            )
        )
        factual = ""
    expression_violations, expression_warnings, expression_valid, expression_text = (
        validate_expression(
            content.get("independent_expression"),
            policy,
            path=f"{path}.independent_expression",
        )
    )
    violations.extend(expression_violations)
    warnings.extend(expression_warnings)
    recommendation = content.get("execution_recommendation")
    recommendation_valid = True
    if dispatch or recommendation is not None:
        recommendation_violations = validate_recommendation(
            recommendation, policy, resolved_refs, path=f"{path}.execution_recommendation"
        )
        violations.extend(recommendation_violations)
        recommendation_valid = not recommendation_violations
    preflight = content.get("preflight")
    expected_preflight = policy["human_response_preflight_fields"]
    if not isinstance(preflight, dict) or set(preflight) != set(expected_preflight):
        violations.append(
            finding(
                "HUMAN_RESPONSE_PREFLIGHT_FIELDS_INVALID",
                f"{path}.preflight",
                "Human-response preflight must contain all eight fields and no extras",
            )
        )
        preflight = preflight if isinstance(preflight, dict) else {}
    computed = {
        "factual_status_grounded": bool(factual.strip()),
        "required_refs_dereferenced": all_refs_resolved,
        "canonical_pointer_present_when_applicable": (not pointer_applicable) or pointer_present,
        "execution_recommendation_present_when_dispatching": (not dispatch)
        or recommendation_valid,
        "independent_expression_present_for_material_event": expression_valid,
        "independent_expression_separated_from_authority": bool(
            isinstance(content.get("independent_expression"), dict)
            and content["independent_expression"].get("separated_from_authority") is True
        ),
        "no_long_task_or_report_echo": len(factual) <= 4000,
        "no_hidden_chain_of_thought_request_or_disclosure": not contains_cot_request(
            factual + "\n" + expression_text
        ),
    }
    for field_name in expected_preflight:
        if preflight.get(field_name) is not True:
            violations.append(
                finding(
                    "HUMAN_RESPONSE_PREFLIGHT_FIELD_FALSE",
                    f"{path}.preflight.{field_name}",
                    "required Human-response preflight field must be true",
                )
            )
        if not computed[field_name]:
            violations.append(
                finding(
                    "HUMAN_RESPONSE_PREFLIGHT_EVIDENCE_MISMATCH",
                    f"{path}.preflight.{field_name}",
                    "preflight claim is not supported by deterministic evidence",
                )
            )
    if contains_cot_request(factual):
        violations.append(
            finding(
                "HIDDEN_REASONING_REQUEST",
                f"{path}.factual_status",
                "visible content requests or discloses hidden reasoning",
            )
        )
    return sorted_findings(violations), sorted_findings(warnings)


def _make_result(
    *,
    policy: dict[str, Any],
    policy_sha: str,
    event_id: str | None,
    task_id: str | None,
    event_type: str | None,
    role: str | None,
    event_class: str,
    input_sha: str,
    receipt_sha: str | None,
    checked_contracts: Iterable[str],
    resolved_refs: Iterable[dict[str, Any]],
    violations: Iterable[dict[str, str]],
    warnings: Iterable[dict[str, str]],
    proposed_transition: Any = None,
    transition_eligible: bool = False,
    error: bool = False,
) -> dict[str, Any]:
    final_violations = sorted_findings(violations)
    result = "error" if error else ("fail" if final_violations else "pass")
    return {
        "schema_version": "human_ai.communication_validation.v1",
        "validator_version": VALIDATOR_VERSION,
        "event_id": event_id,
        "task_id": task_id,
        "event_type": event_type,
        "result": result,
        "violations": final_violations,
        "warnings": sorted_findings(warnings),
        "checked_contracts": sorted(set(checked_contracts)),
        "protocol_head": policy["protocol_head"],
        "role": role,
        "event_class": event_class,
        "resolved_refs": sorted_resolved_refs(resolved_refs),
        "input_sha256": input_sha,
        "policy_sha256": policy_sha,
        "bootstrap_receipt_sha256": receipt_sha,
        "proposed_transition": proposed_transition,
        "transition_eligible": bool(transition_eligible and not final_violations),
        "authorization_granted_by_validator": False,
    }


def ensure_result_schema(result: dict[str, Any]) -> None:
    errors = schema_findings(
        result, "communication_validation.schema.json", "COMMUNICATION_VALIDATION"
    )
    if errors:
        raise ConfigurationError("validator produced an invalid result contract")


def validate_event(
    event: Any,
    repo_root: Path,
    policy: dict[str, Any],
    policy_sha: str,
    *,
    test_mode: bool = False,
) -> dict[str, Any]:
    violations: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    checked = {"material_event_classifier", "communication_event_schema"}
    input_sha = digest_object(event)
    _validate_schema_to(event, "communication_event.schema.json", "EVENT", violations)
    if not isinstance(event, dict):
        result = _make_result(
            policy=policy,
            policy_sha=policy_sha,
            event_id=None,
            task_id=None,
            event_type=None,
            role=None,
            event_class="unknown",
            input_sha=input_sha,
            receipt_sha=None,
            checked_contracts=checked,
            resolved_refs=[],
            violations=violations,
            warnings=warnings,
        )
        ensure_result_schema(result)
        return result

    event_type = event.get("event_type")
    event_class, class_violations = classify_event(event_type, policy)
    violations.extend(class_violations)
    claimed = event.get("claimed_event_class")
    if claimed is not None and claimed != event_class:
        violations.append(
            finding(
                "EVENT_CLASS_MISMATCH",
                "claimed_event_class",
                "claimed event class differs from deterministic policy classification",
            )
        )
    if event_class == "C0" and event.get("proposed_transition") is not None:
        violations.append(
            finding(
                "C0_TRANSITION_FORBIDDEN",
                "proposed_transition",
                "C0 conversation cannot carry a workflow transition",
            )
        )

    provider = event.get("provider")
    role_config = policy["role_mapping"].get(provider)
    role = event.get("occupied_role")
    role_check_required = event_class in policy.get("material_event_classes", []) or role is not None
    if role_config is None and role_check_required:
        violations.append(
            finding("PROVIDER_UNMAPPED", "provider", "provider is not mapped to a stable role")
        )
    elif role_check_required and role_config is not None and role != role_config["occupied_role"]:
        violations.append(
            finding(
                "EVENT_ROLE_MISMATCH",
                "occupied_role",
                "event provider and occupied role do not match",
            )
        )

    receipt = event.get("bootstrap_receipt")
    receipt_sha: str | None = None
    resolved_refs: list[dict[str, Any]] = []
    content_by_path: dict[str, bytes] = {}
    if event_class in policy.get("material_event_classes", []) and provider != "Human":
        checked.add("bootstrap_receipt")
        if not isinstance(receipt, dict):
            violations.append(
                finding(
                    "BOOTSTRAP_RECEIPT_REQUIRED",
                    "bootstrap_receipt",
                    "C1/C2 model event requires a bootstrap receipt",
                )
            )
        else:
            receipt_sha = digest_object(receipt)
            receipt_violations, receipt_refs = validate_bootstrap_receipt(
                receipt, repo_root, policy
            )
            violations.extend(receipt_violations)
            resolved_refs.extend(receipt_refs)
            if receipt.get("provider") != provider or receipt.get("occupied_role") != role:
                violations.append(
                    finding(
                        "BOOTSTRAP_EVENT_BINDING_MISMATCH",
                        "bootstrap_receipt",
                        "bootstrap receipt is bound to a different event provider or role",
                    )
                )

    explicit_refs = event.get("required_refs", [])
    if not isinstance(explicit_refs, list):
        violations.append(
            finding("REQUIRED_REFS_INVALID", "required_refs", "required_refs must be a list")
        )
        explicit_refs = []
    seen_ref_paths: set[str] = set()
    explicit_resolved_refs: list[dict[str, Any]] = []
    for reference in explicit_refs:
        resolved, content, ref_violations = resolve_reference(
            repo_root, reference, test_mode=test_mode
        )
        path = resolved.get("path", "")
        if path in seen_ref_paths:
            violations.append(
                finding(
                    "REQUIRED_REF_DUPLICATE",
                    "required_refs",
                    "required reference paths must be unique",
                )
            )
        seen_ref_paths.add(path)
        resolved_refs.append(resolved)
        explicit_resolved_refs.append(resolved)
        violations.extend(ref_violations)
        if content is not None and resolved.get("status") == "resolved":
            content_by_path[path] = content
    all_explicit_refs_resolved = bool(explicit_refs) and all(
        item.get("status") == "resolved" for item in explicit_resolved_refs
    )
    if event_class in policy.get("material_event_classes", []) and not explicit_refs:
        violations.append(
            finding(
                "REQUIRED_REFS_MISSING",
                "required_refs",
                "C1/C2 durable artifact requires at least one immutable reference",
            )
        )
        all_explicit_refs_resolved = False

    if event_class in policy.get("material_event_classes", []):
        checked.update(
            {
                "pointer_purity",
                "human_operational_completeness",
                "human_response_preflight",
                "independent_expression_boundary",
                "required_ref_resolution",
            }
        )
        communication = event.get("communication")
        if not isinstance(communication, dict):
            violations.append(
                finding(
                    "COMMUNICATION_CONTRACT_REQUIRED",
                    "communication",
                    "C1/C2 event requires a communication contract",
                )
            )
            communication = {}
        allowed_communication_keys = {
            "recipient_mode",
            "channels_separated",
            "human_pointer_only_waiver",
            "human_operational",
            "brief_artifact_ref",
        }
        if set(communication) - allowed_communication_keys:
            violations.append(
                finding(
                    "COMMUNICATION_FIELDS_INVALID",
                    "communication",
                    "communication contract contains unsupported fields",
                )
            )
        recipient_mode = communication.get("recipient_mode")
        if recipient_mode not in {
            "human_only",
            "machine_only",
            "mixed_separable",
            "mixed_nonseparable",
        }:
            violations.append(
                finding(
                    "RECIPIENT_MODE_INVALID",
                    "communication.recipient_mode",
                    "recipient mode is not recognized",
                )
            )
        pointer_applicable = recipient_mode != "human_only"
        pointer = event.get("pointer")
        pointer_present = isinstance(pointer, dict)
        expected_wire = role_config.get("wire_schema") if role_config else None
        if pointer_applicable:
            violations.extend(
                validate_pointer(
                    pointer,
                    expected_wire,
                    policy,
                    proposed_transition=event.get("proposed_transition"),
                )
            )
        elif pointer is not None:
            violations.append(
                finding(
                    "POINTER_NOT_APPLICABLE",
                    "pointer",
                    "human-only event must not manufacture a machine pointer",
                )
            )

        dispatch = event_type in policy.get("dispatch_event_types", [])
        waiver = communication.get("human_pointer_only_waiver") is True
        direct_human = communication.get("human_operational")
        brief_ref = communication.get("brief_artifact_ref")
        brief_path = brief_ref.get("path") if isinstance(brief_ref, dict) else None
        durable_human: dict[str, Any] | None = None
        if brief_path in content_by_path:
            durable_human, brief_violations = parse_human_brief(content_by_path[brief_path])
            violations.extend(brief_violations)

        fallback_required = recipient_mode in {"machine_only", "mixed_nonseparable"} or (
            recipient_mode == "mixed_separable" and waiver and direct_human is None
        )
        if recipient_mode == "mixed_separable" and communication.get("channels_separated") is not True:
            violations.append(
                finding(
                    "MIXED_CHANNEL_SEPARATION_MISSING",
                    "communication.channels_separated",
                    "separable mixed output must keep pointer and Human content structurally separate",
                )
            )
        if recipient_mode == "mixed_nonseparable" and direct_human is not None:
            violations.append(
                finding(
                    "NONSEPARABLE_DIRECT_HUMAN_CONTENT",
                    "communication.human_operational",
                    "non-separable interface direct output must remain pointer-only",
                )
            )
        if fallback_required:
            checked.add("durable_brief_fallback")
            pointer_data = pointer.get("data", {}) if isinstance(pointer, dict) else {}
            pointer_brief_ref = pointer_data.get("brief_ref") if isinstance(pointer_data, dict) else None
            if not isinstance(brief_ref, dict) or durable_human is None:
                violations.append(
                    finding(
                        "DURABLE_BRIEF_FALLBACK_UNRESOLVED",
                        "communication.brief_artifact_ref",
                        "pointer-only fallback requires a resolvable complete Human Brief",
                    )
                )
            if pointer_brief_ref is None or pointer_brief_ref != brief_path:
                violations.append(
                    finding(
                        "POINTER_BRIEF_REF_MISMATCH",
                        "pointer.data.brief_ref",
                        "pointer brief_ref must identify the exact durable fallback artifact",
                    )
                )
            selected_human = durable_human
            selected_path = "durable_brief"
        else:
            selected_human = direct_human
            selected_path = "communication.human_operational"
        human_violations, human_warnings = validate_human_content(
            selected_human,
            policy,
            explicit_resolved_refs,
            dispatch=dispatch,
            pointer_present=pointer_present,
            pointer_applicable=pointer_applicable,
            all_refs_resolved=all_explicit_refs_resolved,
            path=selected_path,
        )
        violations.extend(human_violations)
        warnings.extend(human_warnings)

    proposed_transition = event.get("proposed_transition")
    if proposed_transition is not None and event_class != "C0":
        checked.add("proposed_transition_shape")
        if not isinstance(proposed_transition, dict):
            violations.append(
                finding(
                    "PROPOSED_TRANSITION_INVALID",
                    "proposed_transition",
                    "proposed transition must be a mapping",
                )
            )
        else:
            transition_id = proposed_transition.get("transition_id")
            transition_policy = policy["transitions"].get(transition_id)
            if transition_policy is None:
                violations.append(
                    finding(
                        "TRANSITION_ID_UNKNOWN",
                        "proposed_transition.transition_id",
                        "transition identifier is not defined by policy",
                    )
                )
            elif event_type not in transition_policy["event_types"]:
                violations.append(
                    finding(
                        "TRANSITION_EVENT_TYPE_MISMATCH",
                        "proposed_transition",
                        "event type does not match the proposed transition policy",
                    )
                )

    result = _make_result(
        policy=policy,
        policy_sha=policy_sha,
        event_id=nullable_string(event.get("event_id")),
        task_id=nullable_string(event.get("task_id")),
        event_type=event_type if isinstance(event_type, str) else None,
        role=role if isinstance(role, str) else None,
        event_class=event_class,
        input_sha=input_sha,
        receipt_sha=receipt_sha,
        checked_contracts=checked,
        resolved_refs=resolved_refs,
        violations=violations,
        warnings=warnings,
        proposed_transition=proposed_transition if isinstance(proposed_transition, dict) else None,
    )
    ensure_result_schema(result)
    return result


def _apply_mutations(value: Any, mutations: dict[str, Any]) -> Any:
    target = copy.deepcopy(value)
    for dotted_path, replacement in mutations.items():
        parts = dotted_path.split(".")
        current = target
        for part in parts[:-1]:
            current = current[int(part)] if isinstance(current, list) else current[part]
        last = parts[-1]
        if replacement == "__DELETE__":
            if isinstance(current, list):
                del current[int(last)]
            else:
                current.pop(last, None)
        elif isinstance(current, list):
            current[int(last)] = replacement
        else:
            current[last] = replacement
    return target


def check_transition(
    request: Any,
    validation_result: Any,
    repo_root: Path,
    policy: dict[str, Any],
    policy_sha: str,
    *,
    authority_context: Any = None,
    authority_mode: str = "none",
    test_mode: bool = False,
    consumed_context_ids: set[str] | None = None,
    trusted_authority_verifier: Callable[[dict[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    del repo_root
    violations: list[dict[str, str]] = []
    checked = {"transition_policy", "validation_result_binding", "external_authority_boundary"}
    request_sha = digest_object(request)
    if validation_result is None:
        violations.append(
            finding(
                "VALIDATION_RESULT_MISSING",
                "validation_result",
                "transition is ineligible without a machine-readable validation result",
            )
        )
        if not isinstance(request, dict):
            request = {}
        result = _make_result(
            policy=policy,
            policy_sha=policy_sha,
            event_id=nullable_string(request.get("event_id")),
            task_id=nullable_string(request.get("task_id")),
            event_type=nullable_string(request.get("event_type")),
            role=None,
            event_class=normalized_event_class(request.get("event_class")),
            input_sha=request_sha,
            receipt_sha=None,
            checked_contracts=checked,
            resolved_refs=[],
            violations=violations,
            warnings=[],
            proposed_transition={
                "transition_id": request.get("transition_id"),
                "from_state": request.get("from_state"),
                "to_state": request.get("to_state"),
            },
        )
        ensure_result_schema(result)
        return result
    _validate_schema_to(
        request, "transition_request.schema.json", "TRANSITION_REQUEST", violations
    )
    _validate_schema_to(
        validation_result,
        "communication_validation.schema.json",
        "VALIDATION_RESULT",
        violations,
    )
    if not isinstance(request, dict):
        request = {}
    if not isinstance(validation_result, dict):
        validation_result = {}
    validated_refs_value = validation_result.get("resolved_refs")
    validated_refs = (
        validated_refs_value
        if isinstance(validated_refs_value, list)
        and all(isinstance(item, dict) for item in validated_refs_value)
        else []
    )
    validation_sha = digest_object(validation_result)
    if request.get("validation_result_sha256") != validation_sha:
        violations.append(
            finding(
                "VALIDATION_RESULT_DIGEST_MISMATCH",
                "validation_result_sha256",
                "transition request is not bound to the supplied validation result",
            )
        )
    if validation_result.get("result") != "pass":
        violations.append(
            finding(
                "VALIDATION_RESULT_NOT_PASS",
                "validation_result.result",
                "transition requires a passing communication validation result",
            )
        )
    if validation_result.get("result") == "pass" and validation_result.get("violations"):
        violations.append(
            finding(
                "VALIDATION_RESULT_INCONSISTENT",
                "validation_result.violations",
                "a passing validation result cannot contain violations",
            )
        )
    if (
        validation_result.get("validator_version") != VALIDATOR_VERSION
        or validation_result.get("policy_sha256") != policy_sha
    ):
        violations.append(
            finding(
                "VALIDATION_POLICY_BINDING_MISMATCH",
                "validation_result.policy_sha256",
                "validation result is not bound to the active validator and policy",
            )
        )
    if validation_result.get("protocol_head") != policy["protocol_head"] or request.get(
        "protocol_head"
    ) != policy["protocol_head"]:
        violations.append(
            finding(
                "TRANSITION_PROTOCOL_HEAD_STALE",
                "protocol_head",
                "transition and validation must match the active policy protocol head",
            )
        )
    bindings = {
        "event_id": validation_result.get("event_id"),
        "task_id": validation_result.get("task_id"),
        "event_type": validation_result.get("event_type"),
        "event_class": validation_result.get("event_class"),
        "event_input_sha256": validation_result.get("input_sha256"),
    }
    for key, expected in bindings.items():
        if request.get(key) != expected:
            violations.append(
                finding(
                    "TRANSITION_VALIDATION_BINDING_MISMATCH",
                    key,
                    "transition request does not match its validation result",
                )
            )
    if any(item.get("status") != "resolved" for item in validated_refs):
        violations.append(
            finding(
                "TRANSITION_REF_UNRESOLVED",
                "validation_result.resolved_refs",
                "transition validation contains an unresolved required reference",
            )
        )
    transition_id_value = request.get("transition_id")
    transition_id = transition_id_value if isinstance(transition_id_value, str) else None
    transition_policy = policy["transitions"].get(transition_id)
    if transition_policy is None:
        violations.append(
            finding(
                "TRANSITION_ID_UNKNOWN",
                "transition_id",
                "transition identifier is not defined by policy",
            )
        )
    else:
        if request.get("from_state") not in transition_policy["from_states"]:
            violations.append(
                finding(
                    "TRANSITION_FROM_STATE_UNSUPPORTED",
                    "from_state",
                    "from-state is not eligible for this transition",
                )
            )
        if request.get("to_state") != transition_policy.get("to_state"):
            violations.append(
                finding(
                    "TRANSITION_TO_STATE_MISMATCH",
                    "to_state",
                    "to-state differs from the machine-readable transition policy",
                )
            )
        if request.get("event_type") not in transition_policy["event_types"]:
            violations.append(
                finding(
                    "TRANSITION_EVENT_TYPE_MISMATCH",
                    "event_type",
                    "event type is not allowed for this transition",
                )
            )
        if request.get("event_class") != transition_policy["required_event_class"]:
            violations.append(
                finding(
                    "TRANSITION_EVENT_CLASS_MISMATCH",
                    "event_class",
                    "event class is below or different from the transition policy requirement",
                )
            )
        proposed = validation_result.get("proposed_transition")
        expected_proposed = {
            "transition_id": transition_id,
            "from_state": request.get("from_state"),
            "to_state": request.get("to_state"),
        }
        if proposed != expected_proposed:
            violations.append(
                finding(
                    "PROPOSED_TRANSITION_BINDING_MISMATCH",
                    "validation_result.proposed_transition",
                    "validated event proposed a different transition",
                )
            )

        if transition_policy.get("external_human_authority_required"):
            if authority_context is None:
                violations.append(
                    finding(
                        "AUTHENTICATED_HUMAN_AUTHORITY_UNAVAILABLE",
                        "authorization_context",
                        "C2 transition requires a separately injected Human authority context",
                    )
                )
            else:
                _validate_schema_to(
                    authority_context,
                    "authorization_context.schema.json",
                    "AUTHORIZATION_CONTEXT",
                    violations,
                )
                if isinstance(authority_context, dict):
                    if authority_mode == "test-fixture":
                        trusted = (
                            test_mode
                            and authority_context.get("injection_source")
                            == "deterministic_test_fixture"
                            and authority_context.get("test_only") is True
                        )
                    elif authority_mode == "trusted-host":
                        trusted_shape = (
                            authority_context.get("injection_source")
                            == "trusted_external_host"
                            and authority_context.get("test_only") is False
                        )
                        trusted = False
                        if trusted_shape and trusted_authority_verifier is not None:
                            try:
                                trusted = bool(
                                    trusted_authority_verifier(copy.deepcopy(authority_context))
                                )
                            except Exception:
                                trusted = False
                    else:
                        trusted = False
                    if not trusted:
                        violations.append(
                            finding(
                                "AUTHORITY_CONTEXT_TRUST_BOUNDARY_INVALID",
                                "authorization_context.injection_source",
                                "authority context was not injected through the declared trusted boundary",
                            )
                        )
                    target = request.get("to_state") or transition_id
                    authority_bindings = {
                        "task_id": request.get("task_id"),
                        "event_id": request.get("event_id"),
                        "transition_id": transition_id,
                        "action": request.get("event_type"),
                        "target": target,
                        "protocol_head": policy["protocol_head"],
                    }
                    for key, expected in authority_bindings.items():
                        if authority_context.get(key) != expected:
                            violations.append(
                                finding(
                                    "AUTHORITY_CONTEXT_BINDING_MISMATCH",
                                    f"authorization_context.{key}",
                                    "authority context is bound to a different protected action",
                                )
                            )
                    if authority_context.get("context_id") in (consumed_context_ids or set()):
                        violations.append(
                            finding(
                                "AUTHORITY_CONTEXT_REPLAYED",
                                "authorization_context.context_id",
                                "authority context identifier is already consumed",
                            )
                        )

    result = _make_result(
        policy=policy,
        policy_sha=policy_sha,
        event_id=nullable_string(request.get("event_id")),
        task_id=nullable_string(request.get("task_id")),
        event_type=nullable_string(request.get("event_type")),
        role=nullable_string(validation_result.get("role")),
        event_class=normalized_event_class(request.get("event_class")),
        input_sha=request_sha,
        receipt_sha=nullable_sha256(validation_result.get("bootstrap_receipt_sha256")),
        checked_contracts=checked,
        resolved_refs=validated_refs,
        violations=violations,
        warnings=[],
        proposed_transition={
            "transition_id": transition_id,
            "from_state": request.get("from_state"),
            "to_state": request.get("to_state"),
        },
        transition_eligible=not violations,
    )
    ensure_result_schema(result)
    return result


def validate_drift_record(
    record: Any,
    repo_root: Path,
    policy: dict[str, Any],
    policy_sha: str,
) -> dict[str, Any]:
    violations: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    _validate_schema_to(record, "drift_record.schema.json", "DRIFT_RECORD", violations)
    if not isinstance(record, dict):
        record = {}
    occurrence = record.get("occurrence_count")
    if isinstance(occurrence, int) and occurrence >= policy["drift_policy"][
        "recurrence_threshold"
    ]:
        fixture_ref = record.get("regression_fixture_ref")
        if isinstance(fixture_ref, str):
            path_text, separator, case_id = fixture_ref.partition("#")
            safe = safe_repo_path(path_text)
            if not separator or safe is None or not case_id:
                violations.append(
                    finding(
                        "DRIFT_FIXTURE_REF_INVALID",
                        "regression_fixture_ref",
                        "recurring drift fixture ref must use safe-path#case-id",
                    )
                )
            else:
                suite_path = repo_root.joinpath(*PurePosixPath(safe).parts)
                try:
                    suite = load_document(suite_path)
                    cases = suite.get("cases", []) if isinstance(suite, dict) else []
                    matching = [case for case in cases if case.get("id") == case_id]
                    codes = (
                        matching[0].get("expected_violation_codes", []) if len(matching) == 1 else []
                    )
                    if record.get("violation_class") not in codes:
                        raise InputDocumentError("fixture class mismatch")
                except (InputDocumentError, OSError):
                    violations.append(
                        finding(
                            "DRIFT_FIXTURE_UNRESOLVED",
                            "regression_fixture_ref",
                            "recurring drift fixture does not resolve to a matching negative case",
                        )
                    )
        elif record.get("deterministic_fixture_impossible_reason"):
            review_ref = record.get("foreground_review_ref")
            resolved, _content, ref_violations = resolve_reference(
                repo_root, review_ref, test_mode=False
            )
            if ref_violations or resolved.get("status") != "resolved":
                violations.append(
                    finding(
                        "DRIFT_FOREGROUND_REVIEW_UNRESOLVED",
                        "foreground_review_ref",
                        "deterministic-impossibility exception requires resolved foreground review evidence",
                    )
                )
            else:
                warnings.append(
                    finding(
                        "DRIFT_DETERMINISTIC_FIXTURE_EXCEPTION",
                        "deterministic_fixture_impossible_reason",
                        "recurring drift requires foreground semantic review",
                        "warning",
                    )
                )
        else:
            violations.append(
                finding(
                    "DRIFT_RECURRENCE_FIXTURE_REQUIRED",
                    "regression_fixture_ref",
                    "second occurrence requires a matching regression fixture or reviewed exception",
                )
            )
    result = _make_result(
        policy=policy,
        policy_sha=policy_sha,
        event_id=nullable_string(record.get("record_id")),
        task_id=None,
        event_type="drift_record",
        role=None,
        event_class="C1",
        input_sha=digest_object(record),
        receipt_sha=None,
        checked_contracts={"drift_record_schema", "drift_recurrence_policy"},
        resolved_refs=[],
        violations=violations,
        warnings=warnings,
    )
    ensure_result_schema(result)
    return result


def bootstrap_result(
    receipt: Any,
    repo_root: Path,
    policy: dict[str, Any],
    policy_sha: str,
) -> dict[str, Any]:
    violations, resolved = validate_bootstrap_receipt(receipt, repo_root, policy)
    role = nullable_string(receipt.get("occupied_role")) if isinstance(receipt, dict) else None
    result = _make_result(
        policy=policy,
        policy_sha=policy_sha,
        event_id=(nullable_string(receipt.get("receipt_id")) if isinstance(receipt, dict) else None),
        task_id=None,
        event_type="bootstrap_receipt",
        role=role,
        event_class="C1",
        input_sha=digest_object(receipt),
        receipt_sha=digest_object(receipt) if isinstance(receipt, dict) else None,
        checked_contracts={"bootstrap_receipt", "provider_role_mapping", "loaded_file_binding"},
        resolved_refs=resolved,
        violations=violations,
        warnings=[],
    )
    ensure_result_schema(result)
    return result


def error_result(code: str, message: str, *, error_class: str = "input") -> dict[str, Any]:
    del error_class
    policy = {
        "protocol_head": ZERO_SHA1,
    }
    return _make_result(
        policy=policy,
        policy_sha=ZERO_SHA256,
        event_id=None,
        task_id=None,
        event_type=None,
        role=None,
        event_class="unknown",
        input_sha=ZERO_SHA256,
        receipt_sha=None,
        checked_contracts=[],
        resolved_refs=[],
        violations=[finding(code, "", message)],
        warnings=[],
        error=True,
    )


def result_exit_code(result: dict[str, Any]) -> int:
    if result.get("result") == "pass":
        return EXIT_PASS
    if result.get("result") == "fail":
        return EXIT_COMPLIANCE_FAIL
    return EXIT_INPUT


def _auto_authority_context(
    context: Any, request: dict[str, Any], policy: dict[str, Any]
) -> Any:
    if not isinstance(context, dict):
        return context
    result = copy.deepcopy(context)
    replacements = {
        "AUTO_TASK_ID": request.get("task_id"),
        "AUTO_EVENT_ID": request.get("event_id"),
        "AUTO_TRANSITION_ID": request.get("transition_id"),
        "AUTO_ACTION": request.get("event_type"),
        "AUTO_TARGET": request.get("to_state") or request.get("transition_id"),
        "AUTO_PROTOCOL_HEAD": policy["protocol_head"],
    }
    for key, value in list(result.items()):
        if value in replacements:
            result[key] = replacements[value]
    return result


def run_fixture_suite(
    suite: Any,
    repo_root: Path,
    policy: dict[str, Any],
    policy_sha: str,
) -> tuple[dict[str, Any], int]:
    if not isinstance(suite, dict) or suite.get("schema_version") != "human_ai.communication_fixture_suite.v1":
        raise InputDocumentError("fixture suite contract is invalid")
    cases = suite.get("cases")
    if not isinstance(cases, list):
        raise InputDocumentError("fixture suite cases must be a list")
    seen: set[str] = set()
    event_results: dict[str, dict[str, Any]] = {}
    case_outcomes: list[dict[str, Any]] = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise InputDocumentError("fixture case is malformed")
        case_id = case["id"]
        if case_id in seen:
            raise InputDocumentError("fixture case identifiers must be unique")
        seen.add(case_id)
        operation = case.get("operation")
        actual_exit = EXIT_INTERNAL
        try:
            if operation == "validate_event":
                actual = validate_event(
                    case.get("payload"), repo_root, policy, policy_sha, test_mode=True
                )
                event_results[case_id] = actual
                actual_exit = result_exit_code(actual)
            elif operation == "validate_bootstrap":
                actual = bootstrap_result(case.get("payload"), repo_root, policy, policy_sha)
                actual_exit = result_exit_code(actual)
            elif operation == "validate_drift":
                actual = validate_drift_record(
                    case.get("payload"), repo_root, policy, policy_sha
                )
                actual_exit = result_exit_code(actual)
            elif operation == "classify":
                class_name, class_violations = classify_event(case.get("event_type"), policy)
                actual = _make_result(
                    policy=policy,
                    policy_sha=policy_sha,
                    event_id=case_id,
                    task_id=None,
                    event_type=case.get("event_type"),
                    role=None,
                    event_class=class_name,
                    input_sha=digest_object(case.get("event_type")),
                    receipt_sha=None,
                    checked_contracts={"material_event_classifier"},
                    resolved_refs=[],
                    violations=class_violations,
                    warnings=[],
                )
                actual_exit = result_exit_code(actual)
            elif operation == "parse_document":
                input_ref = safe_repo_path(case.get("input_ref"))
                if input_ref is None:
                    raise InputDocumentError("fixture parse ref is unsafe")
                try:
                    load_document(repo_root.joinpath(*PurePosixPath(input_ref).parts))
                    actual = _make_result(
                        policy=policy,
                        policy_sha=policy_sha,
                        event_id=case_id,
                        task_id=None,
                        event_type="parse_document",
                        role=None,
                        event_class="C1",
                        input_sha=ZERO_SHA256,
                        receipt_sha=None,
                        checked_contracts={"strict_document_parser"},
                        resolved_refs=[],
                        violations=[],
                        warnings=[],
                    )
                    actual_exit = EXIT_PASS
                except InputDocumentError:
                    actual = error_result(
                        "INPUT_DOCUMENT_REJECTED",
                        "strict parser rejected an unsafe document",
                    )
                    actual_exit = EXIT_INPUT
            elif operation == "transition":
                source_id = case.get("event_case_id")
                base_result = event_results.get(source_id) if source_id else None
                if base_result is not None:
                    validation_result = _apply_mutations(
                        base_result, case.get("validation_result_mutations", {})
                    )
                else:
                    validation_result = None
                request = copy.deepcopy(case.get("request", {}))
                if validation_result is not None:
                    auto_values = {
                        "AUTO_EVENT_ID": validation_result.get("event_id"),
                        "AUTO_TASK_ID": validation_result.get("task_id"),
                        "AUTO_EVENT_TYPE": validation_result.get("event_type"),
                        "AUTO_EVENT_CLASS": validation_result.get("event_class"),
                        "AUTO_EVENT_INPUT_SHA256": validation_result.get("input_sha256"),
                        "AUTO_VALIDATION_SHA256": digest_object(validation_result),
                        "AUTO_PROTOCOL_HEAD": policy["protocol_head"],
                    }
                    for key, value in list(request.items()):
                        if value in auto_values:
                            request[key] = auto_values[value]
                request = _apply_mutations(request, case.get("request_mutations", {}))
                authority = _auto_authority_context(
                    case.get("authorization_context"), request, policy
                )
                actual = check_transition(
                    request,
                    validation_result,
                    repo_root,
                    policy,
                    policy_sha,
                    authority_context=authority,
                    authority_mode=case.get("authority_mode", "none"),
                    test_mode=True,
                    consumed_context_ids=set(case.get("consumed_context_ids", [])),
                    trusted_authority_verifier=(
                        (lambda _context: True)
                        if case.get("trusted_host_verifier_result") is True
                        else None
                    ),
                )
                actual_exit = result_exit_code(actual)
            else:
                raise InputDocumentError("fixture operation is not supported")
        except InputDocumentError:
            actual = error_result("INPUT_DOCUMENT_REJECTED", "fixture input was rejected")
            actual_exit = EXIT_INPUT
        actual_codes = sorted({item["code"] for item in actual.get("violations", [])})
        expected_codes = sorted(set(case.get("expected_violation_codes", [])))
        expected_result = case.get("expected_result")
        expected_exit = case.get("expected_exit_code")
        matched = (
            actual.get("result") == expected_result
            and actual_exit == expected_exit
            and actual_codes == expected_codes
        )
        case_outcomes.append(
            {
                "id": case_id,
                "operation": operation,
                "expected_result": expected_result,
                "actual_result": actual.get("result"),
                "expected_exit_code": expected_exit,
                "actual_exit_code": actual_exit,
                "expected_violation_codes": expected_codes,
                "actual_violation_codes": actual_codes,
                "matched": matched,
            }
        )
    mismatches = [item for item in case_outcomes if not item["matched"]]
    summary = {
        "schema_version": "human_ai.communication_fixture_result.v1",
        "result": "pass" if not mismatches else "fail",
        "validator_version": VALIDATOR_VERSION,
        "protocol_head": policy["protocol_head"],
        "total_cases": len(case_outcomes),
        "matched_cases": len(case_outcomes) - len(mismatches),
        "mismatch_count": len(mismatches),
        "cases": sorted(case_outcomes, key=lambda item: item["id"]),
    }
    return summary, EXIT_PASS if not mismatches else EXIT_COMPLIANCE_FAIL


def _read_consumed_ids(path: Path | None) -> set[str]:
    if path is None:
        return set()
    value = load_document(path)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise InputDocumentError("consumed context identifiers must be a string list")
    return set(value)


def build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(prog="validate_communication.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--repo-root", type=Path, default=Path.cwd())
        subparser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
        subparser.add_argument("--output", type=Path)

    validate = subparsers.add_parser("validate")
    common(validate)
    validate.add_argument("--input", required=True, type=Path)
    validate.add_argument("--test-mode", action="store_true")

    bootstrap = subparsers.add_parser("validate-bootstrap")
    common(bootstrap)
    bootstrap.add_argument("--input", required=True, type=Path)

    classify = subparsers.add_parser("classify")
    common(classify)
    classify.add_argument("--event-type", required=True)

    transition = subparsers.add_parser("transition")
    common(transition)
    transition.add_argument("--input", required=True, type=Path)
    transition.add_argument("--validation-result", required=True, type=Path)
    transition.add_argument("--authorization-context", type=Path)
    transition.add_argument(
        "--authority-mode",
        choices=["none", "trusted-host", "test-fixture"],
        default="none",
    )
    transition.add_argument("--test-mode", action="store_true")
    transition.add_argument("--consumed-context-ids", type=Path)

    drift = subparsers.add_parser("validate-drift")
    common(drift)
    drift.add_argument("--input", required=True, type=Path)

    fixtures = subparsers.add_parser("run-fixtures")
    common(fixtures)
    fixtures.add_argument("--suite", type=Path, default=DEFAULT_FIXTURE_SUITE)
    return parser


def _write_output(payload: Any, output: Path | None) -> None:
    serialized = serialize_json(payload)
    if output is not None:
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(serialized, encoding="utf-8", newline="\n")
        except OSError as exc:
            raise InputDocumentError("output file cannot be written") from exc
    sys.stdout.write(serialized)


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        repo_root = args.repo_root.resolve(strict=True)
        policy_path = args.policy
        if not policy_path.is_absolute():
            policy_path = repo_root / policy_path
        policy, policy_sha = load_policy(policy_path)
        if args.command == "validate":
            payload = load_document(args.input)
            result = validate_event(
                payload, repo_root, policy, policy_sha, test_mode=args.test_mode
            )
            exit_code = result_exit_code(result)
        elif args.command == "validate-bootstrap":
            result = bootstrap_result(load_document(args.input), repo_root, policy, policy_sha)
            exit_code = result_exit_code(result)
        elif args.command == "classify":
            class_name, violations = classify_event(args.event_type, policy)
            result = _make_result(
                policy=policy,
                policy_sha=policy_sha,
                event_id=None,
                task_id=None,
                event_type=args.event_type,
                role=None,
                event_class=class_name,
                input_sha=digest_object(args.event_type),
                receipt_sha=None,
                checked_contracts={"material_event_classifier"},
                resolved_refs=[],
                violations=violations,
                warnings=[],
            )
            ensure_result_schema(result)
            exit_code = result_exit_code(result)
        elif args.command == "transition":
            authority = (
                load_document(args.authorization_context)
                if args.authorization_context is not None
                else None
            )
            result = check_transition(
                load_document(args.input),
                load_document(args.validation_result),
                repo_root,
                policy,
                policy_sha,
                authority_context=authority,
                authority_mode=args.authority_mode,
                test_mode=args.test_mode,
                consumed_context_ids=_read_consumed_ids(args.consumed_context_ids),
            )
            exit_code = result_exit_code(result)
        elif args.command == "validate-drift":
            result = validate_drift_record(
                load_document(args.input), repo_root, policy, policy_sha
            )
            exit_code = result_exit_code(result)
        elif args.command == "run-fixtures":
            result, exit_code = run_fixture_suite(
                load_document(args.suite), repo_root, policy, policy_sha
            )
        else:  # pragma: no cover - argparse guarantees command
            raise InvocationError("unknown command")
        _write_output(result, args.output)
        return exit_code
    except InvocationError:
        _write_output(
            error_result("CLI_INVOCATION_INVALID", "invalid command-line invocation"),
            None,
        )
        return EXIT_INVOCATION
    except InputDocumentError:
        _write_output(
            error_result("INPUT_DOCUMENT_INVALID", "input document could not be processed"),
            None,
        )
        return EXIT_INPUT
    except ConfigurationError:
        _write_output(
            error_result("GATE_CONFIGURATION_INVALID", "gate configuration is unavailable or invalid"),
            None,
        )
        return EXIT_CONFIG
    except Exception:
        _write_output(
            error_result("GATE_INTERNAL_ERROR", "unexpected internal gate failure"),
            None,
        )
        return EXIT_INTERNAL


if __name__ == "__main__":
    raise SystemExit(main())
