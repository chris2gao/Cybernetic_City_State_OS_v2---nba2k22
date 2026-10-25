"""Reproduce owner database operation tests/smoke, without game or Native reads."""
import argparse,hashlib,json,platform,sqlite3,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser();parser.add_argument('new_output_directory');args=parser.parse_args();out=Path(args.new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);repo=BASE.parents[2]
    commands={'tests':[sys.executable,'-m','unittest','discover','-s',str(BASE/'tests'),'-p','test_*.py','-q'],
        'sqlite_smoke':[sys.executable,str(BASE/'cli.py'),'smoke']};results={}
    for name,command in commands.items():
        result=subprocess.run(command,cwd=repo,capture_output=True);(out/(name+'.stdout.log')).write_bytes(result.stdout);(out/(name+'.stderr.log')).write_bytes(result.stderr);results[name]=result.returncode
        if result.returncode:print(json.dumps({'status':'OPERATION_CHECK_FAILED','command':name,'exit':result.returncode}));return result.returncode
    files=sorted(BASE.glob('*.py'))+sorted(BASE.glob('*profile.json'))+[BASE/'schema.sql',BASE/'schema_model.py',BASE/'field_dictionary.json']+sorted((BASE/'tests').glob('test_*.py'))
    report={'status':'DATABASE_OPERATION_DEVELOPMENT_CHECKS_PASSED_NOT_FINAL_ACCEPTANCE','candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),
        'environment':{'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'platform':platform.system()},'commands':commands,'exit_codes':results,
        'code_sha256':{p.relative_to(BASE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'game_access':False,'real_backup_proof':'Separate actual-recovery-report.json, not inferred from unit tests',
        'executed_100_season_test':False,'full_goal_complete':False,'independent_review':False}
    (out/'operations_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'status':report['status'],'exit_codes':results}));return 0

if __name__=='__main__':raise SystemExit(main())
