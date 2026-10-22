"""Build shared play references from an explicit archived catalog; no game access."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gm_core.play_pool import VERSION, AUTHORITY, PlayPool, infer_name, play_id


def profile(purpose, types, players, teams, risks, references):
    return dict(purpose=purpose,type_candidates=types,player_fit=players,team_fit=teams,
                poor_fit_or_counters=risks,reference_cards=references,
                evidence_status='BASKETBALL_NAME_INTERPRETATION_NOT_NATIVE_EXECUTION',
                position_restriction='NONE_PLAYER_REPORTED; roles describe suitability, not fixed positions')


PROFILES={
 'UNKNOWN':profile('UNKNOWN',[],['UNKNOWN'],['UNKNOWN'],['名称或用途未确认；保留HOLD，不臆造适配。'],[]),
 'PICK_AND_ROLL':profile('通过持球人与掩护人的配合制造突破、投篮或传球机会。',[4,5,6,7],
    ['PRIMARY_HANDLER：能控球、投篮威胁或突破并读协防。','SCREENING_FINISHER：掩护、顺下接球及终结。','SPACING_OUTLET：拉开空间并接二次传球。'],
    ['SPREAD_PNR：持球创造配掩护终结。','SECOND_SIDE：第一方案被限制后的二次持球动作。'],
    ['持球人不能惩罚防守放投。','顺下路线拥堵；换防后缺乏第二答案。'],['PNR_PRIMARY','SPACING']),
 'OFFSCREEN_SHOT':profile('借无球掩护或连续跑位为接球投篮创造分离空间；具体中投/三分类型尚未由名字认证。',[14,15],
    ['MOVEMENT_SHOOTER：跑位、接球投篮和读追防。','SCREENING_CONNECTOR：掩护质量和及时接应。','ENTRY_PASSER：把握射手出现的传球窗口。'],
    ['MOTION：传切与无球射手配合。','SHOOTER_CENTRIC：为接球投手创造出手机会。'],
    ['追防、top-lock或换防限制接球；需反切和第二选择。'],['MOTION_CUT','SCREEN_ROUTE','SPACING']),
 'HANDOFF':profile('通过手递手或近距离交球连接传球者与接球创造者；具体路线按名称仅作候选解释。',[12,13],
    ['HANDOFF_PASSER：持球保护、传球时机及掩护衔接。','HANDOFF_RECEIVER：接球投篮、突破或继续出球。','CUTTER：利用过度追防。'],
    ['HUB：让连接者参与组织。','MOTION：连续接应，不依赖单一持球点。'],
    ['过度贴防或换防封住交接；需要拒绝手递手/反切的替代意图。'],['POST_HUB','MOTION_CUT']),
 'POST_ATTACK':profile('围绕低位或背身入口创造单点得分、吸引帮助后的传球与切入。',[8,9,10],
    ['POST_SCORER：低位脚步、对抗及终结威胁。','ENTRY_PASSER：角度与时机。','WEAK_SIDE_SHOOTER：惩罚帮助。'],
    ['INSIDE_OUT：内线威胁带动外线。','POST_HIGH_LOW：高低位入口或再入位的研究方向。'],
    ['接球点过远、绕前或包夹；不能把名字当完整高低位脚本。'],['POST_HUB','SPACING']),
 'ISOLATION':profile('为具备个人创造能力的球员提供空间，利用节奏、脚步或错位制造优势。',[1,2,3],
    ['PRIMARY_CREATOR：持球技术、个人终结及被夹后的出球。','SPACER：牵制协防。','SECONDARY_CREATOR：接出球继续攻击。'],
    ['CREATOR_MIDRANGE：允许个人中距离与困难球创造。','MISMATCH_ATTACK：利用对位优势，保留二次接应。'],
    ['强单防、提前包夹、空间不足或核心体能负担。'],['SPACING']),
 'CUTTING':profile('利用空切或反跑形成接球终结机会，要求传球者与切入人识别窗口。',[11],
    ['CUTTER：移动时机、接球与篮下终结。','CONNECTOR：传球视野与时机。','SPACER：拉走协防。'],
    ['MOTION：持续移动。','HUB：围绕策应者组织接球终结。'],
    ['禁区拥堵、传球窗口关闭、无投射牵制。'],['MOTION_CUT','POST_HUB']),
 'HIGH_POST_HUB':profile('把高位/肘区连接者作为接应点，研究传球、切入与交球的衔接；名字不保证某条完整分支。',[9,12,13],
    ['POST_HUB：视野、传球与持球保护，具有得分威胁。','CUTTER：识别反切窗口。','MOVEMENT_SHOOTER：接应和二次攻击。'],
    ['ELBOW_HUB：高位策应。','INSIDE_OUT：在高低位和外线间转移球。'],
    ['接应被拒绝、hub无得分威胁、防守不需要帮助。'],['POST_HUB','MOTION_CUT']),
 'PICK_AND_POP':profile('名称中的POP提示掩护后向外接球的候选用途，不保证实际外弹分支。',[4,5,6,7],
    ['SHOOTING_SCREENER：具备相应射程的掩护接应者。','PRIMARY_HANDLER：读防守收缩并及时传球。'],
    ['SPACING：用外弹拉开空间。','SPREAD_PNR：顺下以外的补充分支。'],
    ['掩护人没有射程时无法产生同样空间代价；换防可压缩机会。'],['PNR_PRIMARY','SPACING']),
 'SHORT_ROLL_HUB':profile('名称中的SHORT ROLL提示短距离接应后处理球的研究方向，不认证固定4v3或传球路线。',[7],
    ['SHORT_ROLL_CONNECTOR：接球后快速传球、抛投或终结。','WEAK_SIDE_SHOOTER：接帮助来源的传球。'],
    ['PNR_COUNTER：对上提/夹击的补充答案。','HUB：让掩护人承担二次决策。'],
    ['连接者停球或传球慢；弱侧没有可利用的空间。'],['PNR_PRIMARY','POST_HUB']),
 'SPLIT_CONNECTION':profile('名称中的SPLIT提示球外协作/交叉掩护的研究线索，具体路线未认证。',[],
    ['CONNECTOR：及时转移球。','MOVEMENT_SHOOTER：读掩护方向。','CUTTER：利用追防过度的空隙。'],
    ['MOTION：多人连续选择。','INSIDE_OUT：让接应者附近形成配合。'],
    ['换防和提前交接可能消除第一优势。'],['MOTION_CUT','POST_HUB'])
}

MODIFIERS={k:dict(meaning=v) for k,v in {
 'POP':'掩护后外弹的名称线索','ROLL':'掩护后顺下的名称线索',
 'SHORT_ROLL':'短顺下接应/处理球的名称线索','SLIP':'提前滑走/空切的名称线索',
 'PINDOWN':'向下无球掩护的名称线索','FLOPPY':'无球掩护选择的名称线索',
 'FLARE':'向外掩护/接应的名称线索','STAGGER':'连续掩护的名称线索',
 'SPLIT':'交叉/球外协作的名称线索','HORNS':'双高位落位的名称线索',
 'ELBOW':'肘区接应的名称线索','PINCH':'高位连接的名称线索',
 'HIGH':'高位入口或落位的名称线索','LOW':'低位入口或落位的名称线索',
 'SPREAD':'拉开空间的名称线索','WEAVE':'连续交接的名称线索',
 'CURL':'绕掩护卷入的名称线索','LOOP':'绕行接应的名称线索',
 'DIVE':'向篮下切入的名称线索','ALLEY':'空接接应的名称线索',
 'HAMMER':'弱侧掩护/底角联系的名称线索','PISTOL':'提前侧翼配合的名称线索',
 'END':'末段组/名称线索，不能保证触发时间','TWIST':'改角度/连续掩护的名称线索'
}.items()}


def build(source, type_names):
    labels={r['crc']:r['labels'] for r in source['static_labels']}
    seen={}
    for book in source['books']:
        for index,crc in enumerate(book['play_crc_slots']):
            if crc:
                seen.setdefault(crc,[]).append(index)
    plays=[]
    extras={'POP':'PICK_AND_POP','SHORT_ROLL':'SHORT_ROLL_HUB','SPLIT':'SPLIT_CONNECTION',
            'ELBOW':'HIGH_POST_HUB','PINCH':'HIGH_POST_HUB'}
    for crc,slots in sorted(seen.items()):
        names=labels.get(crc,[])
        name=names[0] if len(names)==1 else ''
        inferred=infer_name(name,PROFILES,MODIFIERS)
        for tag,profile_id in extras.items():
            if tag in inferred['action_tags'] and profile_id not in inferred['fit_profile_ids']:
                inferred['fit_profile_ids'].append(profile_id)
        favorite_only=all(i>=60 for i in slots)
        if favorite_only:
            inferred.update(purpose='仅在已观测Favorite分组出现；可能是类别/快捷项，不宣称完整动作脚本。',
                            purpose_status='FAVORITE_ENTRY_SEMANTICS_UNKNOWN',type_candidates=[])
        memberships=source.get('type_memberships',{}).get(f'0x{crc:08x}',[])
        levels={m['evidence_status'] for m in memberships}
        type_status=next(iter(levels)) if len(levels)==1 else 'MIXED_EVIDENCE' if levels else 'UNKNOWN'
        plays.append(dict(play_id=play_id(crc),native_crc=crc,names=names,
            name_status='STATIC_LABEL_CRC_JOIN' if len(names)==1 else 'AMBIGUOUS_STATIC_LABELS' if names else 'UNKNOWN',
            entry_kind='FAVORITE_ONLY_ENTRY' if favorite_only else 'LOADED_PLAY_REFERENCE',
            types=dict(status=type_status,memberships=memberships,relationship='MANY_TO_MANY_PLAYER_REPORTED'),
            **inferred,evidence_refs=['ARCHIVED_BOOKS','STATIC_LABELS','NAME_INTERPRETATION','PLAYER_POOL_RULES']))
    return dict(version=VERSION,authority=AUTHORITY,game_scope='NBA2K22_PC_CURRENT_GEN',
        play_type_names=type_names,fit_profiles=PROFILES,action_modifiers=MODIFIERS,
        calling_rules=dict(evidence='PLAYER_REPORTED_UI_2026_10_20',
            player_playtype_slots='ORDERED_HIGHER_FIRST; 1/2 main, 3/4 occasional',
            team_freelance_slots='ORDERED_HIGHER_FIRST_MORE_USED; exact rates unknown',
            shared_pool='ONE_PLAY_MAY_BE_REFERENCED_BY_MANY_BOOKS; other teams can add/replace it',
            type_eligibility='MATCH_REQUIRED; a play can belong to multiple types',
            manual_call='HUMAN_BUTTON_INPUT; CPU-vs-CPU automatically selects',
            exact_frequency='UNKNOWN_NOT_TO_BE_REVERSE_ENGINEERED',
            capacity=dict(total=68,regular=30,bench_group=20,endgame=10,favorite=8)),
        sources=[dict(source_id='ARCHIVED_BOOKS',ref='observed_catalog_v1.json',
                      status='ARCHIVED_REFERENCE_NOT_CURRENT_SAVE',batch=source['source_batch_id']),
                 dict(source_id='STATIC_LABELS',ref='observed_catalog_v1.json:static_labels',
                      status='STATIC_LABEL_AND_CRC_NOT_TYPE_PROOF',exe_sha256=source['exe_sha256']),
                 dict(source_id='NAME_INTERPRETATION',ref='scripts/build_gm_play_pool.py:PROFILES/MODIFIERS',
                      status='QUALITATIVE_BASKETBALL_INFERENCE_NOT_NATIVE_TYPE',
                      basis='Existing M2 action references plus explicit name tokens; no historical NBA season outcomes'),
                 dict(source_id='PLAYER_POOL_RULES',ref='Direct player request 2026-10-20',
                      status='PLAYER_REPORTED_UI',scope='Both four-slot groups ordered, shared pool and capacity')],
        plays=plays)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'web_gm/knowledge/plays/observed_catalog_v1.json')
    parser.add_argument('--output',type=Path,default=ROOT/'web_gm/knowledge/plays/play_pool_v1.json')
    args=parser.parse_args()
    source=json.loads(args.source.read_text(encoding='utf-8-sig'))
    types=json.loads((ROOT/'config/state_io_native/player.json').read_text(encoding='utf-8-sig'))['PLAY_TYPE_NAMES']
    data=build(source,types)
    # Keep references compact; the full fit data lives once per profile and is resolved by show().
    header={k:v for k,v in data.items() if k!='plays'}
    text=json.dumps(header,ensure_ascii=False,indent=2)[:-2]+',\n  "plays": [\n'
    text+=',\n'.join('    '+json.dumps(p,ensure_ascii=False,separators=(',',':')) for p in data['plays'])+'\n  ]\n}\n'
    if len(text.encode('utf-8'))>2_000_000:
        raise ValueError('PLAY_POOL_EXCEEDS_EXISTING_KNOWLEDGE_SIZE_LIMIT')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(text,encoding='utf-8',newline='\n')
    installed=json.loads(args.output.read_text(encoding='utf-8'))
    print(json.dumps(PlayPool(installed,source).coverage(),ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    sys.exit(main())
