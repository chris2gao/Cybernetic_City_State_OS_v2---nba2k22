"""Prepare an offline 30-team review packet for the web GM; no trade templates."""
from dataclasses import asdict
from copy import deepcopy
from . import VERSION
from . import calculations, finance, franchise, roster, tactics, trades, worldline
from .coverage import assess
from .history import compare_context
from .models import module_result


def team_modules(data, team, completed_drafts=None):
    owned_staff = None
    if data.staff.get("ownership_verified") is True:
        owned_staff = [row for row in data.staff.get("records", []) if row.get("team_id") == team["identity"]["team_id"]]
    return {
        "strategy": franchise.analyze(data, team),
        "roster": roster.analyze(data, team),
        "staff": module_result("staff", {"team_staff": owned_staff},
            ["员工池原始观测不等于本队已确认教练；不按姓名或槽位猜归属。"],
            [] if owned_staff else ["本队员工身份/岗位/合同/能力及归属"], ["补齐归属后由 GM 独立评估留任或换帅。"]),
        "offense": tactics.analyze(data, team, "offense"),
        "defense": tactics.analyze(data, team, "defense"),
        "trades": trades.analyze(data, team),
        "contracts": finance.analyze_contracts(data, team),
        "draft_free_agency": module_result("draft_free_agency", {"draft_progress": calculations.draft_year(completed_drafts)},
            ["从历史新秀索引查询已验证模型；未观测选秀权和自由球员权利不作为拥有资产。"],
            ["选秀权归属及未来三年窗口/自由球员签约权"] + ([] if completed_drafts is not None else ["已完成选秀次数"]),
            ["已确认进度后再查对应新秀模型，缺额保留游戏生成球员。"]),
        "development": roster.analyze_development(data, team),
        "business": finance.analyze_business(data, team),
        "culture": module_result("culture", {"adopted_owner_style": None},
            ["球队档案仅作 REFERENCE，未批准的文化与长期方向为 PROPOSED。"],
            ["玩家确认的球队文化/老板偏好和长期经营史"], ["网页 GM 阅读本队参考后提出独立经营方向。"]),
        "worldline": worldline.analyze(data, team, completed_drafts),
    }


def prepare_run(data, run_id, mode="simulation", previous=None, completed_drafts=None):
    if mode not in ("simulation", "analysis"):
        raise ValueError("Preparation only supports simulation or analysis, never execution")
    if previous:
        compare_context(data, previous)
    reviews, metrics = {}, {}
    previous_teams = previous.get("team_reviews", {}) if previous else {}
    for abbreviation, team in sorted(data.teams.items()):
        modules = team_modules(data, team, completed_drafts)
        values = {**finance.metrics(data, team), **roster.metrics(data, team)}
        results = assess(data, team, "results")["values"]
        efficiency_values = assess(data, team, "efficiency")["values"]
        values["win_percentage"] = calculations.win_percentage(results["total_wins"], results["total_losses"], team["state"].get("total_games"))
        values["net_rating"] = calculations.difference(efficiency_values["ortg"], efficiency_values["drtg"], unit="points_per_100")
        for name, metric in values.items():
            metrics[f"{abbreviation}.{name}"] = metric
        old = previous_teams.get(abbreviation)
        strategic = franchise.profile(data, abbreviation, old.get("profile", {}).get("lifecycle") if old else None)
        strategic["roster_construction_issues"] = {"position_distribution": values["positions"], "contract_terms": values["contract_terms"],
                                                   "role_depth": "UNKNOWN_PENDING_ROLE_AND_MINUTES_DATA"}
        strategic["goals"]["short_term"]["evidence"] = [f"{abbreviation}.positions", f"{abbreviation}.roster_count"]
        strategic["goals"]["medium_term"]["evidence"] = [f"{abbreviation}.contract_terms"]
        changes = calculations.field_changes(old["observed_state"], team["state"]) if old else None
        reviews[abbreviation] = {"profile": strategic, "observed_state": team["state"], "modules": modules,
                                 "observed_roster": team["roster"],
                                 "roster_changes_from_previous": calculations.roster_changes(old["observed_roster"], team["roster"]) if old and "observed_roster" in old else None,
                                 "changes_from_previous": changes,
                                 "change_explanation": "已观测字段变化，不推断因果或自动改变战略。" if old else "首次分析，无前次已确认战略。"}
    missing = sorted({gap for review in reviews.values() for module in review["modules"].values() for gap in module["missing_data"]})
    return deepcopy({"schema_version": 1, "engine_version": VERSION, "calculation_version": calculations.VERSION,
            "gm_run_id": run_id, "career_id": data.source.career_id, "source": asdict(data.source),
            "policy": {"policy_id": data.policy["policy_id"], "rules_commit": data.rules_commit,
                       "gm_policy_id": data.gm_policy["policy_id"], "gm_policy_status": data.gm_policy["configuration_status"]},
            "status": "SIMULATION" if mode == "simulation" else "ANALYSIS_ONLY",
            "readiness": "PARTIAL" if missing else "READY", "teams_reviewed": len(reviews),
            "team_reviews": reviews, "calculations": metrics, "missing_data": missing,
            "decisions": [], "market_discussion": {"status": "WEB_GM_REVIEW_REQUIRED", "offers": []},
            "execution_authorized": False, "confirmed_history_written": False,
            "extensions": data.gm_policy["extensions"]})


