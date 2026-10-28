"""Render declared coverage and hash retained static sources; no behavioral checks."""
import collections,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];d=json.loads((root/'data/action_registry.json').read_text(encoding='utf-8'));bindings=json.loads((root/'data/native_bindings.json').read_text(encoding='utf-8'))['bindings'];counts=collections.Counter(a['capability'] for a in d['actions'])
lines=['# 操作覆盖清单（本轮均未实测）','','从Human九域模型派生，包含原定46项及静态发现/参考补充。PRIOR_LIVE_SUCCESS仅继承PR12；其他状态不代表新实机通过。部分Reader可返回明确子集，coverage_unknowns保留缺口。','','| 动作ID | 域 | 成熟度 | 输入键 | 实现/缺口 |','|---|---|---|---|---|']
for a in d['actions']:
 gap='; '.join(a['unknowns']+a.get('coverage_unknowns',[]));impl=a['runtime_handler'] or gap or 'UNKNOWN'
 lines.append('| '+a['action_id']+' | '+a['domain']+' | '+a['capability']+' | '+', '.join(a['input_schema'])+' | '+impl.replace('|','/')+' |')
lines+=['','## Native绑定索引','','RVA均来自固定PC22构建。UNKNOWN返回类型/参数或unknowns非空时不可执行；LAYOUT是只读布局，不冒充业务函数。完整对象、生命周期、指纹及参数编码在data/native_bindings.json和runtime源码。','','| Binding | RVA | 返回 | 显式Win64参数 | 缺口 |','|---|---|---|---|---|']
for b in bindings:
 lines.append('| '+b['binding_id']+' | '+(hex(b['rva']) if b['rva'] is not None else 'LAYOUT')+' | '+b['return_type']+' | '+', '.join(p['name']+':'+p['type'] for p in b['parameters'])+' | '+'; '.join(b['unknowns']).replace('|','/')+' |')
(root/'ACTION_SURFACE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
files=[]
for p in sorted((root/'evidence/static').glob('*.json')):files.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_kind':'PC22_STATIC_NO_LIVE_ACCESS'})
(root/'evidence/manifest.json').write_text(json.dumps({'schema_version':'nba2k22.native_control.static_evidence.v1','game_build_sha256':d['game_build_sha256'],'files':files,'prior_live_success_source_commit':'f6b2f5deb73218406f034c5418896c4bfade8e64','new_live_fixture_or_regression_tests':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'domains':len(d['domains']),'actions':len(d['actions']),'status_counts':counts,'runtime_handlers':len({a['runtime_handler'] for a in d['actions'] if a['runtime_handler']}),'bindings':len(bindings),'retained_static_files':len(files),'static_bytes':sum(p['bytes'] for p in files),'new_tests':False}))
