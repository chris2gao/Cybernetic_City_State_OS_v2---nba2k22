"""Foreground isolated-state adapter. Never enables a production state service."""
import argparse
import json
from pathlib import Path
import sys

from source import PRMSError
from state import LocalGitState, WriterGate
from memory import build_index, search_memory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init-sandbox", "register", "claim", "append", "checkpoint",
                                            "assign", "refresh-index", "recover", "search"])
    parser.add_argument("--state-root", required=True)
    parser.add_argument("--sandbox-parent")
    parser.add_argument("--isolated-test-only", action="store_true")
    parser.add_argument("--session")
    parser.add_argument("--role")
    parser.add_argument("--operation-id")
    parser.add_argument("--expected-head")
    parser.add_argument("--expected-version", type=int)
    parser.add_argument("--expected-epoch", type=int)
    parser.add_argument("--payload")
    parser.add_argument("--query", default="")
    parser.add_argument("--task")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        if not args.isolated_test_only:
            raise PRMSError("FENCING_NOT_ENFORCEABLE", "this CLI has no production authenticated host ingress")
        root = Path(args.state_root).resolve()
        if any((p / "CORE_MANIFEST.yml").is_file() for p in [root, *root.parents]):
            raise PRMSError("REJECTED", "isolated state must remain outside Core/domain code checkout")
        if args.command == "init-sandbox":
            if not args.sandbox_parent:
                raise PRMSError("REJECTED", "explicit sandbox parent required")
            store = LocalGitState.initialize_isolated(root, sandbox_parent=args.sandbox_parent)
            result = {"status": "ISOLATED_STATE_INITIALIZED", "head": store.head(), "fencing_mode": store.fencing_mode}
        else:
            store = LocalGitState(root)
            protocol = json.loads(store.snapshot().get("protocol.json", b"{}"))
            if protocol.get("scope") != "ISOLATED_TEST_ONLY":
                raise PRMSError("AUTHORITY_UNVERIFIED", "not a marked isolated test repository")
            gate = WriterGate(store)
            if args.command == "recover":
                result = gate.recover(args.role)
                result["status"] = "RECOVERED_ISOLATED_STATE"
            elif args.command == "search":
                head = store.head()
                index = build_index(store.snapshot(head), args.role, head, 1)
                result = search_memory(index, args.query, task_id=args.task)
            else:
                session = gate.open_isolated_session(args.session, [args.role])
                payload = json.loads(Path(args.payload).read_text(encoding="utf-8")) if args.payload else {}
                kinds = {"register": "REGISTER", "claim": "CLAIM", "append": "APPEND", "checkpoint": "CHECKPOINT",
                         "assign": "ASSIGN", "refresh-index": "REFRESH_INDEX"}
                result = gate.apply(session, args.role, operation_id=args.operation_id,
                        expected_head=args.expected_head, expected_version=args.expected_version,
                        expected_epoch=args.expected_epoch, kind=kinds[args.command], payload=payload)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": result.get("status"), "output": str(output)}))
        return 0
    except (PRMSError, ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({"status": getattr(exc, "status", "REJECTED"), "detail": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
