"""Syntax/format reading only, explicitly not a functional or fixture test."""
import ast,json,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];counts={'python_parsed':0,'json_read':0}
for p in root.rglob('*.py'):
 ast.parse(p.read_text(encoding='utf-8-sig'),filename=p.name);counts['python_parsed']+=1
for p in root.rglob('*.json'):
 json.loads(p.read_text(encoding='utf-8-sig'));counts['json_read']+=1
node=shutil.which('node');counts['javascript_syntax_parsed']=0
if node:
 for p in (root/'runtime').glob('*.js'):
  r=subprocess.run([node,'--check',str(p)],capture_output=True,text=True)
  if r.returncode:raise SyntaxError(r.stderr)
  counts['javascript_syntax_parsed']+=1
ps=shutil.which('powershell.exe');counts['powershell_syntax_parsed']=0
if ps:
 for p in root.glob('*.ps1'):
  r=subprocess.run([ps,'-NoProfile','-File',str(root/'tools/parse_powershell.ps1'),'-Path',str(p)],capture_output=True,text=True)
  if r.returncode:raise SyntaxError(r.stdout+r.stderr)
  counts['powershell_syntax_parsed']+=1
print(json.dumps({'result':'SOURCE_FILES_READABLE_ONLY',**counts,'business_code_imported_or_executed':False,'fixtures_or_functional_tests':False,'game_process_access':False}))
