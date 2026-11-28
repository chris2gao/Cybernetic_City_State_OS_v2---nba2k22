#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intangibles_rotation_calculator.py
=============================================================================
NBA 2K22 Automated Team-Relative Rotation & Intangibles Inversion Calculator
=============================================================================
Usage Examples:
  # 1. CLI with inline minutes:
  python intangibles_rotation_calculator.py --team DAL --minutes "Luka:34, Brunson:30, Bullock:26, Powell:24, Kleber:22, Dinwiddie:22, Green:18, Bertans:16, Ntilikina:12, Burke:8, Boban:8"

  # 2. CLI with team abbreviation and rotation size (auto-balanced distribution):
  python intangibles_rotation_calculator.py --team GSW --rotation-size 10

  # 3. CLI from JSON spec or text file:
  python intangibles_rotation_calculator.py --team LAL --minutes-file my_lakers_rotation.json

  # 4. Interactive mode (prompts for team and minutes):
  python intangibles_rotation_calculator.py --interactive
=============================================================================
"""

import sys
import os
import argparse
import sqlite3
import json
import re
import numpy as np
from typing import Dict, List, Tuple, Optional, Any

DEFAULT_DB_PATH = r'C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite'

# ---------------------------------------------------------------------------
# 1. 2K Positional Core Weights (excluding durability, potential, intangibles)
# ---------------------------------------------------------------------------
POSITIONAL_CORE_WEIGHTS = {
    'PG': {
        'ball_control': 2.5, 'speed_with_ball': 2.0, 'passing_accuracy': 2.0, 'passing_iq': 1.5, 'passing_vision': 1.5,
        '3pt_shot': 2.0, 'mid_range_shot': 1.5, 'driving_layup': 1.5, 'speed': 1.8, 'acceleration': 1.5,
        'perimeter_defense': 1.8, 'lateral_quickness': 1.5, 'steal': 1.2, 'offensive_consistency': 1.5, 'shot_iq': 1.5
    },
    'SG': {
        '3pt_shot': 2.5, 'mid_range_shot': 2.2, 'driving_layup': 1.8, 'driving_dunk': 1.5, 'ball_control': 1.8,
        'speed': 1.8, 'acceleration': 1.5, 'perimeter_defense': 2.0, 'lateral_quickness': 1.8, 'offensive_consistency': 1.8,
        'shot_iq': 1.5, 'defensive_consistency': 1.5, 'hands': 1.0
    },
    'SF': {
        '3pt_shot': 2.0, 'mid_range_shot': 1.8, 'driving_layup': 1.8, 'driving_dunk': 1.8, 'perimeter_defense': 2.0,
        'interior_defense': 1.5, 'defensive_rebound': 1.5, 'speed': 1.8, 'lateral_quickness': 1.8, 'strength': 1.5,
        'offensive_consistency': 1.8, 'defensive_consistency': 1.5, 'shot_contest': 1.5
    },
    'PF': {
        'interior_defense': 2.5, 'defensive_rebound': 2.5, 'offensive_rebound': 1.8, 'block': 2.0, 'shot_close': 2.0,
        'strength': 2.2, 'mid_range_shot': 1.5, '3pt_shot': 1.2, 'post_moves': 1.5, 'post_fadeaway': 1.2,
        'shot_contest': 1.8, 'defensive_consistency': 1.8, 'offensive_consistency': 1.5
    },
    'C': {
        'interior_defense': 3.0, 'defensive_rebound': 3.0, 'offensive_rebound': 2.2, 'block': 2.5, 'shot_close': 2.5,
        'strength': 2.8, 'standing_dunk': 2.0, 'post_hook': 1.5, 'post_moves': 1.5, 'shot_contest': 2.0,
        'defensive_consistency': 2.0, 'offensive_consistency': 1.5
    }
}

INTA_KAPPA = 0.082   # Delta OVR per 1 unit of Intangibles (range [25, 99])
MINS_PER_OVR = 1.35  # Minutes per 1 unit of intra-team Effective OVR gap

# ---------------------------------------------------------------------------
# 2. Resilient Name & Team Matching Helpers
# ---------------------------------------------------------------------------
def normalize_string(s: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

def match_player_name(query: str, candidate_names: List[str]) -> Optional[str]:
    """Matches user query to canonical 2K database player names resiliently."""
    q_clean = query.strip()
    if not q_clean:
        return None
    
    # 1. Exact match (case insensitive)
    for c in candidate_names:
        if c.lower() == q_clean.lower():
            return c
            
    # 2. Normalized match (without spaces, dots, hyphens)
    q_norm = normalize_string(q_clean)
    for c in candidate_names:
        if normalize_string(c) == q_norm:
            return c
            
    # 3. Substring match
    for c in candidate_names:
        c_norm = normalize_string(c)
        if q_norm in c_norm or c_norm in q_norm:
            return c
            
    # 4. Token / Last name match
    q_tokens = re.findall(r'[a-zA-Z0-9]+', q_clean.lower())
    for tok in reversed(q_tokens):
        if len(tok) < 3:
            continue
        for c in candidate_names:
            c_tokens = [t.lower() for t in re.findall(r'[a-zA-Z0-9]+', c)]
            if any(tok == ct or tok in ct or ct in tok for ct in c_tokens):
                return c
                
    return None

def resolve_team(db_conn: sqlite3.Connection, query: Any) -> Optional[Tuple[int, str, str, str]]:
    """Resolves team by id, abbreviation, city, or name."""
    cur = db_conn.cursor()
    cur.execute("SELECT team_id, abbreviation, city, name FROM teams")
    teams = cur.fetchall()
    
    # If query is integer ID
    try:
        qid = int(query)
        for t in teams:
            if t[0] == qid:
                return t
    except ValueError:
        pass
        
    q_str = str(query).strip().lower()
    q_norm = normalize_string(q_str)
    
    # Match abbreviation
    for t in teams:
        if t[1].lower() == q_str:
            return t
            
    # Match name or city
    for t in teams:
        if q_str in t[3].lower() or q_str in t[2].lower() or q_norm in normalize_string(f"{t[2]} {t[3]}"):
            return t
            
    return None

# ---------------------------------------------------------------------------
# 3. Mathematical Formula: Base OVR & Relative Intangibles Inversion
# ---------------------------------------------------------------------------
def compute_player_ability_metrics(attrs: dict, pos: str) -> Tuple[float, float, float]:
    """
    Computes:
    - total_bball_sum: Raw sum of all 37 non-durability basketball attributes
    - composite_ability: Positional weighted composite index
    - base_ovr: Estimated Base OVR (before Intangibles offset)
    """
    pos_weights = POSITIONAL_CORE_WEIGHTS.get(pos, POSITIONAL_CORE_WEIGHTS['SF'])
    
    # 1. Positional core score
    core_sum = sum(attrs.get(k, {}).get('value', 50) * w for k, w in pos_weights.items())
    core_score = core_sum / sum(pos_weights.values())
    
    # 2. Basketball performance attributes
    bball_attrs = [
        v.get('value', 50) for k, v in attrs.items()
        if 'durability' not in k and k not in ('potential', 'intangibles') and isinstance(v, dict)
    ]
    total_bball_sum = float(sum(bball_attrs))
    gen_score = float(np.mean(bball_attrs)) if bball_attrs else 50.0
    
    # 3. Composite ability
    composite_ability = 0.75 * core_score + 0.25 * gen_score
    
    # 4. Projected Base OVR
    base_ovr = 1.15 * composite_ability - 12.0
    base_ovr = float(np.clip(base_ovr, 60.0, 97.0))
    
    return total_bball_sum, composite_ability, base_ovr

def invert_team_intangibles(
    roster_records: List[dict],
    target_minutes_map: Dict[str, float]
) -> Tuple[List[dict], float]:
    """
    Executes the team-relative inversion:
    Target Minutes -> Effective OVR Ladder -> Intangibles (25 to 99)
    """
    total_minutes = sum(target_minutes_map.values())
    
    # Combine roster info with target minutes
    processed = []
    for p in roster_records:
        name = p['name']
        m = target_minutes_map.get(name, 0.0)
        processed.append({
            'name': name,
            'position': p['position'],
            'total_attr_sum': p['total_attr_sum'],
            'base_ovr': p['base_ovr'],
            'current_intangibles': p['current_intangibles'],
            'target_minutes': m
        })
        
    # Sort by target minutes descending
    processed.sort(key=lambda x: x['target_minutes'], reverse=True)
    
    # Star Anchor Point
    top_p = processed[0]
    top_base = top_p['base_ovr']
    top_anchor = max(top_base, 88.0) if top_base > 85.0 else (top_base + 3.0)
    
    results = []
    for rank, p in enumerate(processed, 1):
        m = p['target_minutes']
        if m > 0.0:
            deficit = top_p['target_minutes'] - m
            target_eff_ovr = top_anchor - (deficit / MINS_PER_OVR)
        else:
            # Pushed below active rotation
            target_eff_ovr = top_anchor - (top_p['target_minutes'] / MINS_PER_OVR) - 4.5
            
        # Invert intangibles: target_eff_ovr = base_ovr + (I - 50) * INTA_KAPPA
        needed_delta = target_eff_ovr - p['base_ovr']
        raw_inta = 50.0 + (needed_delta / INTA_KAPPA)
        new_inta = int(round(np.clip(raw_inta, 25.0, 99.0)))
        
        # Realized effective OVR
        realized_eff_ovr = p['base_ovr'] + (new_inta - 50.0) * INTA_KAPPA
        
        results.append({
            'rank': rank,
            'name': p['name'],
            'position': p['position'],
            'target_minutes': m,
            'total_attr_sum': round(p['total_attr_sum'], 1),
            'base_ovr': round(p['base_ovr'], 1),
            'target_eff_ovr': round(target_eff_ovr, 1),
            'current_intangibles': p['current_intangibles'],
            'recommended_intangibles': new_inta,
            'intangibles_delta': new_inta - p['current_intangibles'],
            'realized_eff_ovr': round(realized_eff_ovr, 1)
        })
        
    return results, total_minutes

# ---------------------------------------------------------------------------
# 4. Main Engine & Data Retrieval API
# ---------------------------------------------------------------------------
def calculate_team_intangibles(
    team_query: Any,
    target_minutes: Optional[Dict[str, float]] = None,
    rotation_size: Optional[int] = None,
    db_path: str = DEFAULT_DB_PATH,
    auto_normalize_240: bool = False
) -> Dict[str, Any]:
    """
    Main function:
    1. Loads team roster and 50+ attributes from SQLite.
    2. Aligns user target minutes or generates an auto-balanced template.
    3. Solves for exact Intangibles values (25-99).
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")
        
    conn = sqlite3.connect(db_path)
    team_info = resolve_team(conn, team_query)
    if not team_info:
        conn.close()
        raise ValueError(f"Could not resolve team matching: '{team_query}'")
        
    tid, abbr, city, name = team_info
    cur = conn.cursor()
    
    cur.execute("""
    SELECT d.player_name, m.position, d.details_json
    FROM player_source_details d
    JOIN player_monthly_stats m ON d.team_id = m.team_id AND d.player_name = m.player_name AND d.snapshot_id = m.snapshot_id
    WHERE d.team_id = ? AND d.snapshot_id = (SELECT snapshot_id FROM monthly_snapshots ORDER BY snapshot_id DESC LIMIT 1)
    GROUP BY d.player_name
    """, (tid,))
    
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        raise ValueError(f"No player records found for team {abbr} (ID: {tid}).")
        
    roster_records = []
    canonical_names = []
    for pname, pos, det_str in rows:
        det = json.loads(det_str)
        attrs = det.get('attributes', {})
        curr_inta = attrs.get('intangibles', {}).get('value', 50)
        tot_sum, composite, base_ovr = compute_player_ability_metrics(attrs, pos)
        
        roster_records.append({
            'name': pname,
            'position': pos,
            'total_attr_sum': tot_sum,
            'composite_ability': composite,
            'base_ovr': base_ovr,
            'current_intangibles': curr_inta
        })
        canonical_names.append(pname)
        
    # Match user minutes map to canonical names
    aligned_minutes = {}
    if target_minutes:
        for q_name, mins in target_minutes.items():
            matched = match_player_name(q_name, canonical_names)
            if matched:
                aligned_minutes[matched] = float(mins)
            else:
                print(f"[Warning] Player '{q_name}' not matched on {abbr} roster. Skipped.", file=sys.stderr)
    elif rotation_size:
        # Generate auto-balanced standard minutes distribution
        # Sort by base OVR descending
        roster_records.sort(key=lambda x: x['base_ovr'], reverse=True)
        rot_n = max(8, min(12, rotation_size))
        # Standard NBA curve template for rot_n
        if rot_n == 8:
            mins_curve = [35.0, 34.0, 32.0, 30.0, 29.0, 28.0, 26.0, 26.0]
        elif rot_n == 9:
            mins_curve = [34.0, 33.0, 31.0, 29.0, 28.0, 26.0, 24.0, 20.0, 15.0]
        elif rot_n == 10:
            mins_curve = [34.0, 32.0, 30.0, 28.0, 26.0, 24.0, 22.0, 18.0, 14.0, 12.0]
        elif rot_n == 11:
            mins_curve = [33.0, 31.0, 29.0, 27.0, 25.0, 23.0, 21.0, 18.0, 14.0, 11.0, 8.0]
        else: # 12
            mins_curve = [32.0, 30.0, 28.0, 26.0, 24.0, 22.0, 20.0, 18.0, 14.0, 12.0, 8.0, 6.0]
            
        for idx, p in enumerate(roster_records):
            if idx < len(mins_curve):
                aligned_minutes[p['name']] = mins_curve[idx]
            else:
                aligned_minutes[p['name']] = 0.0
    else:
        raise ValueError("Must provide either 'target_minutes' dictionary or 'rotation_size' integer.")

    # Auto-normalize if requested or check sum
    tot_m = sum(aligned_minutes.values())
    if auto_normalize_240 and tot_m > 0 and abs(tot_m - 240.0) > 0.1:
        scale = 240.0 / tot_m
        aligned_minutes = {k: round(v * scale, 1) for k, v in aligned_minutes.items()}
        # fix rounding diff on top player
        diff = 240.0 - sum(aligned_minutes.values())
        top_name = max(aligned_minutes, key=aligned_minutes.get)
        aligned_minutes[top_name] = round(aligned_minutes[top_name] + diff, 1)
        tot_m = 240.0

    # Invert to Intangibles
    solved_roster, final_m = invert_team_intangibles(roster_records, aligned_minutes)
    
    return {
        'team_id': tid,
        'abbreviation': abbr,
        'team_name': f"{city} {name}",
        'total_minutes': final_m,
        'conservation_passed': abs(final_m - 240.0) < 0.2,
        'players': solved_roster
    }

