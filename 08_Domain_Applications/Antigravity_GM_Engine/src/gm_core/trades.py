"""v1 describes constraints and observed salaries; v2 negotiation is deferred."""
from .calculations import salary_exchange, result, draft_pick_window
from .coverage import player_value
from .models import module_result
import json


def player_valuation(player):
    fields = ("overall_rating", "age", "potential", "salary_current_year", "contract_years_left")
    missing = [key for key in fields if player.get(key) is None]
    return result(reason="MISSING_OBSERVED_FIELDS: " + ",".join(missing) if missing else "VALUATION_MODEL_DEFERRED_V2",
                  inputs={key: player.get(key) for key in fields})


def constraints(data, assets):
    errors = []
    missing = []
    seen = set()
    draft_catalog = None
    if any(asset.get('kind') == 'draft_pick' for asset in assets):
        path = data.batch_directory / 'draft_assets.json'
        if path.is_file():
            draft_catalog = json.loads(path.read_text(encoding='utf-8'))
    for asset in assets:
        identity = (asset.get("kind"), asset.get("asset_id"))
        if not identity[1]:
            errors.append("ASSET_ID_REQUIRED")
        elif identity in seen:
            errors.append("DUPLICATE_ASSET")
        seen.add(identity)
        if asset.get('kind') in ('pick_swap', 'draft_pick_swap', 'swap_right'):
            errors.append('ONLY_SIMPLE_DRAFT_PICKS_ALLOWED')
        if str(asset.get("player_name", "")).casefold().strip() in {name.casefold().strip() for name in data.gm_policy["protected_player_names"]}:
            errors.append("PROTECTED_PLAYER")
        if asset.get('kind') == 'draft_pick':
            if not draft_catalog or draft_catalog.get('ownership_verified') is not True or draft_catalog.get('metadata_verified') is not True:
                missing.append('DRAFT_PICK_OWNERSHIP_UNKNOWN')
                continue
            observed = next((row for row in draft_catalog['records'] if row.get('asset_id') == asset.get('asset_id')), None)
            if observed is None:
                errors.append('DRAFT_PICK_NOT_IN_OBSERVED_CATALOG')
                continue
            if any(key in asset and asset[key] != observed[key] for key in ('draft_year', 'draft_round', 'original_owner_team_id', 'current_owner_team_id')):
                errors.append('DRAFT_PICK_SOURCE_CONFLICT')
            window = draft_pick_window(draft_catalog.get('next_draft_year'))
            if window['availability'] == 'UNKNOWN':
                missing.append('VERIFIED_NEXT_DRAFT_YEAR_REQUIRED')
            elif observed['draft_year'] not in window['value']['tradeable_draft_years']:
                errors.append('DRAFT_PICK_OUTSIDE_THREE_YEAR_WINDOW')
            if asset.get('offering_team_id') is None:
                missing.append('DRAFT_PICK_OFFERING_TEAM_REQUIRED')
            elif asset['offering_team_id'] != observed['current_owner_team_id']:
                errors.append('DRAFT_PICK_NOT_OWNED_BY_OFFERING_TEAM')
            if any(asset.get(key) not in (None, False, '', 'NONE', 'NOT_USED', [], {}) for key in ('protection', 'swap', 'swap_rights')):
                errors.append('ONLY_SIMPLE_DRAFT_PICKS_ALLOWED')
    return {"legality": "ILLEGAL" if errors else "UNKNOWN", "errors": errors,
            "missing_data": missing + ["游戏执行规则和玩家具体批准；v1 不签发完整 CBA 结论"],
            "executable": False, "approval_status": "NOT_GRANTED"}


def analyze(data, team):
    salaries = [player_value(data, player, "salary_current_year") for player in team["roster"]]
    return module_result("trades", {"observed_player_salaries": salaries or None},
        ["可以讨论需求或询价；本模块不自动撮合、不估造 OVR，不把主观动机当成成交或合法性。"],
        ["球员综评/年龄、已确认选秀权资产及游戏执行规则"],
        ["由双方独立表达利益，正式方案待数据补齐并由玩家批准。"])


def exchange(outgoing, incoming):
    return salary_exchange(outgoing, incoming)
