"""Shared analysis-only contracts and bounded workbench presentation."""
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def same_source(a,b):
    # A later latest pointer may change CURRENT to HISTORICAL without changing this batch.
    return all(a.get(k)==b.get(k) for k in ('career_id','snapshot_id','batch_id','game_date','data_updated_at','audit','query_version'))


def reject_authority(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.casefold() in {'approved', 'approved_by', 'player_approved', 'executed',
                    'execution_receipt', 'execution_receipt_ref', 'approval_status',
                    'execution_authorized', 'write_authority', 'terms_digest', 'batch_digest'}:
                raise ValueError('CALLER_CANNOT_DECLARE_AUTHORITY_OR_GENERATED_RECEIPTS:'+key)
            if (key == 'status' or key.endswith('_status')) and value in ('APPROVED', 'EXECUTED', 'FORMAL_ENABLED'):
                raise ValueError('ANALYSIS_ONLY_STATUS_REQUIRED')
            reject_authority(value)
    elif isinstance(obj, list):
        for value in obj:
            reject_authority(value)


def require(obj, keys):
    if not isinstance(obj, dict) or any(k not in obj for k in keys):
        raise ValueError('REQUIRED_FIELDS:'+','.join(keys))
    return obj


def text_required(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('TEXT_REQUIRED:'+label)


def page(rows, binding, limit=20, cursor=None, budget=17000):
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ValueError('LIMIT_1_TO_50')
    fingerprint = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    offset = 0
    if cursor:
        try:
            token = json.loads(base64.urlsafe_b64decode(cursor))
            offset = token['offset']
            if token['query'] != fingerprint or type(offset) is not int or not 0 <= offset <= len(rows):
                raise ValueError()
        except Exception as exc:
            raise ValueError('STALE_OR_MIXED_CURSOR') from exc
    result = []
    for row in rows[offset:offset+limit]:
        if len(json.dumps(result+[row], ensure_ascii=False).encode()) > budget:
            if not result:
                raise ValueError('ROW_EXCEEDS_BUDGET_REQUEST_SMALLER_PROJECTION')
            break
        result.append(row)
    end = offset+len(result)
    token = base64.urlsafe_b64encode(json.dumps(dict(query=fingerprint, offset=end)).encode()).decode() if end < len(rows) else None
    return dict(rows=result, row_count=len(result), total_rows=len(rows), next_cursor=token, truncated=token is not None)


def export_files(output, files):
    output = Path(output).resolve()
    if any(p.casefold() in {'published', 'saves', 'query_snapshots', 'seasons'} for p in output.parts):
        raise ValueError('EXPORT_CANNOT_TARGET_FACTS')
    if output.exists():
        raise ValueError('EXPORT_DIRECTORY_EXISTS')
    output.mkdir(parents=True)
    for name, obj in files.items():
        (output/name).write_text(json.dumps(obj, ensure_ascii=False, allow_nan=False, indent=2)+'\n', encoding='utf-8')
    return dict(status='EXPORTED_ANALYSIS_ONLY', output=str(output), files=list(files))
