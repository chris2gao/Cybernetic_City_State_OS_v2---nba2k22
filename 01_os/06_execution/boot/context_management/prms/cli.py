"""Explicit foreground discovery/loading adapter; no daemon or automatic actions."""
import argparse
import json
from pathlib import Path
import sys

from catalog import discover_g1, discover_g2, compatibility
from source import GitSource, PRMSError
from context import plan_context, human_choice, assemble_context
from domain import scaffold_domain


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["catalog", "domain", "compatibility", "recover-context", "scaffold-domain"])
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--domain-id")
    parser.add_argument("--installed-root")
    parser.add_argument("--installed-commit")
    parser.add_argument("--installed-repository")
    parser.add_argument("--session")
    parser.add_argument("--role")
    parser.add_argument("--task")
    parser.add_argument("--stage")
    parser.add_argument("--action", action="append", default=[])
    parser.add_argument("--required", action="append", default=[])
    parser.add_argument("--optional", action="append", default=[])
    parser.add_argument("--selected", action="append", default=[])
    parser.add_argument("--human-choice-source")
    parser.add_argument("--budget-bytes", type=int, default=100_000)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        if args.command == "scaffold-domain":
            result = scaffold_domain(args.repo_root, args.domain_id, args.repository, args.commit)
        else:
            source = GitSource(args.repo_root, args.commit, args.repository)
        if args.command == "scaffold-domain":
            pass
        elif args.command == "catalog":
            result = discover_g1(source)
        elif args.command == "domain":
            result = discover_g2(source, args.domain_id)
        elif args.command == "compatibility":
            installed = GitSource(args.installed_root, args.installed_commit, args.installed_repository)
            result = compatibility(source, installed)
        else:
            catalog = discover_g1(source)
            plan = plan_context(source, catalog, session_id=args.session, role=args.role,
                                task_id=args.task, stage=args.stage, actions=args.action,
                                required_paths=args.required, optional_paths=args.optional)
            choice = human_choice(plan, session_id=args.session, selected_paths=args.selected,
                                  decision_source=args.human_choice_source)
            result = assemble_context(source, plan, choice, budget_bytes=args.budget_bytes)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": result.get("status", result.get("coverage")),
                          "counts": result.get("counts"), "output": str(output)}, ensure_ascii=False))
        return 2 if result.get("status") == "BLOCKED" else 0
    except (PRMSError, ValueError, TypeError, OSError) as exc:
        print(json.dumps({"status": getattr(exc, "status", "REJECTED"), "detail": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
