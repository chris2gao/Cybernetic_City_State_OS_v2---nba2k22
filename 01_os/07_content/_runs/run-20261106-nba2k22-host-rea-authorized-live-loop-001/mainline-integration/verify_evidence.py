"""Build or verify the allowlisted, portable S4 mainline evidence."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

BASE = "20ff460792bdf0b44b21f8c8422bc6a2a74a0996"
SOURCE = "27588b82b7ce24cd0a6985abef8161a6afc9351d"
RUN = "01_os/07_content/_runs/run-20261106-nba2k22-host-rea-authorized-live-loop-001"
INTEGRATION = RUN + "/mainline-integration"
ROOT = Path(__file__).resolve().parents[5]
CODE = {"08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/season_cycle_host.py", "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/decision_outbox.py", "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/season_cycle_cli.py", "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/tests/test_season_cycle_host.py", "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/tests/test_decision_outbox.py"}
PORTABLE = {"live-closeout.json": "portable-live-closeout.json", "readonly-preflight.json": "portable-preflight.json"}
SENSITIVE = re.compile(rb'(?<![A-Za-z0-9])[A-Za-z]:[\\/]|\\\\[A-Za-z0-9_.-]+\\|-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}')
FORBIDDEN_NAMES = {"role_authorizations.json", "delegation-proposal.json", "evidence.json", "receipts.jsonl"}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def blob(ref, path):
    return git("show", f"{ref}:{path}")


def changes(left, right):
    return set(filter(None, git("diff", "--name-only", "--no-renames", "-z", left, right).decode().split("\0")))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def projection(name, source):
    data = json.loads(source)
    if name == "readonly-preflight.json":
        return {"historical_preflight": "READ_ONLY", "game_build_sha256": data["build_sha256"],
                "schedule_date": data["schedule_date"], "sqlite_final_count": data["sqlite_final_count"],
                "outbox_intents": data["outbox_intents"], "read_only_elapsed_seconds": data["elapsed_seconds"]}
    host, item, outbox = data["host"], data["execution_journal_item"], data["outbox"]
    return {
        "status": data["status"], "source_execution_commit": data["candidate_commit"],
        "cycle_id": data["cycle_id"], "sealed_plan_sha256": data["plan_digest"],
        "native_plan_sha256": data["native_plan_digest"],
        "approved_target": {k: data["target"][k] for k in ("team_id", "player_id", "field_id", "expected_before", "proposed_value")},
        "execution_exit_code": data["execution_exit_code"],
        "verified_setter_count": data["verified_setter_count"],
        "setter_trace": [{k: row[k] for k in ("binding_id", "stage", "call_number")}
                         for row in data["native_call_stages"] if row["binding_id"] == "player.set_stat_ui"],
        "journal_getter_before": item["getter_before"], "journal_getter_after": item["getter_after"],
        "raw_after": item["raw_after"], "unaltered_fields_check": item["unaltered_fields_check"],
        "fresh_getter_after": host["readback_details"][0]["observed_after"],
        "batch_validation_passed": data["validation"]["validation_passed"],
        "execution_claim_count": outbox["execution_claim_count"],
        "outbox_cycle_status": outbox["cycle_status"], "outbox_item_status": outbox["items"][0]["status"],
        "disk_save_sha256_match": data["disk_save_sha256_before"] == data["disk_save_sha256_after"],
        "host_batch_seconds": host["elapsed_seconds"], "wall_seconds": data["wall_seconds"],
        "private_original_sha256": data["private_original_sha256"],
        "scope": "Verified running memory for this single item; reload persistence and gameplay effects unverified.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    src_paths = changes(BASE, SOURCE)
    assert len(src_paths) == 15 and {p for p in src_paths if not p.startswith(RUN + "/")} == CODE
    generated = {}
    mapping = {}
    for path in sorted(src_paths - CODE):
        name = path.removeprefix(RUN + "/")
        original = blob(SOURCE, path)
        entry = {"source_path": path, "source_sha256": sha(original)}
        if name in PORTABLE:
            relative = INTEGRATION + "/" + PORTABLE[name]
            generated[relative] = encode(projection(name, original))
            entry.update(disposition="portable_projection", portable_path=relative,
                         portable_sha256=sha(generated[relative]))
        else:
            entry.update(disposition="source_only", reason=(
                "Contains inactive delegation proposal details" if name == "delegation-proposal.json"
                else "Retained source documentation, workflow configuration or live preflight runner"
            ))
        mapping[name] = entry
    generated[INTEGRATION + "/source-mapping.json"] = encode({
        "base": BASE, "source": SOURCE, "evidence": mapping,
        "source_code_blobs": {path: git("rev-parse", f"{SOURCE}:{path}").decode().strip() for path in sorted(CODE)},
    })
    if args.prepare:
        for path, data in generated.items():
            (ROOT / path).write_bytes(data)
        return

    head = git("rev-parse", "HEAD").decode().strip()
    candidate_paths = changes(BASE, head)
    assert candidate_paths - CODE == set(generated) | {
        INTEGRATION + "/" + name for name in
        ("INTEGRATION.md", "task-packet.yml", "run.yml", "verification-plan.json", "verify_evidence.py")
    }
    assert changes(SOURCE, head) & CODE == CODE
    for path, data in generated.items():
        assert blob(head, path) == data, path
    for path in candidate_paths:
        assert Path(path).name not in FORBIDDEN_NAMES
        data = blob(head, path)
        assert b"\0" not in data and len(data) < 160_000, path
        # The verifier's own signatures are test patterns and do not contain actual credentials.
        assert path.endswith("/verify_evidence.py") or not SENSITIVE.search(data), path
    git("diff", "--check", BASE, head)
    receipt = projection("live-closeout.json", blob(SOURCE, RUN + "/live-closeout.json"))
    assert receipt["verified_setter_count"] == 1
    assert receipt["journal_getter_before"] == 95 and receipt["fresh_getter_after"] == 96
    assert receipt["batch_validation_passed"] is True and receipt["disk_save_sha256_match"] is True
    assert receipt["outbox_cycle_status"] == "COMPLETED" and receipt["execution_claim_count"] == 1
    print("5 allowed code paths; 10 source evidence hashes; 2 portable projections; privacy and diff checks passed")


if __name__ == "__main__":
    main()
