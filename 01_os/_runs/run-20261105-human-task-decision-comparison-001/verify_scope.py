"""Verify this documentation-only change against the exact approved base."""
import subprocess
from pathlib import Path

BASE = "2a488127db7e77545e23de8b8bc5e05a8f8d1df8"
SPEC = "01_os/开发入口与单窗口任务规范_v1.md"
RUN = Path(__file__).relative_to(Path.cwd()).parent.as_posix() + "/"


def git(*args):
    return subprocess.check_output(["git", *args]).decode("utf-8")


before = git("show", f"{BASE}:{SPEC}")
after = git("show", f"HEAD:{SPEC}")
section = "### 7.2 Human 确认与大任务预确认\n\n"
head, tail = before.split(section)
assert after.startswith(head + section) and after.endswith(tail)
inserted = after[len(head + section):-len(tail)]
for anchor in ("原有实现与问题", "目标与具体施工", "差异与边界", "取舍与验证",
               "批准后的执行", "第 8.1 节", "第 9 节", "Publication Gate", "受保护"):
    assert anchor in inserted, anchor
paths = git("diff", "--name-only", "--no-renames", "-z", BASE, "HEAD").strip("\0").split("\0")
assert [p for p in paths if not p.startswith(RUN)] == [SPEC], paths
subprocess.run(["git", "diff", "--check", BASE, "HEAD"], check=True)
print("Scope PASS: one canonical insertion in §7.2, existing text byte-identical, no other canonical changes.")
