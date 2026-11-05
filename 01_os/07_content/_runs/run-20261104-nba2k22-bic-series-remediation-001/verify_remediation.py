"""Reproduce four BIC remediation checks without game access."""
import hashlib,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
D=Path("08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype")
tests=["test_bic_baseline.py","test_bic_experiments.py","test_observation_scope.py","test_player_details.py","test_bic_remediation.py"]
command=[sys.executable,"-B","-m","pytest",*[str(D/"tests"/name) for name in tests],"-q","-W","always"]
start=time.perf_counter()
rawdir=OUT/'_runtime';rawdir.mkdir(exist_ok=True)
with (rawdir/"regression.stdout.log").open("wb") as stdout,(rawdir/"regression.stderr.log").open("wb") as stderr:
    result=subprocess.run(command,cwd=ROOT,stdout=stdout,stderr=stderr)
elapsed=time.perf_counter()-start
for name in ('regression.stdout.log','regression.stderr.log'):
    (OUT/name).write_bytes((rawdir/name).read_bytes().replace(str(Path(sys.prefix)).encode(),b'<python-runtime>'))
path=(D/"tests/test_player_details.py").as_posix()
old=subprocess.check_output(["git","show","a3e28e186f198e731c76b74f939da2950b5d15bd:"+path],cwd=ROOT)
current=(ROOT/path).read_bytes().replace(b"\r\n",b"\n")
original=subprocess.check_output(["git","show","66f8f73f1a91597f4562b834c2acad332ad9de5b:"+path],cwd=ROOT)
warning={"test_path":path,"old_blob_sha256":hashlib.sha256(old).hexdigest(),"current_lf_sha256":hashlib.sha256(current).hexdigest(),"pre_bic_sha256":hashlib.sha256(original).hexdigest(),"identical_at_pre_bic_and_reviewed_base_and_current":old==original==current,"type":"PytestReturnNotNoneWarning","function":"test_manifest","cause":"pytest collects a helper named test_manifest which returns a dict; source unchanged since pre-BIC","observed_in":"regression.stdout.log","scope":"Existing test helper naming/return contract; no broad unrelated cleanup"}
(OUT/"warning_provenance.json").write_text(json.dumps(warning,indent=2)+"\n",encoding="utf-8",newline="\n")
sys.path.insert(0,str(ROOT/D));sys.path.insert(0,str(ROOT/D/"tests"))
from test_observation_scope import ObservationScopeTests,T1
from bic_baseline import player_baseline,coverage_report,knowledge_query
import types
old_module=types.ModuleType("old_bic")
exec(compile(subprocess.check_output(["git","show","a3e28e18:"+str(D/"bic_baseline.py").replace("\\","/")],cwd=ROOT),"<fixed-reviewed-bic>","exec"),old_module.__dict__)
fixture=ObservationScopeTests();fixture.setUp()
try:
    timings={}
    for label,reader,report in [("reviewed",old_module.player_baseline,old_module.coverage_report),("remediated",player_baseline,coverage_report)]:
        start=time.perf_counter()
        for _ in range(3):
            baseline=reader(fixture.db,"p1",save_id="save",season_id="s1",as_of=T1)
            report(baseline)
        timings[label]={"iterations":3,"total_seconds":time.perf_counter()-start}
    sample=knowledge_query("player_attribute_snapshots.overall_raw",baseline=baseline)
finally:fixture.doCleanups()
(OUT/"performance.json").write_text(json.dumps({"fixture":"SYNTHETIC_HISTORY_SCOPE","timings":timings,"limits":"Small fixture and three warm process iterations; not a full-world benchmark","example_knowledge_query":sample},indent=2)+"\n",encoding="utf-8",newline="\n")
receipt={"checked_at":datetime.now(timezone.utc).isoformat(),"command":["python"]+command[1:],"exit_code":result.returncode,"elapsed_seconds":elapsed,"stdout":"regression.stdout.log","stderr":"regression.stderr.log","source_base":"a3e28e186f198e731c76b74f939da2950b5d15bd","formal_os_pass":False,"log_redaction":"Only Python installation prefix replaced with <python-runtime>; original logs retained in local _runtime", "raw_stdout_sha256":hashlib.sha256((rawdir/'regression.stdout.log').read_bytes()).hexdigest()}
(OUT/"verification_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8",newline="\n")
print(json.dumps({"exit_code":result.returncode,"warning_source_equal":warning["identical_at_pre_bic_and_reviewed_base_and_current"],"timings":timings}))
sys.exit(result.returncode)
