"""Assert the seven-wrapper repair is byte-exact and changes no dependency body."""
from pathlib import Path
import hashlib
import json
import subprocess

BASE = "3dc058a1a3cf393b936025f43fd737b0848937b4"
OLD = b"9c2828be3231ffd5370f9170cd67c1af61347bcb"
NEW = b"0a49b85a4518dc123b3c01e3a46f5454d9a55cc1"
STAGES = ("01_需求建模", "02_信息收集与提炼", "03_结果建模", "04_测试生成",
          "05_步骤拆分", "06_执行", "07_测试执行")
WRAPPERS = [f"01_os/01_workflow/{stage}/实现/阶段协同推演profile引用_v1.yml" for stage in STAGES]
TARGET = "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profile契约_v1.yml"


def read_base(path):
    proc = subprocess.run(["git", "show", BASE + ":" + path], capture_output=True)
    if proc.returncode or proc.stderr:
        raise RuntimeError((path, proc.returncode, proc.stderr.decode("utf-8", "strict")))
    return proc.stdout


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


target = Path(TARGET).read_bytes()
require(target == read_base(TARGET), "profile contract changed")
blob = hashlib.sha1(f"blob {len(target)}\0".encode() + target).hexdigest()
require(blob == NEW.decode(), "unexpected target blob")
discovered = sorted(p.as_posix() for p in Path("01_os/01_workflow").glob("*/实现/阶段协同推演profile引用_v1.yml"))
require(discovered == sorted(WRAPPERS), "wrapper population differs from the exact seven paths")
for path in WRAPPERS:
    before = read_base(path)
    after = Path(path).read_bytes()
    require(before.count(OLD) == 1, f"old pin count: {path}")
    require(after == before.replace(OLD, NEW), f"non-pin change: {path}")
for dependency in ("方法论_v1.md", "阶段profiles_v1.yml", "激活状态_v1.yml",
                   "实现/加载与receipt契约_v1.yml", "实现/verify_stage_collaborative_deliberation_v2.py"):
    path = "01_os/03_mechanisms/stage_collaborative_deliberation/" + dependency
    require(Path(path).read_bytes() == read_base(path), f"dependency changed: {path}")
plan = "01_os/_runs/run-20260907-os-execution-foundation-001/07_测试执行/required_checks.json"
proc = subprocess.run(["git", "show", "46acc0918d3d262e21e69ffe99002837a989ff53:" + plan], capture_output=True)
require(proc.returncode == 0 and not proc.stderr, "cannot read previous candidate plan")
require(Path(plan).read_bytes() == proc.stdout, "required check plan changed")
print(json.dumps({"status": "passed", "base": BASE, "wrapper_count": len(WRAPPERS),
                  "pin_only": True, "target_blob": blob, "dependency_bodies_unchanged": True,
                  "required_check_plan_unchanged": True}, indent=2))
