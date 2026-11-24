import os, sys, re, json, sqlite3, shutil

sys.path.insert(0, '.')

docs_dir = r'08_Domain_Applications/Antigravity_GM_Engine/docs'
tactics_dir = r'08_Domain_Applications/Antigravity_GM_Engine/database/tactics'
out_dir_local = os.path.join(tactics_dir, 'single_team_execution')
out_dir_export = r'C:\nba2k22\exports\single_team_execution'

os.makedirs(out_dir_local, exist_ok=True)
os.makedirs(out_dir_export, exist_ok=True)

# 1. Connect to clean, post-trade league_state.sqlite
db_path = r'C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT team_id, roster_slot, player_name, face_id FROM player_source_details")
db_roster = {}
db_player_name_to_slot = {}
for tid, slot, name, fid in cur.fetchall():
    db_roster[(tid, slot)] = (name, fid)
    db_player_name_to_slot[(tid, name.lower().strip())] = slot
conn.close()

# 2. Load 150-player baseline task spec
spec_150_path = os.path.join(tactics_dir, 'team_competitive_optimization_spec.json')
with open(spec_150_path, 'r', encoding='utf-8') as f:
    spec_150 = json.load(f).get('teams', {})

# Team Order (0..29 standard teams)
team_order = [
    (0, 'PHI', 'Philadelphia 76ers', '56_PHI_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (1, 'MIL', 'Milwaukee Bucks', '53_MIL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (2, 'WAS', 'Washington Wizards', '76_WAS_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (3, 'CHI', 'Chicago Bulls', '63_CHI_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (4, 'CLE', 'Cleveland Cavaliers', '66_CLE_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (5, 'BOS', 'Boston Celtics', '51_BOS_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (6, 'LAC', 'LA Clippers', '61_LAC_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (8, 'MEM', 'Memphis Grizzlies', '58_MEM_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (9, 'ATL', 'Atlanta Hawks', '65_ATL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (10, 'MIA', 'Miami Heat', '52_MIA_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (11, 'NOP', 'New Orleans Pelicans', '68_NOP_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (12, 'UTA', 'Utah Jazz', '60_UTA_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (13, 'SAC', 'Sacramento Kings', '73_SAC_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (14, 'NYK', 'New York Knicks', '71_NYK_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (15, 'LAL', 'Los Angeles Lakers', '62_LAL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (16, 'ORL', 'Orlando Magic', '78_ORL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (17, 'DAL', 'Dallas Mavericks', '55_DAL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (18, 'BKN', 'Brooklyn Nets', '59_BKN_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (19, 'DEN', 'Denver Nuggets', '57_DEN_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (20, 'IND', 'Indiana Pacers', '70_IND_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (21, 'DET', 'Detroit Pistons', '77_DET_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (22, 'TOR', 'Toronto Raptors', '64_TOR_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (23, 'HOU', 'Houston Rockets', '79_HOU_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (24, 'OKC', 'Oklahoma City Thunder', '72_OKC_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (25, 'SAS', 'San Antonio Spurs', '74_SAS_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (26, 'PHX', 'Phoenix Suns', '54_PHX_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (27, 'MIN', 'Minnesota Timberwolves', '67_MIN_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (28, 'POR', 'Portland Trail Blazers', '69_POR_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (29, 'GSW', 'Golden State Warriors', '50_GSW_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'),
    (31, 'CHA', 'Charlotte Hornets', '75_CHA_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md')
]

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
                elif '分球' in col or '出球' in col or 'dish' in c_low or 'dsh' in c_low or '传球意愿' in col: mapping['dish'] = idx
                elif '纪律' in col or 'disc' in c_low: mapping['disc'] = idx
                elif 'roll' in c_low or '顺下' in col or '外弹' in col or '顺弹' in col or 'r/p' in c_low: mapping['roll_pop'] = idx
                elif '3pt' in c_low or '三分' in col: mapping['shot_3'] = idx
                elif '发起' in col or 'initiator' in c_low or '推进' in col or 'init' in c_low: mapping['init'] = idx
                elif ('play' in c_low and ('type' in c_low or '类型' in col or '[' in col)) or '战术类型' in col: mapping['play_types'] = idx
            in_table = True
            continue
            
        if in_table:
            if ls.startswith('|-') or ls.startswith('| :-') or ls.startswith('|:--') or ls.startswith('|: -'):
                continue
            if not ls.startswith('|'):
                if players:
                    in_table = False
                continue
            parts = [x.strip().replace('**', '') for x in ls.split('|')[1:-1]]
            if len(parts) > max(mapping.values()):
                players.append({
                    'slot_str': parts[mapping['slot']] if 'slot' in mapping else parts[0],
                    'name_str': parts[mapping['name']] if 'name' in mapping else parts[1],
                    'role_str': '',
                    'touches_str': parts[mapping['touches']] if 'touches' in mapping else '',
                    'dish_str': parts[mapping['dish']] if 'dish' in mapping else '',
                    'disc_str': parts[mapping['disc']] if 'disc' in mapping else '',
                    'roll_pop_str': parts[mapping['roll_pop']] if 'roll_pop' in mapping else '',
                    'shot_3_str': parts[mapping['shot_3']] if 'shot_3' in mapping else '',
                    'init_str': parts[mapping['init']] if 'init' in mapping else '',
                    'play_types_str': parts[mapping['play_types']] if 'play_types' in mapping else ''
                })
    return players

def parse_coaching_exact(doc_path):
    with open(doc_path, 'r', encoding='utf-8') as f:
        text = f.read()
    coaching = {}
    
    # 1. From Tables
    for line in text.split('\n'):
        ls = line.strip()
        if ls.startswith('|') and not ls.startswith('|-') and not ls.startswith('|:-') and not ls.startswith('|:--'):
            parts = [x.strip().replace('**', '') for x in ls.split('|')[1:-1]]
            if len(parts) >= 3:
                field = parts[0].lower()
                val_col = parts[2]
                m = re.search(r'\b\d+\b', val_col)
                if m:
                    v = int(m.group())
                    if 'active system' in field or '战术体系' in field: coaching['active_system'] = v
                    elif 'help defense' in field or '协防' in field: coaching['help_defense'] = v
                    elif 'run play' in field or '战术执行' in field: coaching['run_play_tendency'] = v
                    elif 'bench depth' in field or '轮换深度' in field: coaching['bench_depth'] = v
                    elif 'bench utilization' in field or '替补使用' in field or '轮换使用' in field: coaching['bench_utilization'] = v
                    elif 'zone' in field or '联防' in field: coaching['zone_usage'] = v

    # 2. From Bullet points
    for line in text.split('\n'):
        ls = line.strip()
        # Find target value after arrow or colon
        arrow = re.search(r'\\rightarrow|→|->|提升至|降至', ls)
        target_part = ls[arrow.end():] if arrow else ls
        has_arrow = bool(arrow)
        
        # active system
        if any(k in ls.lower() for k in ['activesystem', 'active system', '战术体系']):
            if has_arrow or 'active_system' not in coaching:
                m = re.search(r'\b\d+\b', target_part)
                if m: coaching['active_system'] = int(m.group())
            
        # run play tendency
        if any(k in ls.lower() for k in ['runplaytendency', 'run play tendency', '战术执行率', '战术跑位率']):
            if has_arrow or 'run_play_tendency' not in coaching:
                m = re.search(r'\b\d+\b', target_part)
                if m: coaching['run_play_tendency'] = int(m.group())
            
        # help defense
        if any(k in ls.lower() for k in ['helpdefense', 'help defense', '协防智商']):
            if has_arrow or 'help_defense' not in coaching:
                m = re.search(r'\b\d+\b', target_part)
                if m: coaching['help_defense'] = int(m.group())
            
        # bench depth
        if any(k in ls.lower() for k in ['benchdepth', 'bench depth', '轮换深度']):
            if has_arrow or 'bench_depth' not in coaching:
                m = re.search(r'\b\d+\b', target_part)
                if m: coaching['bench_depth'] = int(m.group())
            
        # bench utilization
        if any(k in ls.lower() for k in ['benchutilization', 'bench utilization', '替补使用率', '轮换使用率']):
            if has_arrow or 'bench_utilization' not in coaching:
                m = re.search(r'\b\d+\b', target_part)
                if m: coaching['bench_utilization'] = int(m.group())
            
        # zone usage
        if any(k in ls.lower() for k in ['zoneusage', 'zone usage', '联防频率']):
            if has_arrow or 'zone_usage' not in coaching:
                m = re.search(r'\b\d+\b', target_part)
                if m: coaching['zone_usage'] = int(m.group())
            
    return coaching

# Offsets dictionary according to Doc 43 native specification
FIELD_OFFSETS = {
    'touches': 1177,
    'dish_to_open_man': 1176,
    'roll_vs_pop': 1184,
    'play_discipline': 1181,
    'shot_three': 1182,
    'shot_tendency': 1112,
    'drive_tendency': 1155,
    'attack_strong': 1175,
    'contest_shot': 1207,
    'block_shot': 1208,
    'on_ball_steal': 1206,
    'pass_perception': 1204
}

COACH_OFFSETS = {
    'active_system': (267, 'COACHDATA'),
    'preferred_system': (266, 'COACHDATA'),
    'bench_depth': (222, 'COACHDATA'),
    'bench_utilization': (312, 'COACHDATA'),
    'run_play_tendency': (224, 'COACHDATA'),
    'help_defense': (330, 'COACHDATA'),
    'zone_usage': (226, 'COACHDATA')
}

generated_files = []

for idx, (tid, abbr, tname, doc_file) in enumerate(team_order, 1):
    doc_path = os.path.join(docs_dir, doc_file)
    
    # 1. Coaching parameters: Start with 150-player spec baseline, Doc strictly overrides
    t_150 = spec_150.get(str(tid), {})
    c_150 = t_150.get('coaching_system', {})
    
    final_coaching = {}
    if c_150:
        if 'active_system_id' in c_150: final_coaching['active_system'] = c_150['active_system_id']
        if 'run_play_tendency' in c_150: final_coaching['run_play_tendency'] = c_150['run_play_tendency']
        if 'help_defense' in c_150: final_coaching['help_defense'] = c_150['help_defense']
        if 'bench_depth' in c_150: final_coaching['bench_depth'] = c_150['bench_depth']
        if 'bench_utilization' in c_150: final_coaching['bench_utilization'] = c_150['bench_utilization']

    doc_coaching = parse_coaching_exact(doc_path)
    for k, v in doc_coaching.items():
        if v is not None:
            final_coaching[k] = v

    coaching_writes = []
    for c_field, c_val in final_coaching.items():
        if c_field in COACH_OFFSETS:
            off, blk = COACH_OFFSETS[c_field]
            coaching_writes.append({
                'field_name': c_field,
                'target_block': blk,
                'offset': off,
                'type': 'uint8',
                'val_raw': c_val,
                'description': f"{c_field}: {c_val}"
            })

    # 2. Players unification: Slot-based determinism against clean database
    doc_players = parse_doc_table_players(doc_path)
    team_players = {} # slot -> dict
    
    for dp in doc_players:
        slot_str = dp['slot_str'].replace('*', '').strip()
        m = re.search(r'\b\d+\b', slot_str)
        if not m: continue
        slot = int(m.group())
        if (tid, slot) not in db_roster: continue
        p_name_db, fid = db_roster[(tid, slot)]
        
        # Parse tendencies from doc
        tendencies = {}
        def get_num(s):
            m_n = re.search(r'\b\d+\b', s.replace('*', ''))
            return int(m_n.group()) if m_n else None
            
        t_val = get_num(dp['touches_str'])
        if t_val is not None: tendencies['touches'] = t_val
        d_val = get_num(dp['dish_str'])
        if d_val is not None: tendencies['dish_to_open_man'] = d_val
        disc_val = get_num(dp['disc_str'])
        if disc_val is not None: tendencies['play_discipline'] = disc_val
        rp_val = get_num(dp['roll_pop_str'])
        if rp_val is not None: tendencies['roll_vs_pop'] = rp_val
        s3_val = get_num(dp['shot_3_str'])
        if s3_val is not None: tendencies['shot_three'] = s3_val
        
        # Initiator flag
        init_val = None
        if 'True' in dp['init_str'] or '是' in dp['init_str'] or '1' in dp['init_str']: init_val = 1
        elif 'False' in dp['init_str'] or '否' in dp['init_str'] or '0' in dp['init_str']: init_val = 0
        
        # Play types
        pt_m = re.findall(r'\b\d+\b', dp['play_types_str'])
        play_types = [int(x) for x in pt_m[:4]] if len(pt_m) >= 4 else None
        
        team_players[slot] = {
            'player_name': p_name_db,
            'roster_index': slot,
            'cyberface_id': fid,
            'tendencies': tendencies,
            'initiator': init_val,
            'play_types': play_types,
            'source': 'DOC'
        }

    # Merge 150-player spec baseline for this team (if player is on clean roster)
    p_150_tend = t_150.get('player_tendencies_tuning', {})
    p_150_pt = t_150.get('play_types_and_initiator', {})
    
    for p_name_150, tend_150 in p_150_tend.items():
        slot_150 = db_player_name_to_slot.get((tid, p_name_150.lower().strip()))
        if slot_150 is None:
            # Traded away or not on this team in clean save
            continue
            
        if slot_150 not in team_players:
            p_name_db, fid = db_roster[(tid, slot_150)]
            team_players[slot_150] = {
                'player_name': p_name_db,
                'roster_index': slot_150,
                'cyberface_id': fid,
                'tendencies': {},
                'initiator': None,
                'play_types': None,
                'source': '150_SPEC'
            }
            
        target = team_players[slot_150]
        # Merge tendencies: Doc strictly overrides 150-player spec
        for fld, val in tend_150.items():
            if fld not in target['tendencies']:
                target['tendencies'][fld] = val
                
    for p_name_150, pt_150 in p_150_pt.items():
        slot_150 = db_player_name_to_slot.get((tid, p_name_150.lower().strip()))
        if slot_150 is None or slot_150 not in team_players:
            continue
        target = team_players[slot_150]
        if target['initiator'] is None and 'initiator' in pt_150:
            target['initiator'] = 1 if pt_150['initiator'] else 0
        if target['play_types'] is None and 'slots' in pt_150:
            slots_num = []
            for s in pt_150['slots']:
                m = re.search(r'\((\d+)\)', s)
                if m: slots_num.append(int(m.group(1)))
            if len(slots_num) >= 4:
                target['play_types'] = slots_num[:4]

    # Format player writes (Doc 43 protocol compliant, delta only)
    player_writes = []
    for slot in sorted(team_players.keys()):
        p_data = team_players[slot]
        
        mods = []
        for fld, val in p_data['tendencies'].items():
            if fld in FIELD_OFFSETS:
                mods.append({
                    'field': fld,
                    'target_block': 'PLAYER_STRUCT',
                    'offset': FIELD_OFFSETS[fld],
                    'type': 'uint8',
                    'val_raw': val,
                    'description': f"{fld}: {val}"
                })
                
        p_write_obj = {
            'player_name': p_data['player_name'],
            'roster_index': slot,
            'cyberface_id': p_data['cyberface_id']
        }
        
        if p_data['initiator'] is not None or p_data['play_types'] is not None:
            p_write_obj['tactical_playbook'] = {}
            if p_data['initiator'] is not None:
                p_write_obj['tactical_playbook']['is_play_initiator'] = p_data['initiator']
            if p_data['play_types'] is not None:
                p_write_obj['tactical_playbook']['play_types'] = p_data['play_types']
                
        p_write_obj['modifications'] = mods
        player_writes.append(p_write_obj)

    final_spec = {
        'protocol_version': 'v2.0_full_dimensional_native_mod',
        'team_id': tid,
        'team_abbr': abbr,
        'team_name': tname,
        'source_research_doc': doc_file,
        'conflict_resolution': 'STRICT_LATEST_RESEARCH_DOC_PRIORITY',
        'coaching_writes': coaching_writes,
        'player_writes': player_writes
    }

    fname = f"{tid:02d}_{abbr}_native_mod.json"
    p_local = os.path.join(out_dir_local, fname)
    p_export = os.path.join(out_dir_export, fname)

    with open(p_local, 'w', encoding='utf-8') as f:
        json.dump(final_spec, f, indent=2, ensure_ascii=False)
    with open(p_export, 'w', encoding='utf-8') as f:
        json.dump(final_spec, f, indent=2, ensure_ascii=False)

    size_kb = os.path.getsize(p_local) / 1024
    generated_files.append((fname, size_kb, len(coaching_writes), len(player_writes)))
    print(f"[{idx:02d}/30] Generated {fname}: {size_kb:.2f} KB | coaching_writes={len(coaching_writes)}, players={len(player_writes)}")

print("\nSuccessfully generated all 30 clean delta single-team execution files with dynamic table headers!")
