"""M4 engineering evidence contracts. No basketball evaluation or game access."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import PurePosixPath
import re
from urllib.parse import urlsplit

from .workbench_common import now, reject_authority, require

VERSION = 'M4_SYSTEM_EVOLUTION_V1'
STATUSES = ('OPEN', 'TRIAGED', 'DEFERRED', 'RESOLVED', 'DISMISSED')
CATEGORIES = (
    'DATA_CONSUMER_UNREADABLE', 'SOURCE_SEMANTICS_CONFLICT', 'SOURCE_STALE_OR_MISSING',
    'DECISION_PACKET_MISSING_OR_STALE', 'NATIVE_FIELD_UNAVAILABLE',
    'EXECUTION_CONTRACT_FAILURE', 'OPERATIONS_HANDOFF_FAILURE',
    'DEVELOPMENT_FEATURE_CANDIDATE', 'OTHER_VERIFIED_ENGINEERING_ISSUE')
STAGES = ('CAPTURE', 'ACCESS', 'ANALYTICS', 'GM_INTERFACE', 'APPROVAL', 'EXECUTION', 'HANDOFF', 'MANUAL_RESEARCH')
CONFIDENCE = ('UNKNOWN', 'RESEARCH', 'STATIC_REPORT', 'REPRODUCED_SYNTHETIC', 'OBSERVED_PRODUCTION')
EVENT_KEYS = ('event_id', 'occurred_at', 'category', 'title', 'root_cause_key', 'scope', 'source',
              'affected_capability', 'evidence_refs', 'repro_steps', 'actual', 'expected', 'confidence',
              'severity', 'proposed_owner', 'next_review_trigger', 'related_issue_ids', 'known_limits')


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(',', ':'))


def fingerprint(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def text(value, label, maximum=800, empty=False):
    if not isinstance(value, str) or len(value) > maximum or (not empty and not value.strip()):
        raise ValueError('BOUNDED_TEXT_REQUIRED:'+label)
    # Reports contain references and concise descriptions, never private paths or native dumps.
    if re.search(r'(?i)(?:(?<![a-z0-9])[a-z]:[\\/]|/(?:Users|home)/|0x[0-9a-f]{8,}\b|\bBearer\s+|\b(?:ghp_|github_pat_)|-----BEGIN .*PRIVATE KEY|(?:^|[/\\])\.env(?:\b|$))', value):
        raise ValueError('REFERENCE_ONLY_NO_PRIVATE_PATH_ADDRESS_OR_CREDENTIAL:'+label)
    return value


def reference(value):
    text(value, 'evidence_ref', 600)
    url = urlsplit(value)
    if url.scheme:
        if url.scheme != 'https' or url.hostname != 'github.com' or url.username or url.password or url.query:
            raise ValueError('GITHUB_OR_REPOSITORY_REFERENCE_REQUIRED')
    else:
        path = PurePosixPath(value.split('#', 1)[0])
        if path.is_absolute() or '..' in path.parts or '\\' in value:
            raise ValueError('REPOSITORY_RELATIVE_REFERENCE_REQUIRED')
    return value


def strings(values, label, count=8, maximum=800, refs=False):
    if not isinstance(values, list) or len(values) > count:
        raise ValueError('BOUNDED_LIST_REQUIRED:'+label)
    return list(dict.fromkeys(reference(v) if refs else text(v, label, maximum) for v in values))


def event(payload):
    reject_authority(payload)
    require(payload, EVENT_KEYS)
    if set(payload) - set(EVENT_KEYS) - {'status', 'player_decision_ref', 'roadmap_note'}:
        raise ValueError('UNKNOWN_DEVELOPMENT_EVENT_FIELDS')
    result = deepcopy(payload)
    for name in ('event_id', 'title', 'root_cause_key', 'affected_capability', 'proposed_owner'):
        text(result[name], name, 200)
    for name in ('actual', 'expected', 'next_review_trigger'):
        text(result[name], name)
    stamp = datetime.fromisoformat(result['occurred_at'].replace('Z', '+00:00'))
    if stamp.tzinfo is None:
        raise ValueError('TIMEZONE_REQUIRED')
    result['occurred_at'] = stamp.astimezone(timezone.utc).isoformat()
    if result['category'] not in CATEGORIES or result['confidence'] not in CONFIDENCE or result['severity'] not in ('P0', 'P1', 'P2'):
        raise ValueError('INVALID_CATEGORY_CONFIDENCE_OR_SEVERITY')
    scope = result['scope']; require(scope, ('kind',))
    if set(scope) - {'kind', 'career_id', 'save_instance_id', 'identity_key'} or scope['kind'] not in ('SYSTEM', 'CAREER', 'IDENTITY'):
        raise ValueError('EXPLICIT_ISSUE_SCOPE_REQUIRED')
    if scope['kind'] == 'SYSTEM' and set(scope) != {'kind'}:
        raise ValueError('SYSTEM_SCOPE_HAS_NO_SAVE_IDENTITY')
    if scope['kind'] != 'SYSTEM':
        require(scope, ('career_id',)); text(scope['career_id'], 'scope.career_id', 160)
    if scope['kind'] == 'IDENTITY':
        require(scope, ('save_instance_id', 'identity_key'))
    for key, value in scope.items():
        text(value, 'scope.'+key, 200)
    source = result['source']; require(source, ('source_stage', 'producer'))
    if set(source) - {'source_stage', 'producer', 'career_id', 'save_instance_id', 'generation_id', 'source_batch', 'run_id', 'error_code', 'code_version'}:
        raise ValueError('REFERENCE_ONLY_SOURCE_CONTEXT_REQUIRED')
    if source['source_stage'] not in STAGES:
        raise ValueError('INVALID_SOURCE_STAGE')
    for key, value in source.items():
        text(value, 'source.'+key, 200)
    if scope.get('career_id') and source.get('career_id') != scope['career_id']:
        raise ValueError('ISSUE_AND_EVENT_CAREER_MISMATCH')
    if scope.get('save_instance_id') and source.get('save_instance_id') != scope['save_instance_id']:
        raise ValueError('ISSUE_AND_EVENT_INSTANCE_MISMATCH')
    for key in ('evidence_refs', 'repro_steps', 'related_issue_ids', 'known_limits'):
        result[key] = strings(result[key], key, maximum=400, refs=key == 'evidence_refs')
    if not result['evidence_refs']:
        result['confidence'] = 'UNKNOWN' if result['confidence'] != 'RESEARCH' else 'RESEARCH'
    result['finding_kind'] = 'RESEARCH' if result['confidence'] in ('UNKNOWN', 'RESEARCH') or result['category'] == 'DEVELOPMENT_FEATURE_CANDIDATE' else 'ENGINEERING_EVIDENCE'
    result['status'] = result.get('status', 'OPEN')
    if result['status'] not in ('OPEN', 'DEFERRED'):
        raise ValueError('INGEST_CANNOT_RESOLVE_OR_APPROVE')
    result['player_decision_ref'] = text(result.get('player_decision_ref', ''), 'player_decision_ref', empty=True)
    if result['status'] == 'DEFERRED' and not result['player_decision_ref']:
        raise ValueError('DEFERRED_REQUIRES_PLAYER_DECISION_REF')
    result['roadmap_note'] = text(result.get('roadmap_note', ''), 'roadmap_note', empty=True)
    result['fingerprint'] = fingerprint({k:result[k] for k in ('category', 'root_cause_key', 'scope', 'affected_capability')})
    # SYSTEM already denotes the global namespace; retain its existing persisted keys.
    event_identity = [source['producer'], result['event_id']]
    if scope['kind'] != 'SYSTEM':
        event_identity.append(scope)
    result['event_key'] = 'ingest:'+fingerprint(event_identity)
    result['issue_id'] = 'DEV-'+result['fingerprint'][:20]
    result['evidence_interpretation'] = 'OPERATOR_SUPPLIED_REFERENCES_NOT_M4_LIVE_VERIFICATION'
    if len(encoded(result).encode()) > 14000:
        raise ValueError('EVENT_TOO_LARGE_USE_REFERENCES')
    return result


def triage(payload):
    reject_authority(payload)
    require(payload, ('status', 'reason', 'player_decision_ref'))
    if set(payload) - {'status', 'reason', 'player_decision_ref', 'evidence_refs', 'severity', 'proposed_owner', 'next_review_trigger'}:
        raise ValueError('UNKNOWN_TRIAGE_FIELDS')
    result = deepcopy(payload)
    if result['status'] not in STATUSES:
        raise ValueError('INVALID_DEVELOPMENT_STATUS')
    text(result['reason'], 'triage_reason')
    text(result['player_decision_ref'], 'actual_player_decision_reference')
    result['evidence_refs'] = strings(result.get('evidence_refs', []), 'evidence_refs', refs=True)
    if result['status'] == 'RESOLVED' and not result['evidence_refs']:
        raise ValueError('RESOLVED_REQUIRES_FIX_EVIDENCE')
    if 'severity' in result and result['severity'] not in ('P0', 'P1', 'P2'):
        raise ValueError('INVALID_SEVERITY')
    for key in ('proposed_owner', 'next_review_trigger'):
        if key in result:
            text(result[key], key)
    return result


def brief(issue):
    return {k:issue[k] for k in ('issue_id', 'revision', 'category', 'title', 'severity', 'status',
        'finding_kind', 'first_seen', 'last_seen', 'occurrences', 'proposed_owner')}


def readiness(evidence, issue6=None):
    """Describe a dated evidence manifest. Never infer Web or production acceptance from code."""
    reject_authority(evidence)
    require(evidence, ('as_of', 'engineering', 'pr4', 'gates'))
    text(evidence['as_of'], 'as_of', 120)
    engineering = {}
    for name in ('M0', 'M1', 'M2', 'M3A', 'M3B', 'M3_T', 'M4'):
        entry = evidence['engineering'].get(name, {})
        engineering[name] = readiness_entry(entry, ('COMPLETE_MAIN', 'COMPLETE_BRANCH', 'PENDING'))
    pr = evidence['pr4']
    checked_pr = readiness_entry(pr, ('MERGED', 'OPEN', 'UNKNOWN'))
    if checked_pr['status'] == 'MERGED':
        if not re.fullmatch(r'[0-9a-f]{40}', pr.get('merge_commit', '')):
            raise ValueError('MERGED_PR_REQUIRES_COMMIT')
        checked_pr['merge_commit'] = pr['merge_commit']
    gates = {}
    allowed = {
        'web_DEVELOPMENT': ('PENDING', 'PLAYER_CONFIRMED'),
        'web_ANALYTICS': ('PENDING', 'PLAYER_CONFIRMED'),
        'web_GM': ('PENDING', 'PLAYER_CONFIRMED'),
        'sanitized_production_capture': ('PENDING', 'OBSERVED_SANITIZED'),
        'gm_consumed_sanitized_batch': ('PENDING', 'CONSUMED'),
        'actual_30_team_research': ('UNASSESSED', 'ASSESSED_30'),
        'GSW_SAS_OKC_no_write_rehearsal': ('PENDING', 'EVIDENCED'),
        'issue6_fix': ('OPEN', 'DEFERRED', 'RESOLVED'),
        'BPTI_before_new_save': ('PENDING', 'ENGINEERING_EVIDENCED'),
        'postseason_capture_interface': ('PENDING', 'IMPLEMENTED'),
        'dual_engine_calibrator_interface': ('PENDING', 'IMPLEMENTED'),
        'player_V4_switch_and_new_save': ('PENDING', 'PLAYER_CONFIRMED'),
    }
    for name, statuses in allowed.items():
        gates[name] = readiness_entry(evidence['gates'].get(name, {}), statuses)
    blocked = [name for name, e in gates.items() if e['status'] != allowed[name][-1]]
    blocked.extend(name+'_engineering_integration' for name, e in engineering.items() if e['status'] != 'COMPLETE_MAIN')
    if checked_pr['status'] != 'MERGED':
        blocked.append('PR4_MAIN_MERGE')
    # A newer local issue record cannot silently override this dated readiness evidence.
    if issue6 and issue6['status'] != 'RESOLVED' and 'issue6_fix' not in blocked:
        blocked.append('issue6_local_record_not_resolved')
    return dict(version=VERSION, as_of=evidence['as_of'], generated_at=now(),
        engineering=engineering, pr4=checked_pr, gates=gates, blocked_conditions=blocked,
        issue6_local_record=brief(issue6) if issue6 else 'NOT_IMPORTED',
        engineering_status='M4_ENGINEERING_COMPLETE' if engineering['M4']['status'].startswith('COMPLETE_') else 'PENDING',
        delivery_status='M4_ENGINEERING_COMPLETE_AWAITING_PLAYER' if engineering['M4']['status'].startswith('COMPLETE_') else 'PENDING',
        gm_status='GM_V4_NOT_ENABLED', activation='PLAYER_SEPARATE_TASK_REQUIRED_NO_AUTOMATIC_SWITCH',
        evidence_basis='DATED_REFERENCES_NOT_LIVE_WEB_GAME_OR_GITHUB_PROBES',
        scope='ENGINEERING_ONLY_NO_TEAM_PERFORMANCE_OR_SIMULATION_CALIBRATION')


def readiness_entry(entry, statuses):
    default = 'PENDING' if 'PENDING' in statuses else 'UNKNOWN' if 'UNKNOWN' in statuses else statuses[0]
    status = entry.get('status', default)
    if status not in statuses:
        raise ValueError('INVALID_READINESS_STATUS')
    refs = strings(entry.get('evidence_refs', []), 'readiness_refs', refs=True)
    if status not in ('PENDING', 'UNASSESSED', 'UNKNOWN', 'OPEN', 'DEFERRED') and not refs:
        raise ValueError('READINESS_CLAIM_REQUIRES_EVIDENCE')
    return dict(status=status, evidence_refs=refs, notes=text(entry.get('notes', ''), 'readiness_notes', empty=True))
