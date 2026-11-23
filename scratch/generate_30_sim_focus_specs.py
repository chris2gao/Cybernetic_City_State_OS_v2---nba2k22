import os, sys, re, json, sqlite3

docs_dir = r'08_Domain_Applications/Antigravity_GM_Engine/docs'
tactics_dir = r'08_Domain_Applications/Antigravity_GM_Engine/database/tactics'
db_path = r'C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite'

local_out_dir = r'08_Domain_Applications/Antigravity_GM_Engine/database/tactics/20261123_simulated_gameplan_focus_execution'
exports_out_dir = r'C:\nba2k22\exports\20261123_simulated_gameplan_focus_execution'

os.makedirs(local_out_dir, exist_ok=True)
os.makedirs(exports_out_dir, exist_ok=True)

team_order = [
    (0, "PHI", "Philadelphia 76ers", "56_PHI_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (1, "MIL", "Milwaukee Bucks", "53_MIL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (2, "WAS", "Washington Wizards", "76_WAS_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (3, "CHI", "Chicago Bulls", "63_CHI_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (4, "CLE", "Cleveland Cavaliers", "66_CLE_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (5, "BOS", "Boston Celtics", "51_BOS_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (6, "LAC", "LA Clippers", "61_LAC_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (8, "MEM", "Memphis Grizzlies", "58_MEM_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (9, "ATL", "Atlanta Hawks", "65_ATL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (10, "MIA", "Miami Heat", "52_MIA_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (11, "NOP", "New Orleans Pelicans", "68_NOP_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (12, "UTA", "Utah Jazz", "60_UTA_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (13, "SAC", "Sacramento Kings", "73_SAC_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (14, "NYK", "New York Knicks", "71_NYK_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (15, "LAL", "Los Angeles Lakers", "62_LAL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (16, "ORL", "Orlando Magic", "78_ORL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (17, "DAL", "Dallas Mavericks", "55_DAL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (18, "BKN", "Brooklyn Nets", "59_BKN_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (19, "DEN", "Denver Nuggets", "57_DEN_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (20, "IND", "Indiana Pacers", "70_IND_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (21, "DET", "Detroit Pistons", "77_DET_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (22, "TOR", "Toronto Raptors", "64_TOR_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (23, "HOU", "Houston Rockets", "79_HOU_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (24, "OKC", "Oklahoma City Thunder", "72_OKC_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (25, "SAS", "San Antonio Spurs", "74_SAS_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (26, "PHX", "Phoenix Suns", "54_PHX_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (27, "MIN", "Minnesota Timberwolves", "67_MIN_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (28, "POR", "Portland Trail Blazers", "69_POR_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (29, "GSW", "Golden State Warriors", "50_GSW_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md"),
    (31, "CHA", "Charlotte Hornets", "75_CHA_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md")
]

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT team_id, roster_slot, player_name, face_id FROM player_source_details")
db_players = {}
for tid, slot, name, fid in cur.fetchall():
    if tid not in db_players: db_players[tid] = {}
    db_players[tid][name.lower().strip()] = (slot, fid, name)
    db_players[tid][slot] = (slot, fid, name)
conn.close()

# Load batch poe defaults
batch_files = [f'BATCH_{i:02d}_{name}_FULL_DIMENSIONAL_SPEC.json' for i, name in [
    (1, 'ATLANTIC'), (2, 'CENTRAL'), (3, 'SOUTHEAST'), (4, 'PACIFIC'), (5, 'NORTHWEST'), (6, 'SOUTHWEST')
]]
batch_poe = {}
for bf in batch_files:
    bp = os.path.join(tactics_dir, bf)
    if not os.path.exists(bp): continue
    with open(bp, 'r', encoding='utf-8') as f:
        d = json.load(f)
    for tid_str, t in d.get('teams', {}).items():
        tid = int(tid_str)
        cs = t.get('coaching_system', {})
        batch_poe[tid] = {k: v for k, v in cs.items() if k.startswith('poe_')}

def parse_poe_num(val_str, field):
    if isinstance(val_str, int): return val_str
    m = re.search(r'\((\d+)\)', str(val_str))
    if m: return int(m.group(1))
    m = re.search(r'ID_(\d+)', str(val_str))
    if m: return int(m.group(1))
    fallbacks = {
        'poe_offense': 4,
        'poe_offense_tempo': 8,
        'poe_offense_rebound': 12,
        'poe_defense': 13,
        'poe_defense_physicality': 18,
        'poe_defense_rebound': 19
    }
    return fallbacks.get(field, 0)

poe_enum_metadata = {
    'poe_offense': {
        1: ('GET_TO_BASKET', '冲击篮筐 (Attack the Basket)'),
        2: ('GET_SHOOTERS_OPEN', '为射手跑位 (Get Shooters Open)'),
        3: ('FEED_THE_POST', '打低位内线 (Feed the Post)'),
        4: ('PICK_AND_ROLL_OFFENSE', '挡拆进攻 (Pick & Roll Offense)'),
        5: ('NEUTRAL_OFFENSE_FOCUS', '中立进攻侧重 (Neutral Offense)'),
        6: ('RUN_OFFENSE_THROUGH_SCORER', '围绕得分手运转 (Run Offense Through Scorer)')
    },
    'poe_offense_tempo': {
        7: ('PATIENT_OFFENSE', '耐心阵地战 (Patient Offense)'),
        8: ('NEUTRAL_OFFENSE_TEMPO', '中立进攻节奏 (Neutral Tempo)'),
        9: ('SHOOT_AT_WILL', '尽早出手反击 (Shoot at Will / Fast Pace)')
    },
    'poe_offense_rebound': {
        10: ('CRASH_OFFENSIVE_BOARDS', '全力拼抢前场篮板 (Crash Offensive Boards)'),
        11: ('NEUTRAL_OFFENSE_REBOUND', '中立进攻篮板 (Neutral Offense Rebound)'),
        12: ('LIMIT_TRANSITION', '极速退防限制快攻 (Limit Transition)')
    },
    'poe_defense': {
        13: ('PROTECT_PAINT', '保护禁区油漆区 (Protect the Paint)'),
        14: ('NEUTRAL_DEFENSE_FOCUS', '中立防守侧重 (Neutral Defense)'),
        15: ('LIMIT_PERIMETER_SHOTS', '贴防限制外线三分 (Limit Perimeter Shots)')
    },
    'poe_defense_physicality': {
        16: ('PLAY_CONSERVATIVE', '保守防守避免犯规 (Play Conservative)'),
        17: ('NEUTRAL_DEFENSE_TEMPO', '中立身体对抗 (Neutral Physicality)'),
        18: ('PLAY_PHYSICAL', '强硬身体对抗 (Play Physical)')
    },
    'poe_defense_rebound': {
        19: ('CRASH_DEFENSIVE_BOARDS', '全员保护防守篮板 (Crash Defensive Boards)'),
        20: ('NEUTRAL_DEFENSE_REBOUND', '中立防守篮板 (Neutral Defense Rebound)'),
        21: ('RUN_IN_TRANSITION', '抓篮板极速打反击 (Run in Transition)')
    }
}

# Pre-existing verified scoring options
ready_options = {}
for f in os.listdir(tactics_dir):
    if f.endswith('_tactical_execution_ready.json') and not f.startswith('cycle_02'):
        abbr = f.split('_')[0].upper()
        data = json.load(open(os.path.join(tactics_dir, f), encoding='utf-8'))
        so = data.get('scoring_options')
        if so and len(so) == 3:
            ready_options[abbr] = so

def parse_doc_table_players(doc_path):
    with open(doc_path, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = text.split('\n')
    players = []
    in_table = False
    mapping = {}
    for line in lines:
        ls = line.strip()
        if ('| 槽位 |' in ls or '| Roster' in ls or '| 序号 |' in ls) and any(k in ls for k in ['触球', 'Touches', 'Initiator', 'Init', 'Tch', '推进']):
            cols = [x.strip().replace('**', '') for x in ls.split('|')[1:-1]]
            mapping = {}
            for idx, col in enumerate(cols):
                c_low = col.lower()
                if '槽位' in col or 'roster' in c_low or '序号' in col: mapping['slot'] = idx
                elif '姓名' in col or 'name' in c_low or '球员' in col: mapping['name'] = idx
                elif '触球' in col or 'touches' in c_low or 'tch' in c_low: mapping['touches'] = idx
            in_table = True
            continue
        if in_table:
            if ls.startswith('|-') or ls.startswith('| :-') or ls.startswith('|:--') or ls.startswith('|: -'):
                continue
            if not ls.startswith('|'):
                if players: in_table = False
                continue
            parts = [x.strip().replace('**', '') for x in ls.split('|')[1:-1]]
            if len(parts) > max(mapping.values()):
                players.append({
                    'slot_str': parts[mapping['slot']] if 'slot' in mapping else parts[0],
                    'name_str': parts[mapping['name']] if 'name' in mapping else parts[1],
                    'touches_str': parts[mapping['touches']] if 'touches' in mapping else ''
                })
    return players

def parse_doc_coaching_poe(doc_path):
    with open(doc_path, 'r', encoding='utf-8') as f:
        text = f.read()
    coaching = {}
    for line in text.split('\n'):
        ls = line.strip()
        m = re.search(r'(poe_[a-z_]+)\s*[:=]\s*`?([A-Za-z0-9_\(\)\s]+)`?', ls, re.I)
        if m:
            k = m.group(1).lower().strip()
            v = m.group(2).strip()
            num = parse_poe_num(v, k)
            if num: coaching[k] = num
        # table match
        if '|' in ls and 'poe' in ls.lower():
            parts = [x.strip() for x in ls.split('|')[1:-1]]
            if len(parts) >= 2:
                label = parts[0].lower()
                val = parts[1]
                if 'poe offense tempo' in label or '进攻节奏' in label:
                    n = parse_poe_num(val, 'poe_offense_tempo')
                    if n: coaching['poe_offense_tempo'] = n
                elif 'poe offense rebound' in label or '前场篮板' in label:
                    n = parse_poe_num(val, 'poe_offense_rebound')
                    if n: coaching['poe_offense_rebound'] = n
                elif 'poe offense' in label or '进攻重点' in label or '进攻侧重' in label:
                    n = parse_poe_num(val, 'poe_offense')
                    if n: coaching['poe_offense'] = n
                elif 'poe defense physicality' in label or '身体对抗' in label:
                    n = parse_poe_num(val, 'poe_defense_physicality')
                    if n: coaching['poe_defense_physicality'] = n
                elif 'poe defense rebound' in label or '后场篮板' in label or '防守篮板' in label:
                    n = parse_poe_num(val, 'poe_defense_rebound')
                    if n: coaching['poe_defense_rebound'] = n
                elif 'poe defense' in label or '防守重点' in label or '防守侧重' in label:
                    n = parse_poe_num(val, 'poe_defense')
                    if n: coaching['poe_defense'] = n
    return coaching

print(f"Generating 30 simulated gameplan focus files...")
generated_files = []

for idx, (tid, abbr, tname, doc_name) in enumerate(team_order, 1):
    doc_path = os.path.join(docs_dir, doc_name)
    plist = parse_doc_table_players(doc_path)
    doc_poe = parse_doc_coaching_poe(doc_path)
    bdict = batch_poe.get(tid, {})
    
    # 1. Resolve 6 POE
    final_poe = {}
    for f in ['poe_offense', 'poe_offense_tempo', 'poe_offense_rebound', 'poe_defense', 'poe_defense_physicality', 'poe_defense_rebound']:
        v = doc_poe.get(f)
        if v is None:
            v_raw = bdict.get(f)
            v = parse_poe_num(v_raw, f)
        final_poe[f] = v
        
    # 2. Resolve 3 Scoring Options
    resolved_opts = []
    # Check ready_options first
    if abbr in ready_options:
        for opt in ready_options[abbr]:
            p_name = opt['player_name']
            p_id = opt['player_id']
            for (slot, fid, db_name) in db_players.get(tid, {}).values():
                if fid == p_id or db_name.lower() in p_name.lower() or p_name.lower() in db_name.lower():
                    resolved_opts.append({
                        'option_slot': len(resolved_opts)+1,
                        'player_name': db_name,
                        'player_id': fid,
                        'roster_slot': slot
                    })
                    break
                    
    if len(resolved_opts) < 3:
        resolved_opts = []
        used_fids = set()
        scored_players = []
        for p in plist:
            pname = p.get('name_str', '').strip()
            t_str = p.get('touches_str', '')
            m = re.search(r'\d+', t_str)
            t_val = int(m.group(0)) if m else 0
            scored_players.append((t_val, pname))
        scored_players.sort(key=lambda x: x[0], reverse=True)
        
        for t_val, pname in scored_players:
            if len(resolved_opts) == 3: break
            p_clean = re.sub(r'[\(\（].*?[\)\）]', '', pname).strip().lower()
            matched = None
            for key, val in db_players.get(tid, {}).items():
                if isinstance(key, str):
                    slot, fid, db_name = val
                    if fid in used_fids: continue
                    if p_clean in key or key in p_clean:
                        matched = (slot, fid, db_name)
                        break
                    db_last = key.split()[-1]
                    p_last = p_clean.split()[-1]
                    if len(db_last) >= 4 and db_last in p_clean:
                        matched = (slot, fid, db_name)
                        break
            if not matched:
                for p_raw in plist:
                    if p_raw.get('name_str', '').strip() == pname:
                        slot_m = re.search(r'\d+', p_raw.get('slot_str', ''))
                        if slot_m:
                            s_idx = int(slot_m.group(0))
                            if s_idx in db_players.get(tid, {}):
                                slot, fid, db_name = db_players[tid][s_idx]
                                if fid not in used_fids:
                                    matched = (slot, fid, db_name)
                        break
            if matched:
                slot, fid, db_name = matched
                used_fids.add(fid)
                resolved_opts.append({
                    'option_slot': len(resolved_opts)+1,
                    'player_name': db_name,
                    'player_id': fid,
                    'roster_slot': slot,
                    'touch_proposal': t_val
                })
                
    # 3. Build writes array (9 atomic writes)
    writes = [
        {
            "field_name": "scoring_option_1",
            "target_block": "GAMEPLAN",
            "offset": 376,
            "type": "uint16",
            "val_raw": resolved_opts[0]['player_id'],
            "val_human": resolved_opts[0]['player_name'],
            "roster_slot": resolved_opts[0]['roster_slot'],
            "description": f"第一进攻选择 (Scoring Option 1): {resolved_opts[0]['player_name']} (ID={resolved_opts[0]['player_id']}, Slot={resolved_opts[0]['roster_slot']})"
        },
        {
            "field_name": "scoring_option_2",
            "target_block": "GAMEPLAN",
            "offset": 378,
            "type": "uint16",
            "val_raw": resolved_opts[1]['player_id'],
            "val_human": resolved_opts[1]['player_name'],
            "roster_slot": resolved_opts[1]['roster_slot'],
            "description": f"第二进攻选择 (Scoring Option 2): {resolved_opts[1]['player_name']} (ID={resolved_opts[1]['player_id']}, Slot={resolved_opts[1]['roster_slot']})"
        },
        {
            "field_name": "scoring_option_3",
            "target_block": "GAMEPLAN",
            "offset": 380,
            "type": "uint16",
            "val_raw": resolved_opts[2]['player_id'],
            "val_human": resolved_opts[2]['player_name'],
            "roster_slot": resolved_opts[2]['roster_slot'],
            "description": f"第三进攻选择 (Scoring Option 3): {resolved_opts[2]['player_name']} (ID={resolved_opts[2]['player_id']}, Slot={resolved_opts[2]['roster_slot']})"
        },
        {
            "field_name": "poe_offense",
            "target_block": "GAMEPLAN",
            "offset": 382,
            "type": "uint8",
            "val_raw": final_poe['poe_offense'],
            "val_human": poe_enum_metadata['poe_offense'][final_poe['poe_offense']][0],
            "description": f"进攻侧重/进攻重点 (POEOffense): {poe_enum_metadata['poe_offense'][final_poe['poe_offense']][1]} ({final_poe['poe_offense']})"
        },
        {
            "field_name": "poe_offense_tempo",
            "target_block": "GAMEPLAN",
            "offset": 383,
            "type": "uint8",
            "val_raw": final_poe['poe_offense_tempo'],
            "val_human": poe_enum_metadata['poe_offense_tempo'][final_poe['poe_offense_tempo']][0],
            "description": f"进攻节奏 (POEOffenseTempo): {poe_enum_metadata['poe_offense_tempo'][final_poe['poe_offense_tempo']][1]} ({final_poe['poe_offense_tempo']})"
        },
        {
            "field_name": "poe_offense_rebound",
            "target_block": "GAMEPLAN",
            "offset": 384,
            "type": "uint8",
            "val_raw": final_poe['poe_offense_rebound'],
            "val_human": poe_enum_metadata['poe_offense_rebound'][final_poe['poe_offense_rebound']][0],
            "description": f"进攻篮板策略 (POEOffenseRebound): {poe_enum_metadata['poe_offense_rebound'][final_poe['poe_offense_rebound']][1]} ({final_poe['poe_offense_rebound']})"
        },
        {
            "field_name": "poe_defense",
            "target_block": "GAMEPLAN",
            "offset": 385,
            "type": "uint8",
            "val_raw": final_poe['poe_defense'],
            "val_human": poe_enum_metadata['poe_defense'][final_poe['poe_defense']][0],
            "description": f"防守侧重/防守重点 (POEDefense): {poe_enum_metadata['poe_defense'][final_poe['poe_defense']][1]} ({final_poe['poe_defense']})"
        },
        {
            "field_name": "poe_defense_physicality",
            "target_block": "GAMEPLAN",
            "offset": 386,
            "type": "uint8",
            "val_raw": final_poe['poe_defense_physicality'],
            "val_human": poe_enum_metadata['poe_defense_physicality'][final_poe['poe_defense_physicality']][0],
            "description": f"防守对抗策略 (POEDefensePhysicality): {poe_enum_metadata['poe_defense_physicality'][final_poe['poe_defense_physicality']][1]} ({final_poe['poe_defense_physicality']})"
        },
        {
            "field_name": "poe_defense_rebound",
            "target_block": "GAMEPLAN",
            "offset": 387,
            "type": "uint8",
            "val_raw": final_poe['poe_defense_rebound'],
            "val_human": poe_enum_metadata['poe_defense_rebound'][final_poe['poe_defense_rebound']][0],
            "description": f"防守篮板策略 (POEDefenseRebound): {poe_enum_metadata['poe_defense_rebound'][final_poe['poe_defense_rebound']][1]} ({final_poe['poe_defense_rebound']})"
        }
    ]
    
    spec_data = {
        "protocol_version": "v2.0_full_dimensional_native_mod",
        "spec_type": "SIMULATED_GAMEPLAN_FOCUS_MOD",
        "team_id": tid,
        "team_abbr": abbr,
        "team_name": tname,
        "source_research_doc": doc_name,
        "target_menu": "教练设置 - 模拟侧重 (Simulated Focus / Gameplan Focus)",
        "execution_target": "GAMEPLAN (stride 880, continuous offset range 376-387 / 0x178-0x183)",
        "conflict_resolution": "STRICT_LATEST_RESEARCH_DOC_PRIORITY",
        "simulated_focus_summary": {
            "scoring_options": resolved_opts,
            "poe_settings": {
                "poe_offense": {
                    "id": final_poe['poe_offense'],
                    "name": poe_enum_metadata['poe_offense'][final_poe['poe_offense']][0],
                    "desc": poe_enum_metadata['poe_offense'][final_poe['poe_offense']][1]
                },
                "poe_offense_tempo": {
                    "id": final_poe['poe_offense_tempo'],
                    "name": poe_enum_metadata['poe_offense_tempo'][final_poe['poe_offense_tempo']][0],
                    "desc": poe_enum_metadata['poe_offense_tempo'][final_poe['poe_offense_tempo']][1]
                },
                "poe_offense_rebound": {
                    "id": final_poe['poe_offense_rebound'],
                    "name": poe_enum_metadata['poe_offense_rebound'][final_poe['poe_offense_rebound']][0],
                    "desc": poe_enum_metadata['poe_offense_rebound'][final_poe['poe_offense_rebound']][1]
                },
                "poe_defense": {
                    "id": final_poe['poe_defense'],
                    "name": poe_enum_metadata['poe_defense'][final_poe['poe_defense']][0],
                    "desc": poe_enum_metadata['poe_defense'][final_poe['poe_defense']][1]
                },
                "poe_defense_physicality": {
                    "id": final_poe['poe_defense_physicality'],
                    "name": poe_enum_metadata['poe_defense_physicality'][final_poe['poe_defense_physicality']][0],
                    "desc": poe_enum_metadata['poe_defense_physicality'][final_poe['poe_defense_physicality']][1]
                },
                "poe_defense_rebound": {
                    "id": final_poe['poe_defense_rebound'],
                    "name": poe_enum_metadata['poe_defense_rebound'][final_poe['poe_defense_rebound']][0],
                    "desc": poe_enum_metadata['poe_defense_rebound'][final_poe['poe_defense_rebound']][1]
                }
            }
        },
        "writes": writes
    }
    
    file_name = f"{tid:02d}_{abbr}_sim_focus_mod.json"
    local_path = os.path.join(local_out_dir, file_name)
    export_path = os.path.join(exports_out_dir, file_name)
    
    with open(local_path, 'w', encoding='utf-8') as f:
        json.dump(spec_data, f, indent=2, ensure_ascii=False)
        
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(spec_data, f, indent=2, ensure_ascii=False)
        
    file_sz = os.path.getsize(local_path) / 1024.0
    print(f"[{idx:02d}/30] Generated {file_name}: {file_sz:.2f} KB | writes=9 (3 options + 6 poe)")
    generated_files.append((tid, abbr, file_name, local_path, export_path))

print(f"\nSuccessfully generated and mirrored all 30 single-team simulated focus mod execution files!")
