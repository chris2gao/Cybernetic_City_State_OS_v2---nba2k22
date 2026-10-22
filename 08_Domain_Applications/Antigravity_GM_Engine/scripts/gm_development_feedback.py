"""Explicit offline M4 engineering issue import, triage and small handoff reports."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from gm_core import development_feedback as feedback
from gm_core.workbench_common import export_files, now
from gm_workbench.store import Store


def read_input(path):
    if path is None:
        raise ValueError('EXPLICIT_INPUT_FILE_REQUIRED')
    if path.stat().st_size > 24000:
        raise ValueError('INPUT_24KB_MAX_REFERENCE_LARGE_REPORTS')
    return json.loads(path.read_text(encoding='utf-8-sig'))


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('ingest', 'list', 'show', 'triage', 'export', 'readiness'))
    p.add_argument('--workbench', type=Path, default=ROOT/'_exports/dev10_m3/gm_workbench.sqlite')
    p.add_argument('--input', type=Path)
    p.add_argument('--issue'); p.add_argument('--event-key')
    p.add_argument('--expected-revision', type=int)
    p.add_argument('--status', choices=feedback.STATUSES)
    p.add_argument('--severity', choices=('P0', 'P1', 'P2'))
    p.add_argument('--category', choices=feedback.CATEGORIES)
    p.add_argument('--career'); p.add_argument('--capability')
    p.add_argument('--limit', type=int, default=10); p.add_argument('--cursor')
    p.add_argument('--output', type=Path)
    p.add_argument('--readiness-evidence', type=Path, default=ROOT/'config/m4_readiness_evidence.json')
    return p


def render_current(index, details, ready):
    lines = ['# M4 开发问题交接索引', '',
        'ENGINEERING_FEEDBACK_ONLY / GM_V4_NOT_ENABLED', '',
        '这是本次显式导出的有界问题页，不是实时监控或全部历史。详细原始事件保留在本地派生工作台；本目录仅含小型引用和摘要。', '',
        '下次由玩家主动触发 Web DEVELOPMENT 时先读本页，再按证据提出最小研究/实现范围、成本与任务书草案，等待玩家批准。导入、分流、建议负责人、导出均不授权开发或游戏写入。', '',
        '工程状态：'+ready['delivery_status']+'；正式GM：'+ready['gm_status']+'。',
        '待完成门：'+', '.join(ready['blocked_conditions'])+'。',
        '准备状态依据日期：'+ready['as_of']+'；完整分项见 [readiness.json](readiness.json)。', '',
        '问题页：'+str(index['row_count'])+' 项；全池按状态/严重程度计数：'+feedback.encoded(index['counts'])+'。',
        '还有下一页：'+str(index['truncated'])+'。游标与筛选见 [index.json](index.json)，用CLI继续查询/导出。', '']
    for item in details:
        issue = item['issue']; ident = issue['issue_id']
        lines.extend(['## '+ident+' · '+issue['severity']+' / '+issue['status'], '',
            issue['title'], '',
            '- 类别 / 证据等级：'+issue['category']+' / '+issue['latest_confidence']+'（'+issue['finding_kind']+'）。',
            '- 来源：'+feedback.encoded(issue['latest_source'])+'；作用域：'+feedback.encoded(issue['scope'])+'。',
            '- 首次 / 最近：'+issue['first_seen']+' / '+issue['last_seen']+'；独立事件数：'+str(issue['occurrences'])+'；修订：'+str(issue['revision'])+'。',
            '- 能力 / 影响：'+issue['affected_capability']+'；'+issue['actual'],
            '- 预期：'+issue['expected'],
            '- 最小复现或阅读条件：'+'；'.join(issue['repro_steps']),
            '- 已知限制：'+'；'.join(issue['known_limits']),
            '- 建议负责人：'+issue['proposed_owner']+'；下次触发：'+issue['next_review_trigger'],
            '- 玩家决定：'+(issue['player_decision_ref'] or 'NOT_RECORDED'),
            '- 原始证据：'+'；'.join('['+ref+']('+ (ref if ref.startswith('https://') else '../../'+ref) +')' for ref in issue['latest_evidence_refs']) if issue['latest_evidence_refs'] else '- 原始证据：UNKNOWN / RESEARCH_ONLY',
            '- [详情及最近历史]('+ident+'.json)。完整历史通过 `show --issue '+ident+'` 分页读取。', ''])
        if issue.get('roadmap_note'):
            lines.extend(['规划指针：'+issue['roadmap_note'], ''])
        if issue.get('latest_triage'):
            lines.extend(['最近人工处理：'+issue['latest_triage']['reason'], ''])
    return '\n'.join(lines)+'\n'


def run(a):
    if a.action == 'readiness':
        issue6 = None
        if a.workbench.exists():
            with Store(a.workbench, readonly=True) as store:
                initialized = store.c.execute("SELECT 1 FROM sqlite_master WHERE name='development_issues'").fetchone()
                if initialized:
                    issue6 = store.development_issue6()
        return feedback.readiness(read_input(a.readiness_evidence), issue6)
    writing = a.action in ('ingest', 'triage')
    with Store(a.workbench, readonly=not writing) as store:
        if a.action == 'ingest':
            return store.ingest_development(read_input(a.input))
        if a.action == 'triage':
            if not a.issue:
                raise ValueError('ISSUE_REQUIRED')
            return store.triage_development(a.issue, read_input(a.input), a.expected_revision)
        if a.action == 'show':
            if not a.issue:
                raise ValueError('ISSUE_REQUIRED')
            if a.event_key:
                return dict(issue_id=a.issue, event=store.development_event(a.issue, a.event_key), execution_authorized=False)
            return dict(issue=store.development_issue(a.issue), history=store.development_history(a.issue, a.limit, a.cursor),
                execution_authorized=False)
        filters = {key:value for key,value in dict(status=a.status, severity=a.severity, category=a.category,
            career_id=a.career, capability=a.capability).items() if value is not None}
        if a.action == 'export' and (a.output is None or not 1 <= a.limit <= 20):
            raise ValueError('NEW_EXPORT_DIRECTORY_AND_LIMIT_1_TO_20_REQUIRED')
        result = store.list_development(filters, a.limit, a.cursor)
        result.update(version=feedback.VERSION, filters=filters, counts=store.development_counts(),
            generated_at=now(), publication='NOT_REQUESTED', status='ENGINEERING_FEEDBACK_ONLY')
        if a.action == 'list':
            return result
        ready = feedback.readiness(read_input(a.readiness_evidence), store.development_issue6())
        details = [dict(issue=store.development_issue(row['issue_id']), history=store.development_history(row['issue_id'], 3)) for row in result['rows']]
        files = {'index.json':result, 'readiness.json':ready}
        files.update({item['issue']['issue_id']+'.json':item for item in details})
        exported = export_files(a.output, files)
        (a.output/'CURRENT.md').write_text(render_current(result, details, ready), encoding='utf-8', newline='\n')
        exported['files'].append('CURRENT.md')
        return dict(**exported, row_count=result['row_count'], next_cursor=result['next_cursor'],
            truncated=result['truncated'], publication='NOT_REQUESTED', gm_status='GM_V4_NOT_ENABLED')


def main():
    try:
        result = run(parser().parse_args())
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    except (ValueError, sqlite3.Error, OSError) as exc:
        message = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        print(json.dumps(dict(status='ERROR', error=message, execution_authorized=False), ensure_ascii=False))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
