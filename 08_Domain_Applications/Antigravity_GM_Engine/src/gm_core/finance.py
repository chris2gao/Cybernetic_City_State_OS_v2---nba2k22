from .calculations import difference, observed_sum
from .coverage import player_value, state_value
from .models import module_result


def metrics(data, team):
    payroll = state_value(data, team, "total_salary")
    rules = data.league.get("rules", {})
    return {"payroll_minus_tax_line": difference(payroll, rules.get("luxury_tax_threshold")),
            "salary_cap_minus_payroll_proxy": difference(rules.get("salary_cap"), payroll),
            "observed_roster_salary_sum": observed_sum(player_value(data, player, "salary_current_year") for player in team["roster"])}


def analyze_contracts(data, team):
    values = metrics(data, team)
    return module_result("contracts", values,
        ["工资差额是静态代理，不能据此认证可用空间、交易合法性或球队建队动机。"],
        ["大名单球员薪资"] if values['observed_roster_salary_sum']['availability'] == 'UNKNOWN' else [],
        ["按玩家要求使用大名单薪资；不扩展保障金额、死钱或完整现实 CBA 账本。"])


def analyze_business(data, team):
    keys = ("budget", "staff_budget", "cash", "fan_interest", "ticket_courtside", "ticket_lower", "ticket_upper")
    values = {key: state_value(data, team, key) for key in keys}
    return module_result("business", values,
        ["列出已观测预算、票价和关注度；cash 保留原始观测，不推断净现金流。",
         "monthly_gate_revenue 的聚合窗口未确认，不能当作可比较月度收入。"],
        [key for key, value in values.items() if value is None] + ["上座率、收入统计窗口、成本与历史票价响应"],
        ["先确认经营指标口径，再由 GM 提出待批准的经营方案。"])
