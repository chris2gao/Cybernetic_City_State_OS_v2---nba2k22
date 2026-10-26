import json,shutil,subprocess
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';dest=r.parent/'06_执行/increment35/deferred-overall';dest.mkdir(parents=True,exist_ok=False)
tracked=['TABLE_CARDS.md','cli.py','field_dictionary.json','observation_scope.py','query.py','refresh.py','schema.sql','schema_model.py','tests/test_refresh.py','tests/test_world_data.py'];new=['overall_codec.py','overall_native_profile.json','overall_reader.py'];prefix=app.relative_to(repo)
status=subprocess.run(['git','status','--porcelain'],capture_output=True,text=True,check=True).stdout;expected={str(prefix/Path(name)).replace('\\','/') for name in tracked+new}
assert all(line[3:] in expected for line in status.splitlines()),'Unexpected concurrent worktree edits; stop before restoring.'
patch=subprocess.run(['git','diff','--binary','--',*[str(prefix/Path(name)) for name in tracked]],capture_output=True,check=True).stdout;(dest/'unintegrated-wip.patch').write_bytes(patch)
for name in new:shutil.copyfile(app/name,dest/name)
for name in ('overall-metadata35.json','overall-code-candidates35.json','overall-getters35.json','coverage35.json'):shutil.copyfile(r/name,dest/name)
subprocess.run(['git','restore','--worktree','--',*[str(prefix/Path(name)) for name in tracked]],check=True)
for name in new:(app/name).unlink()
(dest/'README.md').write_text('# Human-deferred overall research\n\nHuman2026-10-26: overall can be omitted from this task and reconsidered later.\nThese files retain unfinished, untested WIP and static research only.\nThey are outside the active app, not imported, not a deliverable reader, not\nverified live cache data, not a schema migration, and not approval to resume.\nThe actual bound database remainsv24; no overall Native values were acquired.\n',encoding='utf-8',newline='\n')
print(json.dumps({'status':'OVERALL_WIP_REMOVED_FROM_ACTIVE_APP_AND_RETAINED_AS_DEFERRED_RESEARCH','restored_tracked_files':len(tracked),'removed_untracked_active_files':len(new),'game_writes':False,'database_changed':False}))
