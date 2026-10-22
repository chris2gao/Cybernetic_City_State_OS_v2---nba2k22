"""One bounded local M02 CLI check. Never captures, publishes or opens the game."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
CAREER = 'mc_haliburton_2021'
BATCH = '2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2'


def call(script, *args):
    result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts'/script), *map(str, args)],
                            cwd=ROOT, capture_output=True, encoding='utf-8', env=environment())
    if result.returncode:
        raise RuntimeError(result.stdout[:1500]+result.stderr[:1000])
    return json.loads(result.stdout)


def environment():
    import os
    return dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')


def main():
    output = ROOT/'_exports/m2_acceptance'/uuid4().hex
    output.mkdir(parents=True)
    binding_args = ['--career', CAREER, '--batch', BATCH]
    search = call('gm_knowledge.py', 'search', '--tag', 'pick_and_roll')
    pnr = call('gm_knowledge.py', 'show', '--card', 'PNR_PRIMARY', *binding_args)
    drop = call('gm_knowledge.py', 'show', '--card', 'DROP_CONCEPT', *binding_args)
    missing = call('gm_knowledge.py', 'show', '--card', 'PNR_PRIMARY')
    franchise = call('gm_knowledge.py', 'franchise', '--team', 'SAS')
    candidates = call('gm_strategy.py', 'init', *binding_args, '--output', output/'candidates')
    workbench = output/'gm_workbench.sqlite'
    saved = call('gm_strategy.py', 'save', '--input', output/'candidates/SAS.json', '--expected-revision', 0, '--workbench', workbench)
    shown = call('gm_strategy.py', 'show', '--career', CAREER, '--team', 'SAS', '--workbench', workbench)
    exported = call('gm_strategy.py', 'export', '--career', CAREER, '--workbench', workbench, '--output', output/'export')
    assert search['cards'][0]['card_id'] == 'PNR_PRIMARY'
    assert pnr['native_resolution'][0]['resolution'] == 'SAME_BATCH_NATIVE_ENUM'
    assert all(r['resolution'] == 'HYPOTHESIS_CANDIDATE' for r in drop['native_resolution'])
    assert missing['native_resolution'][0]['resolution'] == 'UNAVAILABLE'
    assert candidates['candidate_count'] == 30 and candidates['assessed_count'] == 0
    assert shown['status'] == 'UNASSESSED' and shown['current_actions'] == []
    assert franchise['current_game_strategy'] == 'UNASSESSED'
    assert saved['state']['revision'] == 1 and exported['publication'] == 'NOT_REQUESTED'
    receipt = dict(status='PASS_LOCAL_STATIC_M02', checked_at=datetime.now(timezone.utc).isoformat(),
        source_binding=pnr['source_binding'], search_matches=search['total_matches'],
        native_direct=pnr['native_resolution'], drop_hypotheses=drop['native_resolution'],
        no_batch_resolution=missing['native_resolution'][0]['resolution'],
        candidates=30, assessed_teams=0, local_unassessed_state_saved_and_read=True,
        strategy_export='ANALYSIS_ONLY_NOT_PUBLISHED',
        web_connections='DEFERRED_BY_PLAYER', game_access='NOT_RUN')
    (output/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=receipt['status'], receipt=str(output/'receipt.json')),ensure_ascii=False))


if __name__ == '__main__':
    main()