# ---------------------------------------------------------------------------
# 5. CLI Presentation & Interactive Handlers
# ---------------------------------------------------------------------------
def print_results_table(result: dict):
    print("\n" + "=" * 105)
    print(f" NBA 2K22 INTANGIBLES & ROTATION CALCULATOR: {result['team_name']} ({result['abbreviation']})")
    status = "VALID (240.0m)" if result['conservation_passed'] else f"WARNING: {result['total_minutes']:.1f}m != 240.0m"
    print(f" Total Playing Time: {result['total_minutes']:.1f} min | Time Conservation Status: {status}")
    print("=" * 105)
    print(f"{'Rk':<3} | {'Player Name':<20} | {'Pos':<4} | {'Target M':<8} | {'Attr Sum':<8} | {'Base OVR':<8} | {'Old Inta':<8} | {'NEW INTA':<8} | {'Delta':<7} | {'Eff OVR'}")
    print("-" * 105)
    for p in result['players']:
        print(f"{p['rank']:<3d} | {p['name']:<20} | {p['position']:<4} | {p['target_minutes']:<8.1f} | {p['total_attr_sum']:<8.1f} | {p['base_ovr']:<8.1f} | {p['current_intangibles']:<8d} | {p['recommended_intangibles']:<8d} | {p['intangibles_delta']:<+7d} | {p['realized_eff_ovr']:<7.1f}")
    print("=" * 105 + "\n")

