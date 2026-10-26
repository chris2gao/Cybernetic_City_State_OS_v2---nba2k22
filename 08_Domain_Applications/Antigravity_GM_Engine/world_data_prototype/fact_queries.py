"""Typed public fact filtering and exclusive source-qualified JSONL export."""
from contextlib import closing
from dataclasses import asdict
from datetime import datetime,timezone
import hashlib,json,math,os
from pathlib import Path
from observation_scope import current_scope,observed_as_of,query_connection
from schema_model import TABLES,ident

OPS={'eq':'=','ne':'!=','lt':'<','lte':'<=','gt':'>','gte':'>='}


def _public(table,role):
    if role!='GM':raise PermissionError('unsupported fact-query role')
    if not isinstance(table,str) or table not in TABLES or not TABLES[table].public:raise PermissionError('owner-only or unknown fact dataset')
    spec=TABLES[table];fields={c.name:c for c in spec.columns if c.visibility=='GM_PUBLIC'}
    if spec.key not in fields:raise PermissionError('dataset has no public row identity')
    return spec,fields


def fact_fields(table,*,role='GM'):
    spec,fields=_public(table,role)
    return {'table':table,'domain':spec.domain,'grain':spec.grain,'key':spec.key,'role':role,'columns':[asdict(c) for c in fields.values()],
        'operators':list(OPS)+['in','is_null','not_null'],'filter_scope':'AND of typed column predicates; row observations, not per-field latest assembly',
        'permission_scope':'Public typed fields only; no owner artifacts or restricted Potential storage'}


def _typed(column,value):
    if column.kind=='TEXT':valid=isinstance(value,str) and len(value)<=4096
    elif column.kind=='INTEGER':valid=type(value) is int and -(2**63)<=value<2**63
    elif column.kind=='REAL':valid=type(value) in (int,float) and -(2**63)<=value<2**63 and math.isfinite(value)
    else:valid=False
    if not valid:raise ValueError('filter value does not match public column type: '+column.name)
    return value


def _plan(table,columns,filters,role):
    spec,fields=_public(table,role)
    if columns is None:columns=list(fields)
    if not isinstance(columns,list) or not 1<=len(columns)<=512 or any(not isinstance(n,str) or n not in fields for n in columns) or len(set(columns))!=len(columns):raise ValueError('columns must be unique public field names')
    if filters is None:filters=[]
    if not isinstance(filters,list) or len(filters)>16:raise ValueError('at most 16 typed AND filters allowed')
    clauses=[];args=[];normalized=[]
    for condition in filters:
        if not isinstance(condition,dict) or not isinstance(condition.get('column'),str) or condition['column'] not in fields or not isinstance(condition.get('op'),str):raise ValueError('invalid public field filter')
        name,op=condition['column'],condition['op'];column=fields[name];sql='t.'+ident(name)
        if op in ('is_null','not_null'):
            if set(condition)!={'column','op'}:raise ValueError('NULL filters do not accept a value')
            clauses.append(sql+(' IS NULL' if op=='is_null' else ' IS NOT NULL'));normalized.append(dict(condition));continue
        if set(condition)!={'column','op','value'}:raise ValueError('value-bearing filter requires column/op/value')
        value=condition['value']
        if op=='in':
            if not isinstance(value,list) or not 1<=len(value)<=100:raise ValueError('in filter needs 1..100 typed values')
            values=[_typed(column,v) for v in value];clauses.append(sql+' IN ('+','.join('?' for _ in values)+')');args.extend(values);normalized.append({'column':name,'op':op,'value':values})
        elif op in OPS:
            value=_typed(column,value);clauses.append(sql+OPS[op]+'?');args.append(value);normalized.append({'column':name,'op':op,'value':value})
        else:raise ValueError('unsupported filter operator')
    observed='unit_id' in fields
    if observed:clauses.append("u.unit_status='success'")
    source=' FROM '+ident(table)+' t'
    if observed:source+=' JOIN capture_units u ON u.unit_id=t.unit_id JOIN capture_runs r ON r.run_id=u.run_id'
    projection=['t.'+ident(spec.key)+' AS __fact_key']+['t.'+ident(n)+' AS value_'+str(i) for i,n in enumerate(columns)]
    if observed:projection+=['u.'+n+' AS meta_'+n for n in ('unit_id','observed_at','effective_at','completeness','source_key','layout_version')]+['r.source_grade AS meta_source_grade']
    return spec,list(columns),normalized,source,clauses,args,','.join(projection),observed


def _record(row,columns,observed):
    provenance={n:row['meta_'+n] for n in ('unit_id','observed_at','effective_at','completeness','source_key','layout_version','source_grade')} if observed else {'status':'CANONICAL_OR_DICTIONARY_ROW_WITHOUT_OWN_CAPTURE_UNIT'}
    return {'row_key':row['__fact_key'],'values':{n:row['value_'+str(i)] for i,n in enumerate(columns)},'provenance':provenance}


