import json, os, shutil

# 1. Build phx_tactical_execution_ready.json
phx_spec = {
    'team_id': 26,
    'team_abbr': 'PHX',
    'team_name': 'Phoenix Suns',
    'tactical_system': 'Pace and Space / Spread Pick-and-Roll & 0.5-Second Decision Engine',
    'offensive_pace': 'Controlled Half-Court P&R Maestro & 0.5s Ball Movement (Tempo: 70)',
    'defensive_anchor': 'Mikal Bridges (POA DPOY Lock) & Deandre Ayton (Drop/Catch Anchor) & Jae Crowder (Bruising Forward)',
    'coaching_modifications': {
        'active_system': 2,
        'preferred_system': 2,
        'help_defense': 80,
        'run_play_tendency': 75,
        'bench_depth': 9,
        'bench_utilization': 50,
        'poe_offense': 4,
        'poe_offense_tempo': 8,
        'poe_offense_transition': 12,
        'poe_defense': 15,
        'poe_defense_physicality': 18,
        'poe_defense_rebound': 19,
        'zone_usage': 3,
        'tempo': 70
    },
    'freelance_sets': [
        {'slot': 1, 'type_name': 'PACE', 'type_id': 21, 'description': '主选自由跑位: 21 (现代空间拉开站位)'},
        {'slot': 2, 'type_name': 'TWENTY_ONE_DELAY', 'type_id': 28, 'description': '次选自由跑位: 28 (21 Delay 边线手递手延迟落位)'},
        {'slot': 3, 'type_name': 'FLOW', 'type_id': 18, 'description': '备选自由跑位: 18 (强弱侧流动进攻)'},
        {'slot': 4, 'type_name': 'FOUR_OUT', 'type_id': 5, 'description': '备选自由跑位: 5 (一内四外空间体系)'}
    ],
    'scoring_options': [
        {'option_slot': 1, 'player_name': 'Devin Booker', 'player_id': 3487},
        {'option_slot': 2, 'player_name': 'Chris Paul', 'player_id': 2029},
        {'option_slot': 3, 'player_name': 'Deandre Ayton', 'player_id': 4153}
    ],
    'player_modifications': [
        {
            'roster_slot': 0,
            'player_name': 'Chris Paul',
            'role': 'Starters PG / Point God Floor General & Clutch Mid-Range Maestro',
            'touches': 78,
            'dish': 90,
            'play_discipline': 90,
            'roll_pop': 0,
            'shot_three': 75,
            'is_initiator': True,
            'play_types': [4, 13, 1, 12]
        },
        {
            'roster_slot': 1,
            'player_name': 'Devin Booker',
            'role': 'Starters SG / Primary Scoring Assassin & Three-Level Closer',
            'touches': 85,
            'dish': 45,
            'play_discipline': 75,
            'roll_pop': 20,
            'shot_three': 85,
            'is_initiator': False,
            'play_types': [4, 1, 13, 14]
        },
        {
            'roster_slot': 2,
            'player_name': 'Mikal Bridges',
            'role': 'Starters SF / Iron Man DPOY-Caliber Lock & Corner 3&D Weapon',
            'touches': 55,
            'dish': 35,
            'play_discipline': 95,
            'roll_pop': 25,
            'shot_three': 88,
            'is_initiator': False,
            'play_types': [14, 11, 6, 0]
        },
        {
            'roster_slot': 3,
            'player_name': 'Jae Crowder',
            'role': 'Starters PF / Corner Sniper & Bruising Physical Enforcer',
            'touches': 38,
            'dish': 45,
            'play_discipline': 95,
            'roll_pop': 0,
            'shot_three': 85,
            'is_initiator': False,
            'play_types': [14, 11, 0, 0]
        },
        {
            'roster_slot': 4,
            'player_name': 'Deandre Ayton',
            'role': 'Starters C / Pick & Roll Lob Threat & Paint Anchor (RollPop=15)',
            'touches': 62,
            'dish': 40,
            'play_discipline': 85,
            'roll_pop': 15,
            'shot_three': 20,
            'is_initiator': False,
            'play_types': [7, 8, 11, 13]
        },
        {
            'roster_slot': 5,
            'player_name': 'Cameron Johnson',
            'role': 'Bench 6th Man SF/PF / Elite Sharpshooter & Microwave Gunner',
            'touches': 65,
            'dish': 35,
            'play_discipline': 90,
            'roll_pop': 10,
            'shot_three': 92,
            'is_initiator': False,
            'play_types': [14, 11, 12, 0]
        },
        {
            'roster_slot': 7,
            'player_name': 'Cameron Payne',
            'role': 'Bench PG / Secondary Play Initiator & Up-Tempo Rim Attacker',
            'touches': 58,
            'dish': 75,
            'play_discipline': 75,
            'roll_pop': 0,
            'shot_three': 80,
            'is_initiator': True,
            'play_types': [4, 1, 14, 0]
        },
        {
            'roster_slot': 8,
            'player_name': 'Landry Shamet',
            'role': 'Bench SG / Off-Ball Movement Shooter',
            'touches': 45,
            'dish': 35,
            'play_discipline': 85,
            'roll_pop': 10,
            'shot_three': 85,
            'is_initiator': False,
            'play_types': [14, 12, 4, 0]
        },
        {
            'roster_slot': 9,
            'player_name': 'JaVale McGee',
            'role': 'Bench C / High-Energy Rim Runner, Lob Catcher & Shot Blocker',
            'touches': 42,
            'dish': 35,
            'play_discipline': 95,
            'roll_pop': 10,
            'shot_three': 0,
            'is_initiator': False,
            'play_types': [7, 11, 0, 0]
        },
        {
            'roster_slot': 6,
            'player_name': 'Dario Saric',
            'role': 'Bench Big PF/C / Stretch Playmaker & High Post Facilitator',
            'touches': 36,
            'dish': 60,
            'play_discipline': 85,
            'roll_pop': 75,
            'shot_three': 80,
            'is_initiator': False,
            'play_types': [14, 7, 11, 8]
        },
        {
            'roster_slot': 12,
            'player_name': 'Jalen Smith',
            'role': 'Bench PF/C / Young Athletic Big & Rim Crasher',
            'touches': 30,
            'dish': 30,
            'play_discipline': 80,
            'roll_pop': 30,
            'shot_three': 70,
            'is_initiator': False,
            'play_types': [11, 7, 14, 0]
        },
        {
            'roster_slot': 10,
            'player_name': 'Elfrid Payton',
            'role': 'Reserve PG / Traditional Penetration Guard',
            'touches': 20,
            'dish': 65,
            'play_discipline': 80,
            'roll_pop': 0,
            'shot_three': 50,
            'is_initiator': True,
            'play_types': [4, 1, 11, 0]
        },
        {
            'roster_slot': 11,
            'player_name': 'Frank Kaminsky',
            'role': 'Reserve C / Stretch-5 Perimeter Pop Big',
            'touches': 20,
            'dish': 50,
            'play_discipline': 90,
            'roll_pop': 70,
            'shot_three': 75,
            'is_initiator': False,
            'play_types': [14, 7, 11, 8]
        },
        {
            'roster_slot': 13,
            'player_name': 'Abdel Nader',
            'role': 'Reserve Wing / Slashing Defender',
            'touches': 15,
            'dish': 25,
            'play_discipline': 80,
            'roll_pop': 0,
            'shot_three': 70,
            'is_initiator': False,
            'play_types': [14, 11, 0, 0]
        },
        {
            'roster_slot': 21,
            'player_name': 'Chandler Hutchison',
            'role': 'Reserve Wing / Athletic Cutter',
            'touches': 15,
            'dish': 30,
            'play_discipline': 85,
            'roll_pop': 25,
            'shot_three': 65,
            'is_initiator': False,
            'play_types': [11, 14, 0, 0]
        }
    ]
}

