#!/usr/bin/env python3
"""Prove the B0 split moved text verbatim (check id b0_verbatim_move).

For AGENT_WORKING_DISCIPLINE.md, 01_os/README.md and the OS entry: take the candidate file,
drop the added "> 拆分说明" note, expand every （依据：…§ID） marker with fragment ID from
01_os/入口依据与事故记录_v1.md and every （按动作细则：…） stub with the same-heading block of
01_os/开发入口_按动作细则_v1.md, then compare with the base file ignoring whitespace only.
Every fragment and every detail block must be used exactly once.
For AGENTS.md: every section other than the five Human-approved dedup sections must equal
the base section ignoring whitespace; the dedup sections are printed for the reviewer.
Usage: verify_b0_split.py --base <40-char> [--repo-root .]  -> exit 0 b0_verbatim_move_ok
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

BASIS = "01_os/02_boot/os_entry/入口依据与事故记录_v1.md"
DETAIL = "01_os/02_boot/os_entry/开发入口_按动作细则_v1.md"
FILES = ["AGENT_WORKING_DISCIPLINE.md", "01_os/README.md", "01_os/开发入口与单窗口任务规范_v1.md"]
AGENTS_DEDUP = {
    "## Reusable task prototypes across models (Core-wide)": "AGENT_WORKING_DISCIPLINE.md §0.1",
    "## Execution-mode routing and development boundaries": "AGENT_WORKING_DISCIPLINE.md §0.2",
    "## Denial receipts as a model–OS fit signal": "AGENT_WORKING_DISCIPLINE.md §0.3",
    "## Trust-first cooperation and Agent self-reporting (Human decision 2026-11-17)": "AGENT_WORKING_DISCIPLINE.md §0.4",
    "## Default Task Orchestration": "AGENT_WORKING_DISCIPLINE.md §0、§8；开发入口 §5、§11",
}
MARKER = re.compile(r"（依据：入口依据与事故记录_v1\.md §([A-Z][0-9.]*-[0-9]+)）")
STUB = re.compile(r"^(#{1,6} .+)\n\n（按动作细则：[^\n]*）\n", re.M)
HEADING = re.compile(r"^(#{1,6}) ")


def squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


def sections(text: str) -> list[tuple[str, int, str]]:
    """(heading, level, block) for every heading outside code fences; block runs to next heading of level <= it."""
    lines = text.splitlines(keepends=True)
    heads, pos, fence = [], 0, False
    for line in lines:
        if line.startswith("```"):
            fence = not fence
        m = None if fence else HEADING.match(line)
        if m:
            heads.append((line.rstrip("\n"), len(m.group(1)), pos))
        pos += len(line)
    out = []
    for i, (head, level, start) in enumerate(heads):
        end = next((s for h, lv, s in heads[i + 1:] if lv <= level), len(text))
        out.append((head, level, text[start:end]))
    return out


def fragments(text: str) -> dict[str, str]:
    out = {}
    for head, level, block in sections(text):
        m = re.match(r"### ([A-Z][0-9.]*-[0-9]+) · ", head)
        if m and level == 3:
            out[m.group(1)] = block.split("\n", 1)[1]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args(argv)
    root = Path(args.repo_root).resolve()

    def base(rel: str) -> str:
        return subprocess.run(["git", "-C", str(root), "show", f"{args.base}:{rel}"], capture_output=True,
                              check=True).stdout.decode("utf-8")

    def cand(rel: str) -> str:
        return (root / rel).read_text(encoding="utf-8")

    errors: list[str] = []
    frags = fragments(cand(BASIS))
    detail = {h: b for h, lv, b in sections(cand(DETAIL)) if not h.startswith("# ")}
    used_frags: list[str] = []
    used_detail: list[str] = []
    for rel in FILES:
        text = re.sub(r"\n> 拆分说明（2026-11-18）：[^\n]*\n", "\n", cand(rel))

        def expand_marker(m: re.Match) -> str:
            used_frags.append(m.group(1))
            if m.group(1) not in frags:
                errors.append(f"MARKER_WITHOUT_FRAGMENT:{rel}:{m.group(1)}")
                return ""
            return frags[m.group(1)]

        def expand_stub(m: re.Match) -> str:
            used_detail.append(m.group(1))
            if m.group(1) not in detail:
                errors.append(f"STUB_WITHOUT_DETAIL:{rel}:{m.group(1)}")
                return ""
            return detail[m.group(1)]

        text = STUB.sub(expand_stub, text)
        text = MARKER.sub(expand_marker, text)
        if squash(text) != squash(base(rel)):
            a, b = squash(base(rel)), squash(text)
            i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
            errors.append(f"RECONSTRUCTION_MISMATCH:{rel}:at={i}:base={a[i:i+40]!r}:cand={b[i:i+40]!r}")
    # top-level detail blocks only: subsections (7.1, 9.2 …) travel inside their parent block
    top_detail = [h for h, lv, b in sections(cand(DETAIL)) if lv >= 2 and not any(
        h != p and h in pb for p, plv, pb in sections(cand(DETAIL)) if 2 <= plv < lv)]
    for fid in frags:
        if used_frags.count(fid) != 1:
            errors.append(f"FRAGMENT_USE_COUNT:{fid}:{used_frags.count(fid)}")
    for head in top_detail:
        if used_detail.count(head) != 1:
            errors.append(f"DETAIL_USE_COUNT:{head}:{used_detail.count(head)}")

    old_agents = {h: b for h, lv, b in sections(base("AGENTS.md")) if lv == 2}
    new_agents = {h: b for h, lv, b in sections(cand("AGENTS.md")) if lv == 2}
    if list(old_agents) != list(new_agents):
        errors.append("AGENTS_SECTION_SET_CHANGED")
    for head in old_agents:
        if head in AGENTS_DEDUP:
            continue
        if squash(old_agents[head]) != squash(new_agents.get(head, "")):
            errors.append(f"AGENTS_NON_DEDUP_SECTION_CHANGED:{head}")
    print("AGENTS dedup sections (semantic equivalence is for the independent reviewer):")
    for head, target in AGENTS_DEDUP.items():
        print(f"- {head} -> {target}: {len(old_agents.get(head, '').encode())} -> {len(new_agents.get(head, '').encode())} bytes")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"b0_verbatim_move_ok files={len(FILES)} fragments={len(frags)} detail_blocks={len(top_detail)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