def markdown(run):
    def show(value):
        if isinstance(value, dict) and "availability" in value:
            return "UNKNOWN: " + str(value.get("reason")) if value["availability"] == "UNKNOWN" else str(value.get("value", value.get("reference_year", "REFERENCE")))
        if isinstance(value, list):
            return f"{len(value)} 条记录，详细字段见本队 JSON"
        return "UNKNOWN" if value is None else str(value)
    lines = [f"# GM v1.0 {'模拟' if run['status'] == 'SIMULATION' else '准备'}回合：{run['gm_run_id']}", "",
             f"状态：{run['status']}；经营配置待玩家确认；本文件不是正式游戏决策。", "",
             f"存档：{run['career_id']}；游戏日期：{run['source']['game_date']}。",
             f"数据更新时间：{run['source']['data_updated_at']}；上传时间：{run['source']['uploaded_at']}。",
             f"数据批次：{run['source']['batch_id']}；来源 commit：{run['source']['source_commit']}。", "",
             "## 联盟交付", "", f"独立审查 {run['teams_reviewed']} 队，每队 12 个经营模块。正式操作方案为 0；后续由玩家触发网页 GM。", ""]
    for abbreviation, review in run["team_reviews"].items():
        profile = review["profile"]
        lines += [f"## {abbreviation} · {profile['team'].get('city', '')} {profile['team'].get('name', '')}", "",
                  f"生命周期：{profile['lifecycle']['state']}（{profile['lifecycle']['status']}）。", "",
                  f"文化参考：{profile['culture_reference']['file'] or 'UNKNOWN'}；不能把参考预测当成本局事实。", ""]
        for name, module in review["modules"].items():
            lines += [f"### {name} — {module['readiness']} / {module['evaluation']}", "",
                      "；".join(module["analysis"]), "",
                      "已知事实/确定性结果：" + "；".join(f"{key}={show(value)}" for key, value in module["facts"].items()), "",
                      f"缺失：{'；'.join(module['missing_data']) or '无当前接口必需缺口'}", "",
                      f"待 GM 判断：{'；'.join(module['strategic_suggestions'])}", ""]
    lines += ["## 待审批与下一阶段", "", "本模拟未批准或执行任何操作。交易兴趣、正式提案、规则校验、玩家批准、执行回读是独立状态。",
              "v2/v3 仅预留接口；完整交易、谈判、长期历史与世界线自动进度待后续玩家指令。", ""]
    return "\n".join(lines)