local_phx_path = r'08_Domain_Applications/Antigravity_GM_Engine/database/tactics/phx_tactical_execution_ready.json'
with open(local_phx_path, 'w', encoding='utf-8') as f:
    json.dump(phx_spec, f, indent=2, ensure_ascii=False)
print('Saved local spec:', local_phx_path)

mirror_phx_path = r'C:\nba2k22\exports\phx_tactical_execution_ready.json'
shutil.copyfile(local_phx_path, mirror_phx_path)
print('Mirrored to:', mirror_phx_path)

# Mirror Doc 54 to exports
doc_src = r'08_Domain_Applications/Antigravity_GM_Engine/docs/54_PHX_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'
doc_dst = r'C:\nba2k22\exports\54_PHX_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md'
shutil.copyfile(doc_src, doc_dst)
print('Mirrored Doc 54 to:', doc_dst)

# 2. Update BATCH_04_PACIFIC_FULL_DIMENSIONAL_SPEC.json
batch_path = r'08_Domain_Applications/Antigravity_GM_Engine/database/tactics/BATCH_04_PACIFIC_FULL_DIMENSIONAL_SPEC.json'
if os.path.exists(batch_path):
    with open(batch_path, 'r', encoding='utf-8') as f:
        batch = json.load(f)
    t = batch.get('teams', {}).get('26', {})
    cm = phx_spec['coaching_modifications']
    pref_sys = cm.get('preferred_system', cm['active_system'])
    t['coaching_system'] = {
        'active_system': phx_spec['tactical_system'],
        'active_system_id': cm['active_system'],
        'preferred_system': pref_sys,
        'preferred_system_id': pref_sys,
        'freelance_sets': [fs['type_id'] for fs in phx_spec.get('freelance_sets', [])],
        'run_play_tendency': cm['run_play_tendency'],
        'help_defense': cm['help_defense'],
        'bench_depth': cm['bench_depth'],
        'bench_utilization': cm['bench_utilization'],
        'zone_usage': cm.get('zone_usage', 3),
        'tempo': cm.get('tempo', 70),
        'poe_offense': f"ID_{cm['poe_offense']}",
        'poe_offense_tempo': f"ID_{cm['poe_offense_tempo']}",
        'poe_offense_rebound': f"ID_{cm.get('poe_offense_transition', 12)}",
        'poe_defense': f"ID_{cm['poe_defense']}",
        'poe_defense_physicality': f"ID_{cm['poe_defense_physicality']}",
        'poe_defense_rebound': f"ID_{cm['poe_defense_rebound']}"
    }
    pti = {}
    ptend = {}
    for pm in phx_spec['player_modifications']:
        pname = pm['player_name']
        pti[pname] = {
            'is_play_initiator': 1 if pm['is_initiator'] else 0,
            'play_types': pm['play_types'],
            'roster_slot': pm['roster_slot'],
            'role': pm.get('role', '')
        }
        ptend[pname] = {
            'touches': pm['touches'],
            'dish_to_open_man': pm['dish'],
            'play_discipline': pm['play_discipline'],
            'roll_vs_pop': pm['roll_pop'],
            'shot_three': pm['shot_three']
        }
    t['play_types_and_initiator'] = pti
    t['player_tendencies_tuning'] = ptend
    t['player_modifications'] = phx_spec['player_modifications']
    t['coaching_modifications'] = phx_spec['coaching_modifications']
    batch['teams']['26'] = t
    with open(batch_path, 'w', encoding='utf-8') as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    print('Updated batch file:', batch_path)
    shutil.copyfile(batch_path, r'C:\nba2k22\exports\BATCH_04_PACIFIC_FULL_DIMENSIONAL_SPEC.json')
    print('Mirrored batch file to exports')

