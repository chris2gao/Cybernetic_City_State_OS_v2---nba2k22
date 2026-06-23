import glob
import json
import os
import subprocess
import sys
import time


RESULT_PREFIX = "EVALUATOR_RESULT_JSON:"
STATUSES = ("passed", "failed", "review_required", "skipped", "warning")
SKIP_FILENAMES = {"schema.yaml", "topology_compactness.yaml", "topology_transformers.yaml"}


def parse_evaluator_result(stdout, returncode):
    for line in reversed(stdout.splitlines()):
        if line.startswith(RESULT_PREFIX):
            try:
                result = json.loads(line[len(RESULT_PREFIX):])
            except json.JSONDecodeError as error:
                return {
                    "status": "failed",
                    "message": f"Invalid evaluator result JSON: {error}",
                    "warnings": ["unparseable_evaluator_result"],
                }
            if result.get("status") not in STATUSES:
                return {
                    "status": "failed",
                    "message": f"Unknown evaluator status: {result.get('status')}",
                    "warnings": ["unknown_evaluator_status"],
                }
            result.setdefault("warnings", [])
            return result

    return {
        "status": "warning" if returncode == 0 else "failed",
        "message": "Evaluator emitted no structured status marker.",
        "warnings": ["unstructured_evaluator_output"],
    }


def run_bulk_evaluation(db_dir=None):
    if db_dir is None:
        db_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "08_Domain_Applications",
            "Math_Mentor",
            "Pure_Math_Intuition_DB",
        )

    yaml_files = sorted(glob.glob(os.path.join(db_dir, "*.yaml")))
    evaluated_files = [
        file_path
        for file_path in yaml_files
        if os.path.basename(file_path) not in SKIP_FILENAMES
    ]

    print("=== Bulk Executable Sanity Evaluator ===")
    print(f"Found {len(yaml_files)} YAML files; evaluating {len(evaluated_files)} nodes.\n")

    status_counts = {status: 0 for status in STATUSES}
    warning_count = 0
    findings = []
    start_time = time.time()
    evaluator_path = os.path.join(os.path.dirname(__file__), "sandbox_evaluator.py")

    for file_path in evaluated_files:
        filename = os.path.basename(file_path)
        print(f"[*] Testing Node: {filename} ", end="", flush=True)
        process = subprocess.run(
            [sys.executable, evaluator_path, file_path],
            capture_output=True,
            text=True,
        )
        result = parse_evaluator_result(process.stdout, process.returncode)
        status = result["status"]
        status_counts[status] += 1
        warning_count += len(result.get("warnings", []))
        print(f"[{status.upper()}]")

        if status != "passed" or result.get("warnings"):
            findings.append(
                {
                    "file": filename,
                    "status": status,
                    "message": result.get("message", ""),
                    "warnings": result.get("warnings", []),
                    "output": process.stderr or process.stdout,
                }
            )

    elapsed = time.time() - start_time

    print("\n=== BULK EVALUATION REPORT ===")
    print(f"Total Evaluated: {len(evaluated_files)}")
    print(f"Passed: {status_counts['passed']}")
    print(f"Failed: {status_counts['failed']}")
    print(f"Review Required: {status_counts['review_required']}")
    print(f"Skipped: {status_counts['skipped']}")
    print(f"Warning Status: {status_counts['warning']}")
    print(f"Warnings: {warning_count}")
    print(f"Time Elapsed: {elapsed:.2f} seconds")

    if findings:
        print("\n--- Review and Failure Details ---")
        for finding in findings:
            print(f"\nNode: {finding['file']}")
            print(f"Status: {finding['status']}")
            print(f"Message: {finding['message']}")
            if finding["warnings"]:
                print(f"Warnings: {', '.join(finding['warnings'])}")

    if status_counts["failed"]:
        print("\n[FAILED] One or more executable checks failed.")
    elif status_counts["review_required"] or status_counts["skipped"]:
        print(
            "\n[REVIEW_REQUIRED] Executable checks completed, but semantic review "
            "or skipped dependencies still require attention."
        )
    elif status_counts["warning"]:
        print(
            "\n[WARNING] Executable sanity checks completed with audit-depth warnings. "
            "These results do not establish mathematical correctness."
        )
    else:
        print(
            "\n[PASSED] Executable sanity checks completed. "
            "These results do not establish mathematical correctness."
        )

    return {
        "total_evaluated": len(evaluated_files),
        "status_counts": status_counts,
        "warning_count": warning_count,
        "findings": findings,
        "elapsed_seconds": elapsed,
    }


def main():
    report = run_bulk_evaluation()
    if report["status_counts"]["failed"]:
        return 1
    if report["status_counts"]["review_required"] or report["status_counts"]["skipped"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
