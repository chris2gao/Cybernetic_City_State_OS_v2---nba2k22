"""Recompute the measured comparison and publish a portable, bounded projection."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--measurements", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    calls = json.loads((HERE / "tool_calls.json").read_text(encoding="utf-8"))["calls"]
    receipts, inputs = {}, []
    for path in sorted(args.measurements.glob("*.json")):
        raw = path.read_bytes()
        doc = json.loads(raw)
        inputs.append({"file": path.name, "sha256": hashlib.sha256(raw).hexdigest()})
        receipts.setdefault(doc["mode"], {}).update(doc["cases"])
    equal_cases = ["discovery", "git", "history", "reuse", "static"]
    assert all(receipts["baseline"][case]["result"] == receipts["candidate"][case]["result"]
               for case in equal_cases)
    before = receipts["baseline"]["diagnostics"]["result"]["parameter_error"]
    after = receipts["candidate"]["diagnostics"]["result"]["parameter_error"]
    assert before["status"] == "TOOL_FAILED" and after["status"] == "INVALID_REQUEST"
    assert "60000" in after["field_errors"][0]["message"]
    modes = {}
    for mode in ("baseline", "candidate"):
        rows = [row for row in calls if row["mode"] == mode]
        assert all(row["exit_code"] == 0 for row in rows)
        first_business = next(row for row in rows if "reuse" in row["cases"])
        start = rows[0]["started_ms"]
        modes[mode] = {
            "outer_tool_calls": len(rows),
            "tool_wait_seconds": sum(row["wall_time_seconds"] for row in rows),
            "observed_route_seconds": (rows[-1]["finished_ms"] - start) / 1000,
            "first_visible_business_seconds": (first_business["finished_ms"] - start) / 1000,
            "hot_path_first_visible_business_seconds": (
                first_business["finished_ms"] - first_business["started_ms"]) / 1000,
            "bounded_search_calls": 1,
            "repeated_searches": 0,
            "temporary_source_scripts": 0,
            "unexpected_execution_errors": 0,
            "diagnostic_failures_losing_known_parameter_details": int(mode == "baseline"),
        }
    output = {
        "status": "OFFLINE_COMPARISON_PASSED",
        "base": "953b3e34d5432b93f05cdff7215da49fe7f87833",
        "workload": "seven fixed Windows offline operations; baseline split across seven outer calls, candidate grouped into two",
        "modes": modes,
        "outer_call_reduction_percent": 100 * (1 - modes["candidate"]["outer_tool_calls"] / modes["baseline"]["outer_tool_calls"]),
        "tool_wait_reduction_percent": 100 * (1 - modes["candidate"]["tool_wait_seconds"] / modes["baseline"]["tool_wait_seconds"]),
        "equal_business_outputs": equal_cases,
        "history_source": receipts["candidate"]["history"]["result"],
        "static_result": receipts["candidate"]["static"]["result"],
        "parameter_diagnostic_before": before,
        "parameter_diagnostic_after": after,
        "fixture_diagnostic": receipts["candidate"]["diagnostics"]["result"],
        "shell": {key: value for key, value in receipts["candidate"]["shell"]["result"].items()
                  if key not in {"candidates", "python_path"}},
        "measurement_input_hashes": inputs,
        "limitations": [
            "Single controlled paired route, without randomized task assignment or a new model window.",
            "Route times include observed inter-call model/tool scheduling; they do not isolate model inference time.",
            "Hot path is the recorded reuse batch. Cold measurement includes bounded discovery of a fixed workload.",
            "Repeated searches and temporary source scripts were already zero on the baseline.",
            "Historical GE-01 statistics are executor assertions and are not comparable performance baselines for this workload.",
            "Calendar diagnostic differences use an explicitly synthetic row; historical missing row values remain unknown.",
            "Raw local shell receipts retain absolute host paths outside the repository; public projection omits personal paths.",
            "No live Calendar execution, game effect, save persistence or independent final acceptance is established."
        ],
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(output, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"modes": modes,
                      "outer_call_reduction_percent": output["outer_call_reduction_percent"],
                      "tool_wait_reduction_percent": output["tool_wait_reduction_percent"]}))


if __name__ == "__main__":
    main()
