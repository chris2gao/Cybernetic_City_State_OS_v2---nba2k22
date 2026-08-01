from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def failed_node_ids(path: Path) -> list[str]:
    root = ET.parse(path).getroot()
    values = []
    for testcase in root.iter("testcase"):
        if testcase.find("failure") is None and testcase.find("error") is None:
            continue
        classname = testcase.attrib.get("classname", "")
        name = testcase.attrib.get("name", "")
        values.append(f"{classname}::{name}")
    return sorted(values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    baseline = failed_node_ids(args.baseline)
    candidate = failed_node_ids(args.candidate)
    exact = baseline == candidate
    print(
        json.dumps(
            {
                "baseline_failed_node_ids": len(baseline),
                "candidate_failed_node_ids": len(candidate),
                "candidate_caused_failures": len(set(candidate) - set(baseline)),
                "node_ids_exact_match": exact,
            },
            sort_keys=True,
        )
    )
    return 0 if exact else 1


if __name__ == "__main__":
    raise SystemExit(main())
