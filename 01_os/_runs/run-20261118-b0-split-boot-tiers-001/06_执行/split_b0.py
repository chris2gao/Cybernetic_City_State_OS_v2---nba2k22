#!/usr/bin/env python3
"""One-off construction step for OS-CORE-B0-SPLIT-BOOT-TIERS-20261118-001 (Human: 方案 B).

Moves text verbatim, never rewrites it:
  - incident / measurement / rationale fragments of B0 -> 01_os/入口依据与事故记录_v1.md,
    leaving a marker （依据：入口依据与事故记录_v1.md §ID） in place;
  - the on-action sections of the OS entry -> 01_os/开发入口_按动作细则_v1.md under the same
    headings, leaving the heading plus a one-line stub （按动作细则：...）.
Run once on the base tree. verify_b0_split.py (07_测试执行) proves the inverse reconstruction.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
BASIS = "01_os/02_boot/os_entry/入口依据与事故记录_v1.md"
DETAIL = "01_os/02_boot/os_entry/开发入口_按动作细则_v1.md"
ENTRY = "01_os/开发入口与单窗口任务规范_v1.md"
DISC = "AGENT_WORKING_DISCIPLINE.md"
README = "01_os/README.md"

# (id, file, section label, exact start, exact end) - end is searched after start.
FRAGMENTS = [
    ("W0-1", DISC, "§0", "*Paid for 2026-11-11, NBA2K22 Issue #40", "issuecomment-6796587612)."),
    ("W0.1-1", DISC, "§0.1", "*Paid for 2026-11-16, NBA2K22 T15 / GE-01:*", "adequate business delivery."),
    ("W1-1", DISC, "§1", "*Paid for 2026-07-25:* a long session", "rather than a loss."),
    ("W2-1", DISC, "§2", "*Paid for 2026-07-25:* a recursive", "It beats any configuration setting."),
    ("W2-2", DISC, "§2 The specific habits", "Measured 2026-07-26 across 50 Codex", "not estimates."),
    ("W2-3", DISC, "§2 slice reads", "*Measured:* 303 of 355", "roughly a fifth of all tool output."),
    ("W2-4", DISC, "§2 cap output", "*Measured:* output is median", "of every character returned."),
    ("W2-5", DISC, "§2 polling", "*Measured:* the `wait` tool", "that was never used."),
    ("W2-6", DISC, "§2 Git summary", "*Measured:* one `git status`", "real output was longer still."),
    ("W2-7", DISC, "§2 script files", "*Measured:* one quoting mistake", "**twice the cost**."),
    ("W2-8", DISC, "§2 What is not worth optimising", "The shell *invocation* is not where", "output volume does."),
    ("W3-1", DISC, "§3", "*Paid for 2026-07-25, three times:*", "Each would have been expensive to undo."),
    ("W4-1", DISC, "§4", "*Paid for 2026-07-25:* two dispatches", "reported the contradiction."),
    ("W5-1", DISC, "§5", "*Standing failure mode:*", "reproducing itself."),
    ("W6-1", DISC, "§6", "*Paid for once:* an executor", "it fails inconsistently."),
    ("W7-1", DISC, "§7", "*Paid for repeatedly:*", "believe."),
    ("W8-1", DISC, "§8", "*Measured 2026-08-28 on `d9a18b57`:*", "cannot tell live work from history."),
    ("W8-2", DISC, "§8 enumeration cost", "That bill is also why enumeration", "all of it is the communication surface."),
    ("W8-3", DISC, "§8 hiding", "An\n  earlier revision of that tool", "the repository cannot vouch for."),
    ("W9-1", DISC, "§9", "*Paid for 2026-10-23, NBA2K22 R00-01:*", "authorization and proof."),
    ("R-1", README, "Two rules", "A registry that lags is a registry", "found by accident."),
    ("E5-1", ENTRY, "§5", "*实测 2026-08-28 于 `d9a18b57`：*", "的机器判据。"),
]

# heading in the OS entry -> stub sentence (when to read the detail file)
STUBS = {
    "### 1.1 发布传输矩阵": "commit、push、开 PR 或任何发布之前读 §1.1",
    "### 1.2 执行环境约定": "派单固定执行环境、在本仓跑 Git / Python 测试或做候选受控验证之前读 §1.2",
    "## 3. 文件放置规则": "新增、移动或删除文件、判断文件放在哪里时读 §3",
    "## 4. registry 同步规则": "新增或移动 canonical 文件 / path-set、修改 registry 时读 §4",
    "## 6. 分支与发布纪律": "建分支、提交、发布或 master 集成之前读 §6",
    "## 7. 任务包必须包含的字段": "写或读任务包、选择执行者（7.1 模型路由 preflight）、向 Human 请求批准或确认（7.2）时读 §7（含 7.1、7.2）",
    "## 8. 测试与证据标准": "设计或执行测试、写证据、进入开发内部 Loop 时读 §8（含 8.1）",
    "## 9. 独立审核与 Human 决策/确认": "派审核、做审核、安排审核时机或请 Human 决策 / 确认时读 §9（含 9.1–9.3）",
    "## 10. completion pointer 最小模板": "写 completion pointer 或收尾交接时读 §10",
    "## 12. 权威参考": "查某条规则的 canonical 来源，或本文件与 canonical 定义冲突时读 §12",
    "## 13. 现场经验回流到共享 OS": "要把现场经验回流到共享 OS 时读 §13",
}

NOTES = {
    DISC: ("Every rule below was paid for. The incident is named so the rule is not mistaken\nfor style preference.\n",
           "> 拆分说明（2026-11-18）：事故经过、实测数字与设计理由已原文移入 `01_os/02_boot/os_entry/入口依据与事故记录_v1.md`，"
           "本文件在原位以“（依据：入口依据与事故记录_v1.md §编号）”指向；要理解、质疑或修改某条规则时去读。规则本身未改。\n"),
    ENTRY: ("不在这里重复。目录语义、机制定义和机器契约以本文件引用的 canonical 文件为准。\n",
            "> 拆分说明（2026-11-18）：本文件是启动必读核心，保留第 1、2、5、11 节正文。第 1.1、1.2、3、4、6–10、12、13 节"
            "的正文按原节号原文移入 `01_os/02_boot/os_entry/开发入口_按动作细则_v1.md`，本文件在原位保留节标题与“何时读”；引用“开发入口 §x”"
            "时按该指针读细则。两份文件同属本规范，效力相同。事故与实测在 `01_os/02_boot/os_entry/入口依据与事故记录_v1.md`。\n"),
}

HEADING = re.compile(r"^(#{1,6}) ")


def blocks(text: str) -> list[tuple[str, int, int]]:
    """(heading line, start, end) for every heading outside code fences; end = next heading of level <= it."""
    lines = text.splitlines(keepends=True)
    offsets, pos, fence = [], 0, False
    for line in lines:
        if line.startswith("```"):
            fence = not fence
        m = None if fence else HEADING.match(line)
        if m:
            offsets.append((line.rstrip("\n"), len(m.group(1)), pos))
        pos += len(line)
    out = []
    for i, (head, level, start) in enumerate(offsets):
        end = next((s for h, lv, s in offsets[i + 1:] if lv <= level), len(text))
        out.append((head, start, end))
    return out


def main() -> int:
    texts = {f: (ROOT / f).read_text(encoding="utf-8") for f in {DISC, README, ENTRY}}
    basis = ["# 入口依据与事故记录 v1", "",
             "> 本文件收存 B0 入口文件（`AGENT_WORKING_DISCIPLINE.md`、`01_os/README.md`、`01_os/开发入口与单窗口任务规范_v1.md`）"
             "里原有的事故经过、实测数字与设计理由，2026-11-18 由任务 OS-CORE-B0-SPLIT-BOOT-TIERS-20261118-001 原文移入（Human 选择方案 B）。"
             "源文件在原位以“（依据：入口依据与事故记录_v1.md §编号）”指向这里。读取层：按动作读取——要理解、质疑或修改某条规则时读。"
             "这里只是依据，不是规则；规则以源文件为准。", ""]
    current = None
    for fid, rel, label, start, end in FRAGMENTS:
        text = texts[rel]
        s = text.find(start)
        e = text.find(end, s)
        if s < 0 or e < 0 or text.find(start, s + 1) >= 0:
            raise SystemExit(f"FRAGMENT_NOT_UNIQUE:{fid}")
        e += len(end)
        fragment = text[s:e]
        texts[rel] = text[:s] + f"（依据：入口依据与事故记录_v1.md §{fid}）" + text[e:]
        if rel != current:
            basis += [f"## `{rel}`", ""]
            current = rel
        body = "\n".join(line[2:] if line.startswith("  ") else line for line in fragment.split("\n"))
        basis += [f"### {fid} · {label}", "", body, ""]

    entry = texts[ENTRY]
    detail = ["# 01 OS 开发入口：按动作细则 v1", "",
              "> 本文件是 `01_os/开发入口与单窗口任务规范_v1.md` 的按动作读取部分，2026-11-18 由任务 "
              "OS-CORE-B0-SPLIT-BOOT-TIERS-20261118-001 按原节号原文移出（Human 选择方案 B）。效力与开发入口相同；"
              "开发入口在每个节标题下写明做到哪个动作时读本文件的哪一节。", ""]
    found = {h: (s, e) for h, s, e in blocks(entry)}
    for head in sorted(STUBS, key=lambda h: found[h][0], reverse=True):
        s, e = found[head]
        detail_block = entry[s:e]
        stub = f"{head}\n\n（按动作细则：{STUBS[head]}，见 `01_os/02_boot/os_entry/开发入口_按动作细则_v1.md`。）\n\n"
        entry = entry[:s] + stub + entry[e:]
        detail.insert(4, detail_block.rstrip("\n") + "\n")
    texts[ENTRY] = entry

    for rel, (anchor, note) in NOTES.items():
        if texts[rel].count(anchor) != 1:
            raise SystemExit(f"NOTE_ANCHOR:{rel}")
        texts[rel] = texts[rel].replace(anchor, anchor + "\n" + note)

    for rel, text in texts.items():
        (ROOT / rel).write_text(text.rstrip("
") + "
", encoding="utf-8", newline="\n")
    (ROOT / BASIS).write_text("\n".join(basis).rstrip() + "\n", encoding="utf-8", newline="\n")
    (ROOT / DETAIL).write_text("\n".join(detail).rstrip() + "\n", encoding="utf-8", newline="\n")
    print("split_done fragments=%d stubs=%d" % (len(FRAGMENTS), len(STUBS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
