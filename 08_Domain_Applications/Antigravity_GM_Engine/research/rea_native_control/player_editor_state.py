"""Explicit Native read projection and a capture-free role snapshot provider.

Native receipts and save/phase labels enter through the trusted embedding host.
This validates binding/shape, not authenticity of an operator-supplied receipt.
"""
import json
from copy import deepcopy
from pathlib import Path

from badge_fields import load_fields as load_badges
from contracts import NativeActionResult,Outcome
from player_fields import load_fields as load_stats

ACTION='READ_PLAYER_EDITOR_STATE'
DATASET='player.editor_state'
FAMILIES=('attributes','tendencies','badges','play_types')
CONTEXT=('world_id','save_instance_id','generation_id','season_id','phase','snapshot_ref')


def validate_projection(root,projection):
    root=Path(root)
    if not isinstance(projection,dict) or set(projection)!=set(FAMILIES):
        raise ValueError('Explicit arrays for all four Player read families required')
    stats,badges=load_stats(root),load_badges(root)
    allowed={family:{key for key,value in stats['families'][family].items() if value['callable']}
             for family in ('attributes','tendencies')}
    allowed['badges']={key for key,value in badges['fields'].items() if not value['sentinel_name']}
    allowed['play_types']={'1','2','3','4'}
    for family,selected in projection.items():
        if not isinstance(selected,list) or any(type(key) is not str for key in selected):
            raise ValueError('Exact string field IDs required')
        if len(selected)!=len(set(selected)) or set(selected)-allowed[family]:
            raise ValueError('Duplicate, protected or unknown Player read field')
    if not any(projection.values()):raise ValueError('At least one explicit Player read field required')
    return deepcopy(projection)


class PlayerEditorSnapshotProvider:
    """Bind one frozen Native observation to a host-attested context and read grants.

    Calling the provider performs no transport call, process lookup or capture.
    A new capture requires a separate explicit NativeReadFacade invocation.
    """
    def __init__(self,result,*,context,observation_ref,source_kind,root=None):
        root=Path(root) if root else Path(__file__).parent
        if not isinstance(result,NativeActionResult) or result.action_id!=ACTION or result.outcome!=Outcome.RETURNED:
            raise ValueError('Successful exact Player editor read result required')
        if set(context)!=set(CONTEXT) or any(type(context[key]) is not str or not context[key].strip() for key in CONTEXT):
            raise ValueError('Exact host observation context required')
        if source_kind not in {'OFFLINE_FIXTURE','NATIVE_TRANSPORT_RECEIPT'} or type(observation_ref) is not str or not observation_ref.strip():
            raise ValueError('Explicit observation provenance required')
        native=result.native_result
        if not isinstance(native,dict) or native.get('action_id')!=ACTION or native.get('outcome')!=Outcome.RETURNED.value:
            raise ValueError('Native result action/outcome mismatch')
        if source_kind=='NATIVE_TRANSPORT_RECEIPT' and native.get('evidence_id')!=observation_ref:
            raise ValueError('Transport evidence identity mismatch')
        details=native.get('details',{})
        if details.get('read_only') is not True or details.get('snapshot_bracket_unchanged') is not True:
            raise ValueError('Bracket-unchanged read-only receipt required; no atomic-snapshot claim')
        request=deepcopy(dict(result.original_request))
        if set(request)!={'team_id','player_id','projection'} or any(type(request[key]) is not int or not 0<=request[key]<=65534 for key in ('team_id','player_id')):
            raise ValueError('Exact read target required')
        projection=validate_projection(root,request['projection'])
        data=details.get('data')
        if not isinstance(data,dict) or set(data)!={'team_id','player_id','projection',*FAMILIES}:
            raise ValueError('Exact Player data shape required; no raw/debug payload accepted')
        if any(data[key]!=request[key] or type(data[key]) is not int for key in ('team_id','player_id')) or data['projection']!=projection:
            raise ValueError('Read target/projection mismatch')
        stats,badges=load_stats(root),load_badges(root)
        play_names=json.loads((root.parents[1]/'config/state_io_native/player.json').read_text(encoding='utf8'))['PLAY_TYPE_NAMES']
        values={}
        for family in FAMILIES:
            observed=data[family]
            if not isinstance(observed,dict) or set(observed)!=set(projection[family]):
                raise ValueError('Read field projection mismatch')
            for key,value in observed.items():
                if family=='badges':
                    field=badges['fields'][key]
                    if not isinstance(value,dict) or set(value)!={'raw_level','effective_level'} or any(type(level) is not int or not 0<=level<=7 for level in value.values()) or value['raw_level']>field['mask']:
                        raise ValueError('Invalid raw/effective Badge read')
                    if value['effective_level'] not in {value['raw_level'],0,1,2,3,4}:
                        raise ValueError('Effective Badge value contradicts original Getter clamp')
                    record=deepcopy(value)|{'maximum_edit_level':field['maximum'],'internal_enum_name':key,
                        'ui_label_verified':False,'raw_level_within_edit_range':value['raw_level']<=field['maximum']}
                elif family=='play_types':
                    if type(value) is not int or not 0<=value<=15:raise ValueError('Invalid PlayType read')
                    record={'value':value,'meaning':play_names[str(value)],'representation':'ORDERED_NATIVE_CATEGORY'}
                else:
                    if type(value) is not int or not 0<=value<=255:raise ValueError('Invalid Native stat Getter value')
                    field=stats['families'][family][key]
                    if family=='attributes' and not field['minimum']<=value<=field['maximum']:
                        raise ValueError('Native attribute Getter range mismatch')
                    record={'value':value,'meaning':field['meaning'],'name_known':field['name_known'],
                        'representation':'ORIGINAL_NATIVE_GETTER_INTEGER',
                        'within_known_edit_range':field['minimum']<=value<=field['maximum']}
                values[family+'.'+key]=record
        values['identity']={'team_id':request['team_id'],'player_id':request['player_id']}
        values['observation']={'source_kind':source_kind,'observation_ref':observation_ref,
            'context_source':'HOST_ATTESTED_NOT_NATIVE_SAVE_DETECTION',
            'scope':'Same-handler selected-field read; not independent effect/UI/persistence proof'}
        # Strings freeze both data and host labels against subsequent caller mutation.
        self._context=json.dumps(dict(context),sort_keys=True)
        self._values=json.dumps(values,sort_keys=True)
        self._team_id=request['team_id']

    def __call__(self,profile,dataset_id):
        if dataset_id!=DATASET:raise PermissionError('Player observation dataset mismatch')
        context=json.loads(self._context)
        if any(context[key]!=getattr(profile,key) for key in CONTEXT):raise ValueError('Player observation context mismatch')
        if self._team_id not in profile.team_scope:raise PermissionError('Player observation team outside read scope')
        grants=dict(profile.read_grants).get(DATASET)
        if grants is None or not {'identity','observation'}<=set(grants):
            raise PermissionError('Player read grant must include target identity and observation provenance')
        values=json.loads(self._values)
        if set(grants)-set(values):raise ValueError('Requested Player read field was not captured')
        data={key:values[key] for key in grants}
        return {key:context[key] for key in CONTEXT}|{'actor_uid':profile.actor_uid,'role_type':profile.role_type,
            'team_scope':list(profile.team_scope),'data':data}