def parse_minutes_arg(arg_str: str) -> Dict[str, float]:
    """Parses 'Luka:34, Brunson:30, Bullock:26' or 'LeBron=34, AD=33'."""
    m_dict = {}
    tokens = re.split(r'[,;\n]+', arg_str)
    for tok in tokens:
        if not tok.strip():
            continue
        parts = re.split(r'[:=]+', tok.strip())
        if len(parts) == 2:
            pname, m_val = parts[0].strip(), parts[1].strip()
            try:
                m_dict[pname] = float(m_val)
            except ValueError:
                pass
    return m_dict

def main():
    parser = argparse.ArgumentParser(description="NBA 2K22 Automated Team-Relative Intangibles & Rotation Inversion Calculator")
    parser.add_argument('--team', type=str, help="Team abbreviation (e.g. LAL, DAL, GSW), city, or name")
    parser.add_argument('--minutes', type=str, help="Comma-separated string of player:minutes (e.g. 'LeBron:34,AD:33,Westbrook:28')")
    parser.add_argument('--minutes-file', type=str, help="Path to JSON or text file containing player minutes mapping")
    parser.add_argument('--rotation-size', type=int, choices=[8, 9, 10, 11, 12], help="Number of rotation players to auto-balance minutes for")
    parser.add_argument('--auto-normalize', action='store_true', default=True, help="Automatically scale input minutes to strictly equal 240.0 minutes")
    parser.add_argument('--db-path', type=str, default=DEFAULT_DB_PATH, help="Path to league_state.sqlite")
    parser.add_argument('--export-json', type=str, help="Path to export the calculated intangibles result as JSON")
    parser.add_argument('--interactive', action='store_true', help="Run in interactive prompt mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        print("\n=== NBA 2K22 Intangibles Rotation Calculator (Interactive Mode) ===")
        team_q = input("Enter Team (Abbr/City/Name, e.g. LAL, Warriors, Dallas): ").strip()
        rot_str = input("Enter rotation size (e.g. 10) or press Enter to input custom minutes: ").strip()
        
        target_mins = None
        rot_size = None
        if rot_str.isdigit():
            rot_size = int(rot_str)
        else:
            print("Enter player minutes (e.g. 'PlayerName: 32.0', empty line to finish):")
            target_mins = {}
            while True:
                line = input("> ").strip()
                if not line:
                    break
                sub = parse_minutes_arg(line)
                target_mins.update(sub)
                
        res = calculate_team_intangibles(team_q, target_minutes=target_mins, rotation_size=rot_size, db_path=args.db_path, auto_normalize_240=True)
        print_results_table(res)
        return

    if not args.team:
        parser.print_help()
        print("\nError: Please provide --team (e.g. --team DAL) or use --interactive.", file=sys.stderr)
        sys.exit(1)
        
    target_mins = None
    if args.minutes:
        target_mins = parse_minutes_arg(args.minutes)
    elif args.minutes_file:
        if not os.path.exists(args.minutes_file):
            print(f"Error: minutes file not found: {args.minutes_file}", file=sys.stderr)
            sys.exit(1)
        with open(args.minutes_file, 'r', encoding='utf-8') as f:
            if args.minutes_file.endswith('.json'):
                target_mins = json.load(f)
            else:
                target_mins = parse_minutes_arg(f.read())
                
    try:
        res = calculate_team_intangibles(
            team_query=args.team,
            target_minutes=target_mins,
            rotation_size=args.rotation_size if not target_mins else None,
            db_path=args.db_path,
            auto_normalize_240=args.auto_normalize
        )
        print_results_table(res)
        
        if args.export_json:
            with open(args.export_json, 'w', encoding='utf-8') as f:
                json.dump(res, f, indent=2, ensure_ascii=False)
            print(f"Successfully exported result to: {args.export_json}")
            
    except Exception as e:
        print(f"\n[Execution Error]: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
