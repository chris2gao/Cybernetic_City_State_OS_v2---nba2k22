from .calculations import win_percentage
from .coverage import assess
from .models import module_result
from .personas import reference


def lifecycle(data, team):
    inputs = assess(data, team, "results")
    state = team["state"]
    rate = win_percentage(inputs["values"]["total_wins"], inputs["values"]["total_losses"], state.get("total_games"))
    value = rate["value"]
    thresholds = data.gm_policy["lifecycle_candidate_thresholds"]
    played = (rate["inputs"]["wins"] + rate["inputs"]["losses"]) if value is not None else None
    candidate = "UNDETERMINED"
    if played is not None and played >= thresholds["minimum_games"]:
        if value >= thresholds["contending_win_percentage"]:
            candidate = "CONTENDING"
        elif value >= thresholds["competitive_win_percentage"]:
            candidate = "COMPETITIVE"
        elif value < thresholds["rebuilding_win_percentage"]:
            candidate = "REBUILDING"
        else:
            candidate = "RETOOLING"
    return {"state": candidate, "status": "PROPOSED" if candidate != "UNDETERMINED" else "NOT_EVALUABLE",
            "basis": rate, "thresholds_availability": "CONFIGURED",
            "configuration_status": data.gm_policy["configuration_status"],
            "note": "候选生命周期不是玩家已确认战略；不依据工资或旧历史标签分类。"}


def profile(data, abbreviation, previous=None):
    team = data.teams[abbreviation]
    category = lifecycle(data, team)
    return {"team": team["identity"], "status": "PROPOSED", "lifecycle": category,
            "culture_reference": reference(data, abbreviation),
            "goals": {"short_term": {"status": "PROPOSED", "text": "依据本队可用证据界定优先问题，等待网页 GM 判断。"},
                      "medium_term": {"status": "PROPOSED", "text": "结合本队合同期限与角色需求讨论阵容连续性。"},
                      "long_term": {"status": "PROPOSED", "text": "结合玩家确认的文化和战略建立长期方向，不预定冠军。"}},
            "core_asset_policy": {"status": "PROPOSED", "protected_player_names": data.gm_policy["protected_player_names"],
                                  "other_core_assets": None},
            "roster_construction_issues": [], "last_confirmed_strategy": None,
            "last_confirmed_decision": None,
            "previous_analysis": previous,
            "history_status": "CONFIRMED_STRATEGY_HISTORY_NOT_YET_PROVIDED"}


def analyze(data, team):
    category = lifecycle(data, team)
    return module_result("strategy", {"win_percentage": category["basis"]},
                         [category["note"]], [] if category["state"] != "UNDETERMINED" else ["足够场次的真实战绩"],
                         ["将候选生命周期交网页 GM 结合核心资产和球队文化判断，不自动买卖球员。"])
