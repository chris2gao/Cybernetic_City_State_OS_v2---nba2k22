from datetime import date
from .calculations import draft_year
from .models import module_result

CATEGORIES = ("GAME_REALITY", "HISTORICAL_REFERENCE", "PROPOSED_WORLDLINE")


def reference_context(game_date, policy, completed_drafts=None):
    if game_date is None:
        return {'category': 'HISTORICAL_REFERENCE', 'availability': 'UNKNOWN',
                'reference_mode': None, 'reference_year': None, 'progress_status': 'GAME_DATE_UNCONFIRMED',
                'draft': draft_year(completed_drafts), 'game_results': None,
                'attribute_write_authority': False, 'mc_growth': 'DISABLED_DEFERRED'}
    year = date.fromisoformat(game_date).year
    gravity = policy["historical_gravity"]
    transition = gravity["historical_reference_from_game_year"]
    historical_year = None
    if year == transition:
        historical_year = gravity["historical_anchor_year"] + gravity["elapsed_historical_years_at_transition"]
    elif year > transition and type(completed_drafts) is int and completed_drafts >= 4:
        historical_year = draft_year(completed_drafts)["value"]["next_class_year"]
    return {"category": "HISTORICAL_REFERENCE", "availability": "REFERENCE",
            "reference_mode": "MODERN" if year < transition else "HISTORICAL_ERA",
            "reference_year": year if year < transition else historical_year,
            "progress_status": "KNOWN_REFERENCE_ANCHOR" if year <= transition else
                               ("PLAYER_CONFIRMED_PROGRESS" if historical_year else "PLAYER_PROGRESS_REQUIRED"),
            "draft": draft_year(completed_drafts), "game_results": None,
            "attribute_write_authority": False, "mc_growth": "DISABLED_DEFERRED"}


def analyze(data, team, completed_drafts=None):
    context = reference_context(data.source.game_date, data.policy, completed_drafts)
    return module_result("worldline", {"reference": context},
        ["历史参考不覆盖游戏战绩，不预定交易或冠军；历史重力只能另提具体待批准方案。"],
        ["玩家确认的历史进度和有来源的历史参考事件"] if completed_drafts is None else [],
        ["以本局事实为首要依据，分别记录 GAME_REALITY、HISTORICAL_REFERENCE 和 PROPOSED_WORLDLINE。"])


def draft_candidates(records, active_names):
    selected, seen, conflicts = [], set(), []
    for row in records:
        if row.get("model_category") != "HISTORICAL_ROOKIE":
            continue
        key = (row["full_name"].casefold().strip(), row.get("draft_year"), row.get("draft_round"), row.get("draft_pick"))
        if key[0] in {name.casefold().strip() for name in active_names}:
            conflicts.append({"identity": list(key), "reason": "ACTIVE_NAMESAKE_REQUIRES_REVIEW"})
        elif key not in seen:
            seen.add(key)
            selected.append(row)
    return {"candidates": selected, "conflicts": conflicts, "missing_slots": "KEEP_GAME_GENERATED_ROOKIES",
            "slot_injection": "NOT_IMPLEMENTED_IN_GM_CORE"}
