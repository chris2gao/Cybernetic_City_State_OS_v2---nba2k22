"""Three explicit verification checks; no implicit online or process access."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[4]
RUN=REPO/'01_os/07_content/_runs/run-20261023-native-atlas-codex-triage-01'
sys.path.insert(0,str(ROOT))
import adjudicate as a

def regressions():
    return subprocess.call([sys.executable,'-B','-m','unittest','discover','-s',str(ROOT),'-p','test_adjudication.py','-v'])

def static_replay():
    from static_extract import extract
    image=os.environ.get('NBA2K22_TRIAGE_STATIC_IMAGE')
    if not image:
        raise ValueError('NBA2K22_TRIAGE_STATIC_IMAGE must explicitly name the authorized disk image')
    expected=a.load('static_evidence.json')
    actual=extract(image)
    if actual!=expected:
        raise ValueError('Image, extracted bytes, native resource references or dispatch differs from pinned static evidence')
    for slot,term in {9:'College',22:'Playbook',35:'CustomUniform',39:'Record',42:'Draft',61:'DeadCap',24:'PlayerStat'}.items():
        gs=[g for g in actual['getters'] if g['slot']==slot]
        if not any(term in r['value'] for g in gs for r in g['resources']):
            raise ValueError(f'Static native name missing for {slot}')
    print('PASS disk image hash, bounded getter code/resources and all 68 switch targets replayed; no live process read')
    return 0

def delivery():
    for name in ['README.md','REVERSE_ENGINEERING.md','GEMINI_NEXT_ROUND.md','ingredient_gaps.json','next_round_plan.json','adjudication_75.json','static_evidence.json','source_manifest.json']:
        if not (ROOT/name).is_file():raise ValueError(f'Missing deliverable {name}')
    plan=a.load('next_round_plan.json')
    if plan['authorization_status']!='PROPOSAL_NOT_LIVE_AUTHORIZATION':raise ValueError('Plan must not self-authorize live reads')
    for phase in plan['phases']:
        for key in ['rank','id','roles','objective','steps','evidence_required','envelope','positive_controls','negative_controls','stop_conditions']:
            if not phase.get(key):raise ValueError(f'Missing {key}')
        if phase['envelope']['access_mode'] not in ['STATIC_ONLY','READ_ONLY_PROPOSED']:
            raise ValueError('Invalid follow-up access mode')
    gaps=a.load('ingredient_gaps.json')
    if set(gaps['roles'])!={'Player','GM','Coach'}:raise ValueError('Incomplete consumer roles')
    if any(not row.get('blockers') for rows in gaps['roles'].values() for row in rows):raise ValueError('Unsupported complete ingredient claim')
    paths=subprocess.check_output(['git','diff','--name-only','-z','407e2134bd2f595477099b2c6e3484c818059fd9'],cwd=REPO).decode('utf-8').split('\0')
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=REPO).decode('utf-8').split('\0')
    prefixes=[ROOT.relative_to(REPO).as_posix()+'/',RUN.relative_to(REPO).as_posix()+'/']
    for p in filter(None,paths+untracked):
        if not any(p.startswith(prefix) for prefix in prefixes):raise ValueError(f'Out-of-scope path {p}')
    subprocess.run(['git','diff','--check'],cwd=REPO,check=True)
    issue=json.loads((RUN/'issue_snapshot.json').read_text(encoding='utf-8'))
    if issue['number']!=1 or 'Slot 39' not in issue['body']:raise ValueError('Issue source not preserved')
    print('PASS deliverable contracts, consumer gaps, proposed envelopes and actual path scope; not independent acceptance')
    return 0

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('check',choices=['ADJUDICATION_AND_REGRESSIONS','STATIC_EVIDENCE_REPLAY','DELIVERY_AND_SCOPE'])
    check=parser.parse_args().check
    sys.exit({'ADJUDICATION_AND_REGRESSIONS':regressions,'STATIC_EVIDENCE_REPLAY':static_replay,'DELIVERY_AND_SCOPE':delivery}[check]())
