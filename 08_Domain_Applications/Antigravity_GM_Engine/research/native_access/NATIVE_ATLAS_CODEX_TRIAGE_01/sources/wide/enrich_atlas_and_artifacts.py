#!/usr/bin/env python3
"""
Generates the comprehensive research deliverables for NBA2K22-NATIVE-ATLAS-R00-WIDE-01:
- Enriched native_object_atlas_75.json
- native_ingredient_matrix.json (Player, GM, Coach ingredient coverage across 6 tiers)
- priority_research_queue.json (Ranked exploration queue)
- codex_breakthrough_packets.json (Targeted engineering problem packets)
"""

import json
from pathlib import Path
from datetime import datetime, timezone

TARGET_DIR = Path(__file__).resolve().parent
ATLAS_PATH = TARGET_DIR / "native_object_atlas_75.json"

SLOT_METADATA = {
    0: {"domains": ["SYSTEM", "LEAGUE"], "relation": "Root header defining global season year and roster engine state.", "open_q": "Decipher bitfields in 56-byte header."},
    1: {"domains": ["PLAYER"], "relation": "Primary Player entity pool; PlayerID index anchors stats, contracts, and rotations.", "open_q": "Isolate exact GetPlayerByIndex RVA in .text."},
    2: {"domains": ["PLAYER"], "relation": "1-to-1 or filtered sub-data for active roster players (160 bytes).", "open_q": "Determine which 270 players receive this sub-record."},
    3: {"domains": ["PLAYER"], "relation": "Special attributes or all-time legendary player modifiers (10 records).", "open_q": "Map 10 records to specific game legends or celebrity players."},
    4: {"domains": ["PLAYER", "DRAFT"], "relation": "Draft prospects pool sharing 1264-byte PLAYER struct with Slot 1.", "open_q": "Confirm whether field layout is identical to Slot 1 byte-for-byte."},
    5: {"domains": ["LEAGUE", "GM"], "relation": "Global CBA and league operational rules (8008 bytes).", "open_q": "Locate salary cap ceiling, luxury tax thresholds, and trade rules inside 8KB block."},
    6: {"domains": ["GM", "TEAM"], "relation": "Secondary team configuration, market size, and fan interest (4860 bytes).", "open_q": "Map team market categories and fan loyalty multipliers."},
    7: {"domains": ["SYSTEM"], "relation": "Reserved empty slot (count=0, pData=NULL).", "open_q": "None; verify remains inactive across saves."},
    8: {"domains": ["GM", "TEAM"], "relation": "Primary Team entity pool (219 teams, 4696 bytes); anchors team_id.", "open_q": "Decode team colors, arena references, and historical franchise lineage."},
    9: {"domains": ["TEAM", "GM"], "relation": "Team arena, court floor, and jersey uniform catalog (60 bytes).", "open_q": "Correlate with 4-byte gap preceding Slot 10."},
    10: {"domains": ["LEAGUE"], "relation": "League historical championship and records index 1 (32 bytes).", "open_q": "Distinguish from Slot 44 and map year ranges."},
    11: {"domains": ["LEAGUE"], "relation": "League historical awards index 2 (32 bytes).", "open_q": "Identify MVP, DPOY, Finals MVP historical entries."},
    12: {"domains": ["LEAGUE"], "relation": "League retired jerseys and hall-of-fame index 3 (32 bytes).", "open_q": "Map retired jersey numbers to teams."},
    13: {"domains": ["LEAGUE"], "relation": "League record book index 4 (32 bytes).", "open_q": "Map single-game and career record categories."},
    14: {"domains": ["SYSTEM"], "relation": "Reserved empty slot (Slot 14-17 group).", "open_q": "None."},
    15: {"domains": ["SYSTEM"], "relation": "Reserved empty slot (Slot 14-17 group).", "open_q": "None."},
    16: {"domains": ["SYSTEM"], "relation": "Reserved empty slot (Slot 14-17 group).", "open_q": "None."},
    17: {"domains": ["SYSTEM"], "relation": "Reserved empty slot (Slot 14-17 group).", "open_q": "None."},
    18: {"domains": ["COACH"], "relation": "Coaching tactics, philosophy, offensive/defensive tempo, and playstyle (32 bytes).", "open_q": "Decode pace, ball movement, defense aggression integers."},
    19: {"domains": ["COACH", "GM"], "relation": "Staff members pool (head coach, assistants, scouts, trainers - 352 bytes).", "open_q": "Map badges, teaching ratings, and contract salary."},
    20: {"domains": ["LEAGUE"], "relation": "Schedule metadata header (current day index, total games).", "open_q": "Map current season calendar day."},
    21: {"domains": ["LEAGUE", "GM"], "relation": "Calendar events, trade deadline, draft day, all-star schedule (12 bytes).", "open_q": "Decode date offsets and event enum codes."},
    22: {"domains": ["COACH", "PLAYER"], "relation": "Team rotation timeline and minutes distribution grid (360 bytes).", "open_q": "Decode 48-minute substitution matrix per position."},
    23: {"domains": ["SYSTEM"], "relation": "Statistics header metadata (4 bytes).", "open_q": "Decode tracking flags for statistical accumulation."},
    24: {"domains": ["PLAYER"], "relation": "Player regular season cumulative traditional and shooting statistics (48 bytes).", "open_q": "Completed R00-01 verification; map remaining secondary metrics."},
    25: {"domains": ["SYSTEM"], "relation": "Playoff stats split header (2 bytes).", "open_q": "Decode playoff qualifier count."},
    26: {"domains": ["PLAYER"], "relation": "Player playoff cumulative statistics (114 bytes).", "open_q": "Compare schema layout with regular season Slot 24."},
    27: {"domains": ["SYSTEM"], "relation": "Team stats split header (2 bytes).", "open_q": "None."},
    28: {"domains": ["GM", "TEAM"], "relation": "Team regular season cumulative traditional statistics (62 bytes).", "open_q": "Decode pace, points per game, offensive/defensive rating."},
    29: {"domains": ["SYSTEM"], "relation": "Team split header metadata (2 bytes).", "open_q": "None."},
    30: {"domains": ["GM", "TEAM"], "relation": "Team playoff cumulative statistics (114 bytes).", "open_q": "Decode playoff series win-loss metrics."},
    31: {"domains": ["PLAYER"], "relation": "Player career-high single game statistics (48 bytes).", "open_q": "Identify game date and opponent cross-reference."},
    32: {"domains": ["PLAYER"], "relation": "Player advanced and tracking metrics (hustle, speed, touches - 48 bytes).", "open_q": "Align with NBA.com tracking statistics definitions."},
    33: {"domains": ["PLAYER"], "relation": "Player All-Star game cumulative statistics (48 bytes).", "open_q": "Map All-Star appearance years."},
    34: {"domains": ["PLAYER"], "relation": "Player NBA Finals cumulative statistics (48 bytes).", "open_q": "Map Finals series appearances."},
    35: {"domains": ["GM"], "relation": "Team financial ledger, total payroll, luxury tax bill, cash balance (4020 bytes).", "open_q": "High-value Codex target: decode multi-year financial projection block."},
    36: {"domains": ["GM", "PLAYER"], "relation": "Mid-season player contract extension proposals and negotiation states (336 bytes).", "open_q": "Decode negotiation sentiment, player demand, and deadline."},
    37: {"domains": ["PLAYER"], "relation": "Player last 5 games rolling statistical window (48 bytes).", "open_q": "Confirm rolling window calculation mechanism."},
    38: {"domains": ["LEAGUE", "GM"], "relation": "Standings tiebreak rules and conference seedings (120 bytes).", "open_q": "Decode division winner and head-to-head tiebreaker order."},
    39: {"domains": ["PLAYER", "LEAGUE"], "relation": "Player year-by-year historical career logs (69,040 records, 52 bytes).", "open_q": "High-value Codex target: decode indexing from PlayerID and season year."},
    40: {"domains": ["GM", "DRAFT"], "relation": "Draft metadata header (4 bytes).", "open_q": "Identify current draft round and lottery state."},
    41: {"domains": ["GM", "DRAFT"], "relation": "Draft combine scouting measurements and athletic drill scores (152 bytes).", "open_q": "Decode wingspan, standing reach, vertical leap, lane agility."},
    42: {"domains": ["GM", "DRAFT"], "relation": "Future draft pick assets, protections, swap rights (32 bytes).", "open_q": "High-value Codex target: decode pick protections (top-3, top-10) and originating team."},
    43: {"domains": ["GM", "DRAFT"], "relation": "Draft order pick ownership pointers (8 bytes).", "open_q": "Connect picks to draft board slots."},
    44: {"domains": ["GM"], "relation": "Team trade restrictions or head-to-head matchup matrix (24 bytes).", "open_q": "Resolve historical conflict: schedule vs matchup matrix vs trade restrictions."},
    45: {"domains": ["SYSTEM"], "relation": "Unassigned or empty descriptor slot.", "open_q": "Verify slot presence."},
    46: {"domains": ["GM", "PLAYER"], "relation": "Free agent interest index and destination preference matrix (216 bytes).", "open_q": "Decode city preference, title contender preference, market size weights."},
    47: {"domains": ["GM"], "relation": "Team GM and Owner relationship, trust, goals, budget constraints (16 bytes).", "open_q": "Decode owner patience, spending tolerance, and expectations."},
    48: {"domains": ["SYSTEM"], "relation": "Reserved empty slot.", "open_q": "None."},
    49: {"domains": ["SYSTEM"], "relation": "Reserved empty slot.", "open_q": "None."},
    50: {"domains": ["COACH"], "relation": "Team offensive playbook catalog and set play assignments (280 bytes).", "open_q": "High-value Coach target: decode 32 set plays per team playbook."},
    51: {"domains": ["SYSTEM"], "relation": "Unassigned descriptor slot.", "open_q": "Verify slot presence."},
    52: {"domains": ["COACH"], "relation": "Tactical play diagram waypoints and execution routes (128 bytes).", "open_q": "Decode court coordinates and pass timing tags."},
    53: {"domains": ["SYSTEM"], "relation": "Unassigned descriptor slot.", "open_q": "Verify slot presence."},
    54: {"domains": ["PLAYER"], "relation": "Player detailed gameplay tendency and action weights (64 bytes).", "open_q": "Correlate 64 bytes with 99 gameplay tendency sliders."},
    55: {"domains": ["GM"], "relation": "Arena operations, maintenance, security expenditure (1960 bytes).", "open_q": "Decode facility upgrade tiers."},
    56: {"domains": ["SYSTEM"], "relation": "Unassigned descriptor slot.", "open_q": "Verify slot presence."},
    57: {"domains": ["GM"], "relation": "Ticket pricing table, attendance demand, pricing tiers (32 bytes).", "open_q": "Decode upper bowl, lower bowl, luxury box pricing."},
    58: {"domains": ["SYSTEM"], "relation": "Unassigned descriptor slot.", "open_q": "Verify slot presence."},
    59: {"domains": ["GM"], "relation": "Luxury tax bracket configuration and repeater penalties (212 bytes).", "open_q": "Decode CBA tax brackets and penalty rates."},
    60: {"domains": ["SYSTEM"], "relation": "Unassigned descriptor slot.", "open_q": "Verify slot presence."},
    61: {"domains": ["GM", "PLAYER"], "relation": "Waived player salary and stretch provision dead money ledger (136 bytes).", "open_q": "Disassembly confirmed RVA 0xF3C790; decode multi-year stretch allocation."},
    62: {"domains": ["SYSTEM"], "relation": "Unassigned descriptor slot.", "open_q": "Verify slot presence."},
    63: {"domains": ["GM", "PLAYER"], "relation": "Contract option clauses (player option, team option, non-guaranteed bonuses - 120 bytes).", "open_q": "Decode option decision dates and incentive clauses."},
    64: {"domains": ["SYSTEM"], "relation": "Unassigned descriptor slot.", "open_q": "Verify slot presence."},
    65: {"domains": ["COACH", "LEAGUE"], "relation": "All-Defensive and All-NBA team voting results (8 bytes).", "open_q": "Decode award vote points."},
    66: {"domains": ["GM"], "relation": "Team salary cap exceptions (MLE, BAE, Hard Cap Apron state - 112 bytes).", "open_q": "Decode MLE remaining amount and apron hard-cap trigger."},
    67: {"domains": ["GM"], "relation": "Traded Player Exceptions (TPE) balances and expiration dates (116 bytes).", "open_q": "Decode TPE amount, originating player, and expiry timestamp."},
    68: {"domains": ["PLAYER", "COACH"], "relation": "Global team chemistry and player morale matrix (16,132 bytes).", "open_q": "Decode player-to-player and player-to-coach satisfaction weights."},
    69: {"domains": ["PLAYER"], "relation": "Global player injury system state and body part trauma (41,704 bytes).", "open_q": "Decode injury duration, body part enum, severity level."},
    70: {"domains": ["SYSTEM"], "relation": "Unassigned descriptor slot.", "open_q": "Verify slot presence."},
    71: {"domains": ["GM", "COACH"], "relation": "Staff budget allocation across coaching, medical, and scouting (112 bytes).", "open_q": "Decode departmental budget allocations."},
    72: {"domains": ["SYSTEM"], "relation": "Unassigned descriptor slot.", "open_q": "Verify slot presence."},
    73: {"domains": ["SYSTEM"], "relation": "Reserved empty slot.", "open_q": "None."},
    74: {"domains": ["SYSTEM"], "relation": "Global engine feature flags and unlockable bitmasks (8,136 records, 2 bytes).", "open_q": "Decode active feature bitmasks."}
}