# 3. Update cycle_02_30_teams_realism_execution_ready.json
cycle_path = r'08_Domain_Applications/Antigravity_GM_Engine/database/tactics/cycle_02_30_teams_realism_execution_ready.json'
with open(cycle_path, 'r', encoding='utf-8') as f:
    cycle_data = json.load(f)

for batch in cycle_data.get('batches', []):
    for t in batch.get('teams', []):
        if t.get('team_id') == 26:
            cm = phx_spec['coaching_modifications']
            pref_sys = cm.get('preferred_system', cm['active_system'])
            t['coaching_writes'] = [
                {'field_name': 'active_system', 'target_block': 'COACHDATA', 'offset': 267, 'val_raw': cm['active_system'], 'description': f"战术系统: {cm['active_system']}"},
                {'field_name': 'preferred_system', 'target_block': 'COACHDATA', 'offset': 266, 'val_raw': pref_sys, 'description': f"偏好战术系统: {pref_sys}"},
                {'field_name': 'bench_depth', 'target_block': 'COACHDATA', 'offset': 222, 'val_raw': cm['bench_depth'], 'description': f"轮换人数: {cm['bench_depth']}人"},
                {'field_name': 'bench_utilization', 'target_block': 'COACHDATA', 'offset': 312, 'val_raw': cm['bench_utilization'], 'description': f"替补使用率: {cm['bench_utilization']}"},
                {'field_name': 'run_play_tendency', 'target_block': 'COACHDATA', 'offset': 224, 'val_raw': cm['run_play_tendency'], 'description': f"战术执行倾向: {cm['run_play_tendency']}%"},
                {'field_name': 'help_defense', 'target_block': 'COACHDATA', 'offset': 330, 'val_raw': cm['help_defense'], 'description': f"全队协防倾向: {cm['help_defense']}%"},
                {'field_name': 'zone_usage', 'target_block': 'COACHDATA', 'offset': 226, 'val_raw': cm.get('zone_usage', 3), 'description': f"区域联防频率: {cm.get('zone_usage', 3)}%"}
            ]
            t['coaching_modifications'] = cm
            t['player_modifications'] = phx_spec['player_modifications']
            
            pwrites = []
            for pm in phx_spec['player_modifications']:
                pwrites.append({
                    'player_name': pm['player_name'],
                    'roster_index': pm['roster_slot'],
                    'tactical_playbook': {
                        'is_play_initiator': 1 if pm['is_initiator'] else 0,
                        'play_types': pm['play_types']
                    },
                    'modifications': [
                        {'field': 'touches', 'offset': 1177, 'val_raw': pm['touches'], 'type': 'uint8', 'description': f"触球呼叫倾向: {pm['touches']}"},
                        {'field': 'dish_to_open_man', 'offset': 1176, 'val_raw': pm['dish'], 'type': 'uint8', 'description': f"分球意愿: {pm['dish']}"},
                        {'field': 'roll_vs_pop', 'offset': 1184, 'val_raw': pm['roll_pop'], 'type': 'uint8', 'description': f"顺下外弹倾向: {pm['roll_pop']}"},
                        {'field': 'play_discipline', 'offset': 1181, 'val_raw': pm['play_discipline'], 'type': 'uint8', 'description': f"战术纪律: {pm['play_discipline']}"},
                        {'field': 'shot_three', 'offset': 1182, 'val_raw': pm['shot_three'], 'type': 'uint8', 'description': f"三分出手倾向: {pm['shot_three']}"}
                    ]
                })
            t['player_writes'] = pwrites
            print(f"Updated Team 26 PHX in cycle_02 with {len(pwrites)} players!")

with open(cycle_path, 'w', encoding='utf-8') as f:
    json.dump(cycle_data, f, indent=2, ensure_ascii=False)
print('Updated cycle_02 file:', cycle_path)
shutil.copyfile(cycle_path, r'C:\nba2k22\exports\cycle_02_30_teams_realism_execution_ready.json')
print('Mirrored cycle_02 to exports')
