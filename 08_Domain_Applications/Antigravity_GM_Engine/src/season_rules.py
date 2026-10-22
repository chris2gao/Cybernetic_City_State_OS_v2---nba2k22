# -*- coding: utf-8 -*-
"""Load the season rules maintained in the reusable save template."""
import json
import os
from typing import Dict, Optional


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(PROJECT_DIR, "database", "templates", "save_template.json")


def load_configured_season_rules(season_year: Optional[int] = None) -> Dict:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as source:
        template = json.load(source)
    configured_year = int(template["default_season_year"])
    requested_year = configured_year if season_year is None else int(season_year)
    if requested_year != configured_year:
        raise ValueError(
            f"当前模板只包含 {configured_year-1}-{configured_year} 赛季规则；"
            "其他年份需先更新经过确认的模板数据。"
        )

    rules = {
        "season_year": configured_year,
        "season_code": f"{configured_year-1}-{configured_year}",
        "salary_cap": int(template["salary_cap"]),
        "luxury_tax_threshold": int(template["luxury_tax_threshold"]),
        "first_apron": int(template["first_apron"]),
        "historical_draft_class_year": int(template["historical_draft_class_year"]),
    }
    if min(rules["salary_cap"], rules["luxury_tax_threshold"], rules["first_apron"]) <= 0:
        raise ValueError("模板中的工资帽、奢侈税线和第一土豪线都必须为正数。")
    if not rules["salary_cap"] < rules["luxury_tax_threshold"] < rules["first_apron"]:
        raise ValueError("模板中的工资帽、奢侈税线、第一土豪线顺序无效。")
    if rules["historical_draft_class_year"] < 1947:
        raise ValueError("模板中的历史选秀年份无效。")
    return rules