def enrich():
    with open(ATLAS_PATH, "r", encoding="utf-8") as f:
        atlas = json.load(f)

    for slot in atlas["slots"]:
        idx = slot["slot_index"]
        meta = SLOT_METADATA.get(idx, {"domains": ["UNKNOWN"], "relation": "Unknown relation", "open_q": "Uninvestigated slot"})
        slot["role_domains"] = meta["domains"]
        slot["temporal_or_identity_relation"] = meta["relation"]
        slot["open_reverse_engineering_questions"] = meta["open_q"]
        
        # Maturity classification
        if idx in (1, 24):
            slot["confidence_maturity"] = "VERIFIED_ACTIVE"
        elif slot["status"] == "EMPTY_RESERVED":
            slot["confidence_maturity"] = "EMPTY_RESERVED"
        elif slot["status"] == "CONFIRMED_ACTIVE_READABLE":
            slot["confidence_maturity"] = "ACTIVE_READABLE_EMPIRICAL"
        else:
            slot["confidence_maturity"] = "UNVERIFIED"

    with open(ATLAS_PATH, "w", encoding="utf-8") as f:
        json.dump(atlas, f, indent=2, ensure_ascii=False)
    print("Enriched native_object_atlas_75.json")

    # Generate native_ingredient_matrix.json
    matrix = {
        "schema_version": "nba2k22.native_ingredient_matrix.v1",
        "task_id": "NBA2K22-NATIVE-ATLAS-R00-WIDE-01",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "domains": {
            "PLAYER": {
                "description": "Player core vitals, ratings, tendencies, contracts, health, performance stats, and career history.",
                "tier_1_discovered_and_certified": [
                    {"ingredient": "PLAYER_CORE_ATTRIBUTES", "primary_slot": 1, "offset_range": "0..1263", "evidence": "Slot 1 verified on PID 1828 (3390 records, Ben Simmons/Seth Curry DOB & max extension contract verified)."},
                    {"ingredient": "PLAYER_REGULAR_SEASON_STATS", "primary_slot": 24, "offset_range": "0..47", "evidence": "Slot 24 verified on PID 1828 (9773 records, Curry 16-game BoxScore cumulative stats parity)."}
                ],
                "tier_2_discovered_uncertified_decoding": [
                    {"ingredient": "PLAYER_PLAYOFF_STATS", "primary_slot": 26, "stride": 114, "records": 1023, "getter_rva": "0xF3F6F0", "notes": "Active in memory, requires schema alignment against Slot 24."},
                    {"ingredient": "PLAYER_ADVANCED_METRICS", "primary_slot": 32, "stride": 48, "records": 4119, "getter_rva": "0xF3D9C0", "notes": "Hustle, touches, speed; fields require individual verification."},
                    {"ingredient": "PLAYER_CAREER_HIGH_STATS", "primary_slot": 31, "stride": 48, "records": 2744, "getter_rva": "0xF3CDB0", "notes": "Single-game highs; requires mapping opponent and game context."},
                    {"ingredient": "PLAYER_TENDENCY_WEIGHTS", "primary_slot": 54, "stride": 64, "records": 5227, "getter_rva": None, "notes": "64 bytes active in memory; needs alignment with 99 UI tendency sliders."}
                ],
                "tier_3_historical_research_clue_only": [
                    {"ingredient": "PLAYER_CAREER_LOGS_HISTORICAL", "primary_slot": 39, "stride": 52, "records": 69040, "getter_rva": "0xF400A0", "notes": "Massive 69K records; requires decoding PlayerID + season year composite key."},
                    {"ingredient": "PLAYER_SPECIAL_SUBDATA", "primary_slot": 2, "stride": 160, "records": 270, "getter_rva": "0xF3FC10", "notes": "270 records active; semantics unverified."}
                ],
                "tier_4_native_source_unknown": [
                    {"ingredient": "PLAYER_REAL_TIME_ENERGY_FATIGUE", "status": "UNKNOWN_FAIL_CLOSED", "notes": "In-game real-time stamina/fatigue is in match engine memory, not ROSTERDATA."},
                    {"ingredient": "PLAYER_FACE_3D_MESH_POINTER", "status": "UNKNOWN_FAIL_CLOSED", "notes": "Visual render mesh handles reside in graphics subsystem."}
                ],
                "tier_5_requires_cross_object_join": [
                    {"ingredient": "PLAYER_ROTATION_ASSIGNMENT", "join_formula": "Slot 1 (PlayerID) <-> Slot 22 (TeamRotationTimeline)", "notes": "Player minutes are determined by Coach rotation timeline (Slot 22)."},
                    {"ingredient": "PLAYER_MORALE_AND_CHEMISTRY", "join_formula": "Slot 1 (PlayerID) <-> Slot 68 (GlobalMoraleMatrix)", "notes": "Player happiness requires mapping team morale block."}
                ],
                "tier_6_non_existent_or_unproven_in_game": [
                    {"ingredient": "INDEPENDENT_STANDALONE_AGE_INT", "verdict": "NON_EXISTENT", "notes": "Age is dynamically computed from birth_date (0x6E..0x70) and game_date formula, no separate integer."}
                ]
            },
            "GM": {
                "description": "Franchise finances, payroll, luxury tax, cap exceptions, dead money, trade assets, draft picks, and operations.",
                "tier_1_discovered_and_certified": [
                    {"ingredient": "TEAM_CORE_ENTITY", "primary_slot": 8, "records": 219, "stride": 4696, "evidence": "Team identity anchors verified across historical and live memory."}
                ],
                "tier_2_discovered_uncertified_decoding": [
                    {"ingredient": "WAIVED_DEAD_SALARY_CAP_HIT", "primary_slot": 61, "stride": 136, "records": 222, "getter_rva": "0xF3C790", "notes": "Getter disassembly confirmed RVA 0xF3C790; multi-year stretch breakdown pending."},
                    {"ingredient": "TEAM_HARD_CAP_EXCEPTIONS", "primary_slot": 66, "stride": 112, "records": 120, "getter_rva": "0xF3BE10", "notes": "MLE, BAE, Apron hard-cap state; active in memory."},
                    {"ingredient": "TRADE_EXCEPTION_TPE_RECORDS", "primary_slot": 67, "stride": 116, "records": 443, "getter_rva": "0xF40730", "notes": "TPE amount, player anchor, expiration date."},
                    {"ingredient": "DRAFT_PICK_ASSETS", "primary_slot": 42, "stride": 32, "records": 504, "getter_rva": "0xF3C940", "notes": "Traded picks, swap rights, protection tiers."}
                ],
                "tier_3_historical_research_clue_only": [
                    {"ingredient": "TEAM_FINANCIAL_LEDGER_BLOCK", "primary_slot": 35, "stride": 4020, "records": 112, "getter_rva": "0xF3C6B0", "notes": "4KB financial ledger per franchise; Codex packet prepared."},
                    {"ingredient": "FREE_AGENT_MARKET_DEMAND", "primary_slot": 46, "stride": 216, "records": 543, "getter_rva": "0xF3D0D0", "notes": "Free agency destination priority weights."}
                ],
                "tier_4_native_source_unknown": [
                    {"ingredient": "OWNER_NET_WORTH_REALTIME", "status": "UNKNOWN_FAIL_CLOSED", "notes": "Owner dynamic financial injections not located in ROSTERDATA."}
                ],
                "tier_5_requires_cross_object_join": [
                    {"ingredient": "TOTAL_TEAM_PAYROLL_AND_TAX", "join_formula": "Slot 1 (ContractYear) + Slot 61 (WaivedSalary) + Slot 67 (TPE) <-> Slot 35 (Ledger) <-> Slot 59 (TaxBrackets)", "notes": "Total cap hit is a multi-object composite."},
                    {"ingredient": "DRAFT_BOARD_PICK_OWNERSHIP", "join_formula": "Slot 42 (DraftAssets) <-> Slot 43 (PickPointers) <-> Slot 40 (DraftMeta)", "notes": "Pick trade history requires asset-to-pointer join."}
                ],
                "tier_6_non_existent_or_unproven_in_game": [
                    {"ingredient": "OFF_THE_BOOKS_ILLEGAL_PAYMENTS", "verdict": "NON_EXISTENT", "notes": "Game engine does not model CBA violations outside standard rules."}
                ]
            },
            "COACH": {
                "description": "Tactical schemes, offensive playbooks, set play execution, substitution timelines, and staff abilities.",
                "tier_1_discovered_and_certified": [
                    {"ingredient": "STAFF_PERSONNEL_POOL", "primary_slot": 19, "records": 1470, "stride": 352, "evidence": "Verified across historical and live memory (GetStaffDataByIndex RVA 0xF3C120)."}
                ],
                "tier_2_discovered_uncertified_decoding": [
                    {"ingredient": "TEAM_ROTATION_TIMELINE", "primary_slot": 22, "stride": 360, "records": 84, "getter_rva": "0xF3ED70", "notes": "Minutes distribution and 48-min rotation timeline."},
                    {"ingredient": "COACH_TACTICS_INDEX", "primary_slot": 18, "stride": 32, "records": 203, "getter_rva": "0xF3FEF0", "notes": "Pace, offensive focus, defensive pressure, transition style."},
                    {"ingredient": "PLAYBOOK_SET_PLAY_CATALOG", "primary_slot": 50, "stride": 280, "records": 32, "getter_rva": "0xF3EE50", "notes": "32 playbooks; assigns set plays per team."}
                ],
                "tier_3_historical_research_clue_only": [
                    {"ingredient": "TACTICAL_DIAGRAM_ROUTES", "primary_slot": 52, "stride": 128, "records": 1601, "getter_rva": "0xF3F000", "notes": "Detailed court diagram waypoints and play design coordinates."}
                ],
                "tier_4_native_source_unknown": [
                    {"ingredient": "MID_GAME_HALF_TIME_SPEECH_EFFECT", "status": "UNKNOWN_FAIL_CLOSED", "notes": "Transient audio/cutscene morale adjustments not in static roster."}
                ],
                "tier_5_requires_cross_object_join": [
                    {"ingredient": "COACH_SYSTEM_FIT_RATING", "join_formula": "Slot 19 (Coach Schemes) <-> Slot 1 (Player Vitals & Attributes)", "notes": "System proficiency is computed by crossing coach preference with player ratings."},
                    {"ingredient": "SET_PLAY_TO_TACTICAL_ROUTE", "join_formula": "Slot 50 (PlaybookCatalog) <-> Slot 52 (TacticalDiagramItems)", "notes": "Set plays reference route items in Slot 52."}
                ],
                "tier_6_non_existent_or_unproven_in_game": [
                    {"ingredient": "COACH_LIFELONG_HISTORICAL_WIN_LOSS_LOGS", "verdict": "NON_EXISTENT_OR_UNPROVEN", "notes": "Head coach career logs appear condensed into single summary attributes."}
                ]
            }
        }
    }

    matrix_path = TARGET_DIR / "native_ingredient_matrix.json"
    with open(matrix_path, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2, ensure_ascii=False)
    print("Generated native_ingredient_matrix.json")

    # Generate priority_research_queue.json
    queue = {
        "schema_version": "nba2k22.priority_research_queue.v1",
        "task_id": "NBA2K22-NATIVE-ATLAS-R00-WIDE-01",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "queue_items": [
            {
                "priority_rank": 1,
                "target_slot": 39,
                "target_name": "PLAYER_CAREER_LOGS",
                "stride_bytes": 52,
                "count": 69040,
                "getter_rva": "0xF400A0",
                "consumer_role": "PLAYER",
                "impact": "Unlocks historical year-by-year player boxscore performance and career milestones.",
                "research_objective": "Determine composite key (PlayerID + SeasonYear) and unpack 52-byte record schema."
            },
            {
                "priority_rank": 2,
                "target_slot": 35,
                "target_name": "TEAM_FINANCIAL_LEDGER_BLOCK",
                "stride_bytes": 4020,
                "count": 112,
                "getter_rva": "0xF3C6B0",
                "consumer_role": "GM",
                "impact": "Unlocks multi-year team payroll, cash reserves, revenue, and luxury tax bills.",
                "research_objective": "Map 4KB structure into sub-blocks (payroll, tax, exceptions, revenue streams)."
            },
            {
                "priority_rank": 3,
                "target_slot": 42,
                "target_name": "DRAFT_ASSETS",
                "stride_bytes": 32,
                "count": 504,
                "getter_rva": "0xF3C940",
                "consumer_role": "GM",
                "impact": "Unlocks all traded draft picks, pick swaps, and conditional protections.",
                "research_objective": "Unpack 32-byte struct: draft year, round, original team, owning team, protection bitmask."
            },
            {
                "priority_rank": 4,
                "target_slot": 22,
                "target_name": "TEAM_ROTATION_TIMELINE",
                "stride_bytes": 360,
                "count": 84,
                "getter_rva": "0xF3ED70",
                "consumer_role": "COACH",
                "impact": "Unlocks coach substitution timeline, minutes per game targets, and depth chart hierarchy.",
                "research_objective": "Map 360 bytes to 15 player roster slots across 48 minutes."
            },
            {
                "priority_rank": 5,
                "target_slot": 61,
                "target_name": "WAIVED_SALARY",
                "stride_bytes": 136,
                "count": 222,
                "getter_rva": "0xF3C790",
                "consumer_role": "GM",
                "impact": "Unlocks dead salary cap hits and multi-season stretch provision accounting.",
                "research_objective": "Unpack 136-byte dead money schedule and player reference index."
            },
            {
                "priority_rank": 6,
                "target_slot": 50,
                "target_name": "PLAYBOOK_SET_PLAY_CATALOG",
                "stride_bytes": 280,
                "count": 32,
                "getter_rva": "0xF3EE50",
                "consumer_role": "COACH",
                "impact": "Unlocks playbooks for all 30 teams and set play selections.",
                "research_objective": "Unpack 280-byte playbook table and cross-reference with Slot 52 diagram waypoints."
            }
        ]
    }

    queue_path = TARGET_DIR / "priority_research_queue.json"
    with open(queue_path, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)
    print("Generated priority_research_queue.json")

    # Generate codex_breakthrough_packets.json
    codex_packets = {
        "schema_version": "nba2k22.codex_breakthrough_packets.v1",
        "task_id": "NBA2K22-NATIVE-ATLAS-R00-WIDE-01",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "packets": [
            {
                "packet_id": "CODEX-PKT-01-CAREER-LOG-INDEXING",
                "title": "Slot 39 PLAYER_CAREER_LOGS (69K Records) Composite Indexing & Schema",
                "target_slot": 39,
                "getter_rva": "0xF400A0",
                "record_stride_bytes": 52,
                "live_count": 69040,
                "consumer_domain": "PLAYER",
                "core_problem": "Slot 39 contains 69,040 52-byte records, representing year-by-year career historical stats. How does the game index into this massive pool from Slot 1 (PLAYER)? Is there a start_log_index and log_count in Slot 1, or is Slot 39 sorted by PlayerID and SeasonYear?",
                "disassembly_anchor": "Getter RVA 0xF400A0 accesses [rax + 0x270] (count) and [rax + 0x278] (pData); stride imul is 52 (0x34).",
                "reproducible_conditions": "Game process running (PID 1828); pData is live at 0x7FF4E76C5CE0.",
                "expected_decoded_shape": "{ player_id: uint16, season_year: uint16, team_id: uint8, games_played: uint8, games_started: uint8, minutes: uint16, pts: uint16, reb: uint16, ast: uint16, stl: uint16, blk: uint16, fgm: uint16, fga: uint16, ftm: uint16, fta: uint16, tpm: uint16, tpa: uint16 }",
                "verification_method": "Verify whether decoding matches known historical records for Michael Jordan, LeBron James, Stephen Curry with 100% statistical fidelity."
            },
            {
                "packet_id": "CODEX-PKT-02-FINANCIAL-LEDGER-STRUCTURE",
                "title": "Slot 35 TEAM_FINANCIAL_LEDGER_BLOCK (4KB Block) Multi-Year Decomposition",
                "target_slot": 35,
                "getter_rva": "0xF3C6B0",
                "record_stride_bytes": 4020,
                "live_count": 112,
                "consumer_domain": "GM",
                "core_problem": "Slot 35 allocates 4,020 bytes per team (112 records across 30 active + historical franchises). This massive block governs salary payroll, cash flow, revenue, luxury tax, and arena operations. What is the internal sub-struct layout of this 4KB block?",
                "disassembly_anchor": "Getter RVA 0xF3C6B0 accesses [rax + 0x230] (count) and [rax + 0x238] (pData); stride is 4020 (0xFB4).",
                "reproducible_conditions": "pData is live at 0x7FF4E75B69F0.",
                "expected_decoded_shape": "{ team_id: uint8, current_payroll: int64, projected_tax: int64, cash_balance: int64, ticket_revenue_projected: int64, multi_year_commitments: list[int64] }",
                "verification_method": "Cross-reference decoded payroll and luxury tax against in-game GM front-office screen for Golden State Warriors (highest tax bill in 2021-22)."
            },
            {
                "packet_id": "CODEX-PKT-03-DRAFT-ASSET-PROTECTIONS",
                "title": "Slot 42 DRAFT_ASSETS (32 Bytes) Traded Pick Protection Bitmask",
                "target_slot": 42,
                "getter_rva": "0xF3C940",
                "record_stride_bytes": 32,
                "live_count": 504,
                "consumer_domain": "GM",
                "core_problem": "Future draft pick trading in NBA2K22 allows protections (e.g. top-3 protected, lottery protected, pick swaps). How does the 32-byte record encode original owning team, current owning team, draft year, round, and condition/protection logic?",
                "disassembly_anchor": "Getter RVA 0xF3C940 accesses [rax + 0x2A0] (count) and [rax + 0x2A8] (pData); stride is 32 (0x20).",
                "reproducible_conditions": "pData is live at 0x7FF4E7B2D7C0.",
                "expected_decoded_shape": "{ asset_id: uint16, year: uint16, round: uint8, original_team_id: uint8, current_owner_team_id: uint8, is_swap: bool, protection_kind: enum, protection_range: uint8 }",
                "verification_method": "Check traded pick assets against known 2021-22 real-world traded picks (e.g. Lakers 2022 first round pick owned by Pelicans)."
            },
            {
                "packet_id": "CODEX-PKT-04-ROTATION-TIMELINE-GRID",
                "title": "Slot 22 TEAM_ROTATION_TIMELINE (360 Bytes) 48-Minute Substitution Grid",
                "target_slot": 22,
                "getter_rva": "0xF3ED70",
                "record_stride_bytes": 360,
                "live_count": 84,
                "consumer_domain": "COACH",
                "core_problem": "Slot 22 represents coach rotation timelines (360 bytes per team). 360 = 15 players * 24 bytes, or 30 players * 12 bytes, or 48 minutes * 7.5 bytes? How does the timeline represent which 5 players are on the floor for each minute of the game?",
                "disassembly_anchor": "Getter RVA 0xF3ED70 accesses [rax + 0x160] (count) and [rax + 0x168] (pData); stride is 360 (0x168).",
                "reproducible_conditions": "pData is live at 0x7FF4E74A0418.",
                "expected_decoded_shape": "{ team_id: uint8, player_minutes_targets: list[uint8, 15], minute_by_minute_lineup: list[list[uint16, 5], 48] }",
                "verification_method": "Compare decoded minute allocations with in-game Coach Rotation UI timeline."
            }
        ]
    }

    packets_path = TARGET_DIR / "codex_breakthrough_packets.json"
    with open(packets_path, "w", encoding="utf-8") as f:
        json.dump(codex_packets, f, indent=2, ensure_ascii=False)
    print("Generated codex_breakthrough_packets.json")

if __name__ == "__main__":
    enrich()