def _validate_cursor(cursor,target):
    if not isinstance(cursor,dict) or set(cursor)!={'format','target','observed_through','scope_sha256','after_key'} or cursor['format']!='WORLD_FACT_CURSOR_V1' or cursor['target']!=target or not isinstance(cursor['after_key'],str):raise ValueError('invalid fact-query cursor or changed query target')


def query_facts(path,table,*,columns=None,filters=None,limit=100,cursor=None,role='GM'):
    if type(limit) is not int or not 1<=limit<=1000:raise ValueError('fact query limit must be 1..1000')
    spec,columns,filters,source,clauses,args,projection,observed=_plan(table,columns,filters,role);target={'table':table,'columns':columns,'filters':filters}
    if cursor is not None:_validate_cursor(cursor,target)
    scope=current_scope()
    if scope is None:
        cutoff=cursor['observed_through'] if cursor else datetime.now(timezone.utc).isoformat()
        with observed_as_of(path,cutoff):return query_facts(path,table,columns=columns,filters=filters,limit=limit,cursor=cursor,role=role)
    if cursor is not None:
        if cursor['observed_through']!=scope.observed_through or cursor['scope_sha256']!=scope.fingerprint:raise ValueError('observation ledger or acquisition cutoff changed; restart paging')
        clauses.append('t.'+ident(spec.key)+'>?');args.append(cursor['after_key'])
    sql='SELECT '+projection+source+(' WHERE '+' AND '.join(clauses) if clauses else '')+' ORDER BY t.'+ident(spec.key)+' LIMIT ?'
    with closing(query_connection(path,True)) as conn:rows=conn.execute(sql,args+[limit+1]).fetchall()
    more=len(rows)>limit;rows=rows[:limit];next_cursor=None
    if more:next_cursor={'format':'WORLD_FACT_CURSOR_V1','target':target,'observed_through':scope.observed_through,'scope_sha256':scope.fingerprint,'after_key':rows[-1]['__fact_key']}
    return {'table':table,'role':role,'columns':columns,'filters':filters,'records':[_record(r,columns,observed) for r in rows],'has_more':more,'next_cursor':next_cursor,'observation_scope':scope.metadata(),
        'selection_scope':'All matching successful row observations in the fixed acquisition ledger; not a latest-state merge or proof of complete Native coverage',
        'null_semantics':'NULL means absent/unproved as documented by field metadata; use explicit is_null/not_null predicates'}


def export_filtered_facts(path,new_output_directory,table,*,columns=None,filters=None,max_rows=10000,role='GM'):
    if type(max_rows) is not int or not 1<=max_rows<=10000000:raise ValueError('export max_rows must be 1..10000000')
    spec,columns,filters,source,clauses,args,projection,observed=_plan(table,columns,filters,role)
    if current_scope() is None:
        with observed_as_of(path,datetime.now(timezone.utc).isoformat()):return export_filtered_facts(path,new_output_directory,table,columns=columns,filters=filters,max_rows=max_rows,role=role)
    scope=current_scope();where=' WHERE '+' AND '.join(clauses) if clauses else '';out=Path(new_output_directory).resolve()
    with closing(query_connection(path,True)) as conn:
        conn.execute('BEGIN');count=conn.execute('SELECT count(*)'+source+where,args).fetchone()[0]
        if count>max_rows:raise ValueError(f'filtered export needs max_rows >= {count}; no silent truncation')
        out.mkdir(parents=True,exist_ok=False)
        try:
            digest=hashlib.sha256();written=0;byte_count=0;pending=out/'facts.pending.jsonl'
            with pending.open('xb') as stream:
                for row in conn.execute('SELECT '+projection+source+where+' ORDER BY t.'+ident(spec.key),args):
                    line=(json.dumps(_record(row,columns,observed),ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n').encode('utf-8');stream.write(line);digest.update(line);byte_count+=len(line);written+=1
                stream.flush();os.fsync(stream.fileno())
            if written!=count:raise RuntimeError('filtered export count changed inside read transaction')
            pending.rename(out/'facts.jsonl')
            catalog=fact_fields(table,role=role);catalog['columns']=[c for c in catalog['columns'] if c['name'] in columns]
            manifest={'format':'WORLD_FILTERED_FACT_EXPORT_V1','status':'COMPLETE_PUBLIC_FACT_EXPORT','table':table,'role':role,'columns':columns,'filters':filters,'rows':written,'file':'facts.jsonl','sha256':digest.hexdigest(),'bytes':byte_count,
                'observation_scope':scope.metadata(),'field_metadata':catalog,'selection_scope':'Matching row observations only; no synthetic history, latest-state merge or inferred missing fields','game_access':False}
            with (out/'manifest.pending.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(manifest,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
            (out/'manifest.pending.json').rename(out/'manifest.json')
            return {**manifest,'path':str(out)}
        except BaseException as error:
            with (out/'failure.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump({'status':'INCOMPLETE_EXPORT','error_type':type(error).__name__,'complete_manifest_required':True},stream)
            raise
