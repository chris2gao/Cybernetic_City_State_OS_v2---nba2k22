"""Build B2/B3 references from checked-in research and the existing static registry.

No game/source DB access. This generator creates knowledge, never native actions.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from gm_core.bpti import VERSION, SYSTEM_IDS, publication_upper_bound
from gm_state_io.registry import Registry

RESEARCH = 'docs/development_research/'
R2 = RESEARCH + 'BPTI_R2_30_FRANCHISE_IDENTITIES_AND_EVOLUTION_DEEP_RESEARCH_V2.md'
EVIDENCE = 'docs/development_reviews/BPTI_PACKAGE_B_HISTORICAL_EVIDENCE.md'
BASE = '80459b4ad7c2047e2479b0cb9b1140bfbf77e6ea'
URL = 'https://github.com/chris2gao/nba2k22-gm-engine/blob/' + BASE + '/'


def locator(document, line=1, end=None):
    return dict(document=document, line_start=line, line_end=end or line)


def claim(cid, statement, source_ids, origin, *, domain='PROJECT_NATIVE_INTERFACE',
          status='VERIFIED', since='2026-10-20', until=None, **extra):
    return dict(claim_id=cid, domain=domain, statement=statement, source_ids=source_ids,
                origin=origin, historical_period='PROJECT_METADATA' if domain == 'PROJECT_NATIVE_INTERFACE' else 'PRE_2021_REFERENCE',
                fact_valid_from=since, fact_valid_to=until or since, knowledge_available_from=until or since,
                retrospective_only=domain != 'PROJECT_NATIVE_INTERFACE', claim_status=status,
                evidence_level='REVIEWED_PROJECT_INTERFACE' if status == 'VERIFIED' else 'ARCHIVED_SUPPORTED_INTERPRETATION',
                counterevidence=['Field availability is not a certified basketball effect.'] if domain == 'PROJECT_NATIVE_INTERFACE' else
                ['Historical reference only; not current-save personnel, organizational continuity or tactical outcomes.'],
                design_relevance='Reference direction only; no native plan or player approval.',
                verification_ref=origin['document'] if status == 'VERIFIED' else None, **extra)


def build():
    index = json.loads((ROOT / 'web_gm/knowledge/bpti/research_source_index.json').read_text(encoding='utf-8'))
    source_map = {s['source_id']: s for s in index['sources']}
    sources, claims, bindings = [], [], []
    interface_docs = {
        'B2-COACH': ('web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md', 76, 99),
        'B2-PLAYER': ('src/gm_state_io/registry.py', 32, 54),
        'B2-BOOK': ('docs/GM_SHARED_PLAY_POOL_V1.md', 35, 48),
        'B2-DEFENSE': ('docs/DEV14_STATE_IO_RUNBOOK.md', 24, 37),
        'B2-TRAINING': ('src/gm_state_io/registry.py', 83, 99),
        'B2-BOUNDARY': ('web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md', 76, 118),
    }
    for sid, (doc, start, end) in interface_docs.items():
        sources.append(dict(source_id=sid, title=sid + ' existing project interface', publication_date='2026-10-20',
                            historical_period='NBA2K22_PC_CURRENT_GEN_PROJECT_INTERFACE', url=URL + doc,
                            origin=locator(doc, start, end), source_status='VERIFIED', verification_ref=doc))
        claims.append(claim(sid + '-C', 'Existing reviewed interface and its documented restrictions; gameplay effects remain unknown.',
                            [sid], locator(doc, start, end)))
    registry = Registry()
    groups = {
        'SYSTEM': ['coach.PreferredSystem', 'coach.ActiveSystem'],
        'COACH': [k for k, f in registry.fields.items() if k.startswith('coach.') and f['gm_enabled']
                  and 'Freelance' not in k and k not in {'coach.PreferredSystem', 'coach.ActiveSystem', 'coach.Tempo'}],
        'FREELANCE': [k for k in registry.fields if k.startswith('coach.Freelance')],
        'PLAYTYPE': [k for k in registry.fields if k.startswith('playtype.')],
        'TENDENCY': [k for k, f in registry.fields.items() if k.startswith('tendency.') and f['gm_enabled']],
        'PERSONAL': [k for k, f in registry.fields.items() if k.startswith('personal.') and f['gm_enabled']],
        'TRAINING': [k for k, f in registry.fields.items() if k.startswith('training.') and f['gm_enabled']],
        'ROTATION': ['rotation.intangibles', 'coach.BenchDepth', 'coach.BenchUtilization'],
        'BOOK': ['playbook.slot'],
    }
    intents = {
        'MOTION_READ_REACT': '移动射手、连接者与切入者传递第一优势，防守交换后保留第二侧阅读。',
        'TRIANGLE_INSIDE_OUT': '强侧三角与低位入口牵动防守，受阻时保留弱侧接应。',
        'SPREAD_PICK_AND_ROLL': '区分持球创造、顺下/外弹和短接应角色，阅读不同掩护覆盖。',
        'ISOLATION_MIDRANGE_CREATION': '保留错位与中距离创造权，并为协防到来后的二次出球留空间。',
        'POST_HIGH_LOW': '低位威胁配合高位接应，绕前或包夹时寻找另一入口。',
        'POINT_CENTER_ELBOW_HUB': '大个策应连接手递手、切入和第二次挡拆；不假定有专属原生开关。',
        'TRANSITION_EARLY_OFFENSE': '取得球权后争取早期优势，未成时进入半场第二方案。',
        'DEFENSE_FIRST_RIM_PROTECTION': '先保护篮下并延伸补防链，不把护框价值只理解为盖帽。',
        'SWITCHABLE_PRESSURE_DEFENSE': '根据实际对位换防/施压，并保留错位代价及反制。',
        'ADAPTIVE_MULTIPLE_SYSTEMS': '主方案被克制时比较副体系与机会成本，限玩家触发的赛前配置。',
    }
    qualifications = {
        'SYSTEM': '八种原生体系均可研究：BALANCED/GRIT_AND_GRIND/PACE_AND_SPACE/PERIMETER/POST/TRIANGLE/SEVEN_SECONDS/DEFENSE；十家族不与八枚举一一对应。',
        'COACH': '按POE进攻/节奏/篮板、防守及调用倾向表达粗方向；POE2/3不是第二第三得分手。',
        'FREELANCE': '四槽有序，前槽优先；只选当批合法枚举，不承诺调用比例。',
        'PLAYTYPE': '四槽类型与Initiator形成角色入口；前槽优先，不能由类型字段存在推断某CRC成员。',
        'TENDENCY': '仅具名48项，按角色分别研究；不统一Touches或Shot数值，不改原始能力。',
        'PERSONAL': '18项仅用于当批明确owner/opponent/offender/defender对象；不回退整体防守。',
        'TRAINING': '球队6项和球员5项训练方向；不承诺即时成长、疲劳变化或位置完整模板。',
        'ROTATION': 'BenchDepth为人数；Intangibles25–99仅为AI软轮换偏置，不锁分钟、不作球探能力。',
        'BOOK': '本队68槽容器可引用共享池；新同批合法加载目录和原有本队书身份仍必需。',
    }
    claim_for = {'SYSTEM':'B2-COACH-C', 'COACH':'B2-COACH-C', 'FREELANCE':'B2-COACH-C',
                 'PLAYTYPE':'B2-PLAYER-C', 'TENDENCY':'B2-PLAYER-C', 'PERSONAL':'B2-DEFENSE-C',
                 'TRAINING':'B2-TRAINING-C', 'ROTATION':'B2-PLAYER-C', 'BOOK':'B2-BOOK-C'}
    for family in SYSTEM_IDS:
        for group, fields in groups.items():
            bindings.append(dict(schema_version=VERSION, object_type='NativeBinding', binding_id='B2-' + family + '-' + group,
                                 system_id=family, evidence_claim_ids=[claim_for[group]], basketball_intent=intents[family] + qualifications[group],
                                 field_candidates=fields, mapping_status='SUPPORTED_FIELD_DIRECTION',
                                 behavior_effect='HYPOTHESIS_NOT_GUARANTEED',
                                 unknowns=['Specific AI selection, beneficiary, gameplay effect and effect size are not certified.',
                                           'Current same-batch GM_SANITIZED objects/enums and existing M3/DEV14 approval are required.'],
                                 fallback='HOLD_RESEARCH', status='REFERENCE_ONLY'))
        for suffix, fields, intent, status in (
            ('CRC_TYPE', ['playbook.slot'], '共享池名称仅供研究；逐CRC类型成员未知，不能输出TYPE_MATCHED_ONLY。', 'UNKNOWN_NATIVE_BEHAVIOR'),
            ('TEMPO', ['coach.Tempo'], 'Tempo原生可读写但篮球含义未知；以已认证POE节奏作较低精度替代。', 'UNKNOWN_NATIVE_BEHAVIOR'),
            ('BENEFICIARY', [], '第一受益人和分支未知；不凭编号、位置或FIST/GIVE/QUICK词根认证。', 'UNKNOWN_NATIVE_BEHAVIOR'),
            ('FORBIDDEN', ['overall.*', 'coach.PlaybookID', 'tendency.RAW_*'],
             '普通GM整体防守、自由换书和51匿名倾向不开放；只用个人防守、现有书及具名倾向。换书仅独立已确认事件后TEAM_BOOK_REBIND，再取新来源做槽提案。', 'UNSUPPORTED_ACTION'),
            ('EXACT_AI', [], '不支持硬锁分钟、精确调用概率、实时scram/peel/指定受益人或能力增强；使用角色/软轮换候选或HOLD。', 'UNSUPPORTED_ACTION'),
        ):
            bindings.append(dict(schema_version=VERSION, object_type='NativeBinding', binding_id='B2-' + family + '-' + suffix,
                                 system_id=family, evidence_claim_ids=['B2-BOUNDARY-C'], basketball_intent=intent,
                                 field_candidates=fields, mapping_status=status, behavior_effect='UNKNOWN',
                                 unknowns=['No certified per-CRC membership, exact beneficiary, probability or live-action controller.'],
                                 fallback='HOLD_RESEARCH', status='REFERENCE_ONLY'))

    # B3: narrow team-specific extraction from R2, not a new team-state database.
    philosophies = {
        'ATL':'McMillan：连接、一致性与回合组织；长期组织传统未知。',
        'BOS':'Udoka于2021上任；不借2022结果预知换防成功。',
        'BKN':'Nash：明星自主与持续传导并存。', 'CHA':'Borrego：青年培养与多功能性；后续长度分析不回填。',
        'CHI':'Donovan：协调半场创造者与防守连接者；不预装11月关键球表现。',
        'CLE':'Bickerstaff：先建立防守，再争取转换。', 'DAL':'Kidd新周期：提升防守，同时保留主创造核心。',
        'DEN':'Malone：竞争与防守要求，进攻强调移动和传球。', 'DET':'Casey：发展、工作习惯与防守标准。',
        'GSW':'Kerr：传球、移动、掩护与多点决策；不读取2022传球成绩。',
        'HOU':'Silas：年轻重建期；后来基础战术本回顾不作为开档事实。',
        'IND':'Carlisle：创造好投篮、防守与可持续竞争。', 'LAC':'Lue：第一动作受阻后继续适应和阅读。',
        'LAL':'Vogel：防守、跑动与明确角色；随机切入主张LAL-S2缺源。',
        'MEM':'Jenkins：推进、空间与突破通道。', 'MIA':'Spoelstra：守护组织文化，具体scheme可变；11月联防实例不回填。',
        'MIL':'Budenholzer：护框基础与2021季后赛适应；不把单场改动推广为全部比赛。',
        'MIN':'Finch：创造性与发挥球员特点；组织连续性不足。',
        'NOP':'Green：连接、关怀与责任；新周期不等于长期传统。', 'NYK':'Thibodeau：防守、竞争和工作标准。',
        'OKC':'Daigneault：发展与职业性；后来的less-patterns回顾不回填。',
        'ORL':'Mosley：pace/space/pass，防守沟通与破坏性。', 'PHI':'Rivers/Morey阶段：人才适配优先，不把Process视为固定战术。',
        'PHX':'Williams：team-first与快速决定，角色互补。', 'POR':'Billups新周期：增加传导、防守，保留第一创造者。',
        'SAC':'Walton：防守愿景与既有结果有张力；不采用11月材料。',
        'SAS':'Popovich：分享、责任、培养，具体战术随时代改变。', 'TOR':'Nurse：创新与因人因敌调整。',
        'UTA':'Snyder：保留护框轴，同时允许进攻演化。', 'WAS':'Unseld Jr.：防守责任、沟通和准备。',
    }
    aliases = dict(zip(('MOTION','TRIANGLE','SPREAD_PNR','ISO','POST','POINT_CENTER','TRANSITION','RIM_PROTECT','SWITCH_PRESSURE','ADAPTIVE'), SYSTEM_IDS))
    sources.append(dict(source_id='B3-R2-RETROSPECTIVE', title='R2 historical seed extraction',
                        publication_date='2026-10-20', historical_period='Claim-level pre-cutoff snapshot extraction only',
                        url=URL + R2, origin=locator(R2, 29, 156), source_status='REFERENCE_INDEXED', verification_ref=None))
    identities, identity_layers = [], {}
    lines = (ROOT / R2).read_text(encoding='utf-8').splitlines()
    for number, line in enumerate(lines, 1):
        if not line.startswith('| R2-T-'):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        parent, team, coach, culture, offense, defense, roles, confidence, gaps = cells
        candidates = list(dict.fromkeys(aliases[t] for t in re.findall(r'[A-Z_]+', offense + '+' + defense) if t in aliases))
        parent_claim = next(c for c in index['claims'] if c['claim_id'] == parent)
        ids = parent_claim['source_ids']
        early = [s for s in ids if source_map[s]['source_status'] != 'SOURCE_MISSING'
                 and publication_upper_bound(source_map[s]['publication_date']) is not None
                 and publication_upper_bound(source_map[s]['publication_date']).isoformat() <= '2021-10-19']
        coach_sources = early[:1] if team == 'ATL' else ([s for s in early if s.endswith('S2')] or early[:1])
        narratives = {
            'FRANCHISE_IDENTITY': ('时期限定的研究种子：' + culture + '。不据当前名单倒推永恒组织文化。', early[:1], 'FRANCHISE_HISTORICAL_REFERENCE'),
            'COACH_PHILOSOPHY': (coach + '（R2历史背景，非本局任命）：' + philosophies[team], coach_sources, 'COACH_HISTORICAL_PHILOSOPHY'),
            'BASKETBALL_SYSTEM': ('研究候选：进攻 ' + offense + '；防守 ' + defense + '。不是已执行体系或原生枚举。', early, 'GM_DESIGN_HYPOTHESIS'),
            'PLAYER_ROLE_AND_AGENCY': ('历史角色推理：' + roles + '；结构化阅读与创造权须依据本局真实技能重新评估，不按历史姓名赋予能力。', early, 'GM_DESIGN_HYPOTHESIS'),
            'MATCHUP_GAMEPLAN': ('研究条件：若第一优势被拒或角色空间不兼容，先比较局部角色/副体系与HOLD。代价是发展机会、空间和防守覆盖的取舍；保留' + culture + '的时期边界，不能因单次输赢重写文化。', early, 'GM_DESIGN_HYPOTHESIS'),
        }
        layer_refs = {}
        for layer, (statement, supporting, domain) in narratives.items():
            cid = 'B3-' + team + '-' + layer
            known = bool(supporting)
            references = supporting + ['B3-R2-RETROSPECTIVE'] if known else ids
            # A seed is an opening-date snapshot. Do not date later roster/context details
            # at the earliest article's publication; the retrospective is extracted per claim.
            date = '2021-10-19' if known else None
            c = claim(cid, statement, references, locator(R2, number), domain=domain,
                      status='SUPPORTED_INTERPRETATION' if known else 'UNKNOWN', since=date,
                      parent_claim_id=parent, team_abbr=team, identity_layer=layer)
            c['counterevidence'] += parent_claim['counterevidence']
            claims.append(c)
            layer_refs[layer] = [cid]
        # Missing sources remain explicit layer claims; no substitute URL or retrospective upgrade.
        for sid in ids:
            if source_map[sid]['source_status'] == 'SOURCE_MISSING' or (team == 'ATL' and sid == 'ATL-S2'):
                cid = 'B3-' + team + '-GAP-' + sid
                layer = 'COACH_PHILOSOPHY' if team == 'LAL' else 'FRANCHISE_IDENTITY'
                claims.append(claim(cid, sid + ': source missing or supports staffing only, not enduring culture.',
                                    [sid], locator(R2, number), domain='UNKNOWN', status='SOURCE_MISSING' if source_map[sid]['source_status']=='SOURCE_MISSING' else 'UNKNOWN',
                                    since=None, parent_claim_id=parent, team_abbr=team, identity_layer=layer))
                layer_refs[layer].append(cid)
        refs = [c for values in layer_refs.values() for c in values]
        unknowns = ['Historical personnel are not current-save facts.',
                    'Long-run identity continuity, game roster, coach, finances and matchup behavior require independent evidence.']
        unknowns += parent_claim['counterevidence']
        identities.append(dict(schema_version=VERSION, object_type='TeamIdentity', identity_id='B3-TEAM-' + team,
                               team_abbr=team, historical_seed_as_of='2021-10-19', evidence_claim_ids=refs,
                               franchise_value_claim_ids=layer_refs['FRANCHISE_IDENTITY'],
                               historical_coach_claim_ids=layer_refs['COACH_PHILOSOPHY'], unknown_values=unknowns,
                               system_candidates=candidates, confidence='HISTORICAL_SEED_ONLY',
                               operational_link='NOT_BOUND_TO_ANY_SAVE', status='HISTORICAL_SEED_ONLY'))
        identity_layers[team] = layer_refs

    # Four narrow, independently dated mechanism claims; original full research cards stay sealed.
    mechanism_claims = {}
    evidence_rows = json.loads((ROOT / 'web_gm/knowledge/bpti/four_family_evidence_v1.json').read_text(encoding='utf-8'))
    for row in evidence_rows:
        sid, family = row['source_id'], row['system_id']
        sources.append(dict(source_id=sid, title=row['title'], historical_period=row['event_period'],
                            publication_date=row['publication_date'], url=row['url'], origin=locator(EVIDENCE, row['evidence_line']),
                            source_status='REFERENCE_INDEXED', verification_ref=EVIDENCE))
        cid = 'B1-E4-' + family
        c = claim(cid, row['mechanism'], [sid], locator(EVIDENCE, row['evidence_line']), domain='BASKETBALL_PRINCIPLE',
                  status='SUPPORTED_INTERPRETATION', since=row['fact_valid_from'], until=row['fact_valid_to'],
                  parent_claim_id='R1-C-' + family)
        c['knowledge_available_from'] = row['publication_date']
        c['retrospective_only'] = False
        c['verification_ref'] = EVIDENCE
        c['counterevidence'] = ['Narrow film-study mechanism only; full original card, universal effects and NBA2K behavior remain unverified.']
        claims.append(c)
        mechanism_claims[family] = [cid]
    package = dict(schema_version=VERSION, version='BPTI_PACKAGE_B_V1',
                   sources=sources, claims=claims, bindings=bindings, identities=identities,
                   identity_layers=identity_layers, mechanism_claims=mechanism_claims,
                   supported_field_keys=sorted({k for fields in groups.values() for k in fields}),
                   authority='REFERENCE_ONLY_NOT_BOUND_TO_SAVE_NO_APPROVAL', base_main=BASE)
    output = ROOT / 'web_gm/knowledge/bpti/package_b_v1.json'
    output.write_text(json.dumps(package, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(status='KNOWLEDGE_BUILT', bindings=len(bindings), identities=len(identities),
                          narrow_mechanisms=len(mechanism_claims), output=str(output)), ensure_ascii=False))


if __name__ == '__main__':
    build()
