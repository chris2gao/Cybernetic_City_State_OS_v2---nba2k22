"""Independent observations vs verified applied intent; drift never causes writes."""
import json
import save_context
from .codec import decode, normalized_value
from .common import binding, canonical
from .plan import load_plan
from .store import connect
from .workspace import Workspaces, lifecycle_lock


def reconcile(source, registry):
    with lifecycle_lock():
        w=Workspaces().active(source['save_id'],source)
        objects={o['object_key']:o for o in source['objects']}
        rows=[]
        seen=set()
        with connect(save_context.save_paths(w['save_id'])['control_db_path']) as c:
            plans=c.execute("SELECT d.plan_json FROM desired_change_sets d JOIN execution_runs e USING(change_set_id) WHERE e.status='MEMORY_VERIFIED' ORDER BY e.started_at DESC").fetchall()
            for p in plans:
                plan=json.loads(p[0])
                latest=c.execute('SELECT status FROM execution_runs WHERE change_set_id=? ORDER BY started_at DESC LIMIT 1',(plan['change_set_id'],)).fetchone()
                if latest[0] != 'MEMORY_VERIFIED' or binding(plan)!=binding(source):
                    continue
                if source['source_batch_id']==plan['source_batch_id']:
                    raise ValueError('RECONCILE_REQUIRES_NEW_INDEPENDENT_OBSERVATION')
                if source['registry_version']!=plan['registry_version']:
                    raise ValueError('RECONCILIATION_REGISTRY_CHANGED')
                for action in plan['actions']:
                    field_target=(action['object_key'],action['field_key'])
                    if field_target in seen:
                        continue
                    seen.add(field_target)
                    obj=objects.get(action['object_key'])
                    value=None
                    if obj is None:
                        coverage=source.get('coverage',{}).get(action['selector']['target_kind'],{})
                        status='NOT_OBSERVED' if coverage.get('status') in ('NOT_OBSERVED','PARTIALLY_OBSERVED') else (
                            'IDENTITY_CHANGED' if any(o['selector'].get('team_id')==action['selector'].get('team_id') and o['selector']['target_kind']==action['selector']['target_kind'] for o in objects.values()) else 'NOT_OBSERVED')
                    elif obj['identity']!=action['identity']:
                        status='IDENTITY_CHANGED'
                    else:
                        values=[decode(bytes.fromhex(m['raw']),registry.field(action['field_key'])) for m in (obj.get('members') or [obj])]
                        value=values[0] if len(set(values))==1 else values
                        if all(v==normalized_value(action['target_value'],registry.field(action['field_key'])) for v in values):
                            status='MATCHED'
                        elif action['domain']=='training' and any(k.endswith('automate_intensity') and v for k,v in obj.get('values',{}).items()):
                            status='GAME_MANAGED_EXPECTED'
                        else:
                            status='DRIFT_DETECTED'
                    key=action['object_key']+':'+action['field_key']
                    c.execute('INSERT OR REPLACE INTO reconciliation_records VALUES (?,?,?,?,?,?,?)',
                              (plan['change_set_id'],source['source_snapshot_id'],key,canonical(action['target_value']),canonical(value),status,'REPORT_ONLY_NO_GAME_WRITES'))
                    rows.append(dict(change_set_id=plan['change_set_id'],action_id=action['action_id'],status=status,observed=value))
        return dict(status='RECONCILED_REPORT_ONLY',source_batch_id=source['source_batch_id'],rows=rows,game_writes=0)
