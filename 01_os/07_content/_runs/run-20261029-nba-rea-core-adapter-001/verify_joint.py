"""Reproduce the static Core/NBA integration with a caller-selected non-game binary."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess


DOMAIN = Path("08_Domain_Applications/Antigravity_GM_Engine")


def head(root):
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", type=Path, required=True)
    parser.add_argument("--nba-root", type=Path, required=True)
    parser.add_argument("--core-head", required=True)
    parser.add_argument("--nba-head", required=True)
    parser.add_argument("--fixture-binary", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    if head(args.core_root) != args.core_head or head(args.nba_root) != args.nba_head:
        raise RuntimeError("Checkout heads differ from the selected verification inputs")
    bridge_path = args.nba_root / DOMAIN / "research/rea_core_profile/bridge.py"
    spec = importlib.util.spec_from_file_location("nba_profile_for_joint_check", bridge_path)
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    profile = json.loads(bridge.PROFILE.read_bytes())
    core_path = profile["core"]["adapter_path"]
    pinned = bridge.git_blob(args.core_root, profile["core"]["commit"], core_path)
    if pinned != bridge.git_blob(args.core_root, args.core_head, core_path):
        raise RuntimeError("Core candidate differs from the adapter pinned by the NBA Profile")
    domain_catalog = bridge.load_catalog(args.nba_root, profile)
    for name in ("TRADE_EXECUTE_AGREED_PACKAGE", "COACH_SET_KNOWN_CURRENT_SETTINGS", "SCOUT_SET_EXISTING_GOAL_TARGETS"):
        row = domain_catalog["actions"][name]
        if row["evidence_level"] != "LiveEffectVerified" or row["current_execution"] != "NOT_RUN":
            raise RuntimeError("Historical effect must remain bound to its original example")
    with args.fixture_binary.open("rb") as stream:
        fixture_sha = hashlib.file_digest(stream, "sha256").hexdigest()
    if fixture_sha == profile["target"]["sha256"]:
        raise RuntimeError("Select a non-game fixture")
    args.evidence_dir.mkdir()
    mismatched, code = bridge.call_core(args.core_root, profile, args.evidence_dir / "wrong-target", "invoke", args.fixture_binary)
    if code == 0 or mismatched.get("status") != "SOURCE_MISMATCH":
        raise RuntimeError("Game Profile must reject the non-game binary")
    fixture_profile = copy.deepcopy(profile)
    fixture_profile["target"] = {"mode": "non-game integration fixture", "sha256": fixture_sha}
    static, code = bridge.call_core(args.core_root, fixture_profile, args.evidence_dir / "fixture", "invoke", args.fixture_binary)
    if code != 0 or static["status"] != "DOMAIN_STATIC_RECEIPT_VERIFIED" or static["current_game_effect"] != "NOT_RUN":
        raise RuntimeError("Static integration did not produce a domain-verified receipt")
    result = {
        "status": "PASS_STATIC_CROSS_REPOSITORY",
        "core_head": args.core_head, "nba_head": args.nba_head,
        "adapter_pin": profile["core"]["commit"], "adapter_sha256": hashlib.sha256(pinned).hexdigest(),
        "native_research_pin": profile["native_research"]["commit"],
        "native_executor_candidate": profile["native_executor_candidate"]["commit"],
        "action_count": len(domain_catalog["actions"]),
        "binding_count": domain_catalog["binding_count"], "reader_count": domain_catalog["reader_count"],
        "mismatched_build": mismatched["status"],
        "static_fixture": static, "new_live_game_test": "NOT_RUN",
    }
    (args.evidence_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
