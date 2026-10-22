from .calculations import distribution, result
from .coverage import player_value
from .models import module_result


def metrics(data, team):
    roster = team["roster"]
    return {"positions": distribution([player_value(data, p, "position") for p in roster], "position"),
            "contract_terms": distribution([player_value(data, p, "contract_years_left") for p in roster], "contract_years"),
            "roster_count": result(len(roster)) if roster else result(reason="ROSTER_COVERAGE_UNKNOWN")}


def analyze(data, team):
    values = metrics(data, team)
    missing = [name for name, value in values.items() if value["availability"] == "UNKNOWN"]
    missing += ["完整能力/角色/上场时间/伤病/年龄，不能仅凭位置人数认定实力缺口"]
    return module_result("roster", values, ["位置和合同分布可描述阵容结构，不默认填入 OVR、年龄或潜力。"],
                         missing, ["由 GM 结合实测角色与比赛证据区分轮换缺口、冗余和保留资产。"])


def analyze_development(data, team):
    observed = [{"player_name": player["player_name"],
                 "ratings": {key: player_value(data, player, key) for key in
                             ("three_point_rating", "pass_accuracy_rating", "speed_rating", "perimeter_defense_rating")}}
                for player in team["roster"]]
    return module_result("development", {"observed_partial_ratings": observed or None},
        ["只能分析培养环境；游戏自然成长，不生成能力、潜力、徽章或倾向改值。"],
        ["年龄、完整属性、训练负荷、教练归属和连续成长观测"],
        ["GM 可讨论出场角色及培养环境，MC 成长故事继续停用。"])
