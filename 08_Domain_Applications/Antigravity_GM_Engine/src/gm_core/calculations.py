"""Pure, deterministic arithmetic. Missing/invalid inputs never become zero."""
import math

VERSION = "gm_calculations_v1"


def number(value):
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        return False


def result(value=None, reason=None, inputs=None, unit=None):
    return {"availability": "UNKNOWN" if reason else "CALCULATED", "value": value if not reason else None,
            "reason": reason, "inputs": inputs, "unit": unit, "calculation_version": VERSION}


def difference(left, right, unit="USD"):
    inputs = {"left": left, "right": right}
    if not all(number(value) for value in inputs.values()):
        return result(reason="MISSING_OR_INVALID_INPUT", inputs=inputs, unit=unit)
    value = left - right
    return result(value, inputs=inputs, unit=unit) if number(value) else result(reason="NUMERIC_OVERFLOW", inputs=inputs, unit=unit)


def observed_sum(values, unit="USD"):
    try:
        values = list(values)
    except TypeError:
        return result(reason="MISSING_OBSERVED_VALUES", unit=unit)
    if not values or not all(number(value) and value >= 0 for value in values):
        return result(reason="INCOMPLETE_OBSERVED_VALUES", inputs=values, unit=unit)
    total = sum(values)
    return result(total, inputs=values, unit=unit) if number(total) else result(reason="NUMERIC_OVERFLOW", inputs=values, unit=unit)


def distribution(values, kind):
    if values is None or kind not in ("position", "contract_years"):
        return result(reason="MISSING_VALUES_OR_UNKNOWN_DISTRIBUTION")
    values = list(values)
    valid = lambda item: item in ("PG", "SG", "SF", "PF", "C") if kind == "position" else type(item) is int and item >= 0
    if not values or not all(valid(item) for item in values):
        return result(reason=f"INCOMPLETE_{kind.upper()}", inputs=values)
    return result({str(item): values.count(item) for item in sorted(set(values), key=str)}, inputs=values)


def win_percentage(wins, losses, games=None):
    inputs = {"wins": wins, "losses": losses, "games": games}
    if any(type(value) is not int or value < 0 for value in (wins, losses)):
        return result(reason="MISSING_OR_INVALID_RESULTS", inputs=inputs)
    played = wins + losses
    if played == 0:
        return result(reason="NO_GAMES", inputs=inputs)
    if games is not None and (type(games) is not int or games != played):
        return result(reason="CONFLICTING_GAME_COUNTS", inputs=inputs)
    return result(round(wins / played, 6), inputs=inputs, unit="fraction")


def efficiency(points, possessions):
    if not number(points) or not number(possessions) or points < 0 or possessions <= 0:
        return result(reason="MISSING_OR_INVALID_POSSESSIONS", inputs={"points": points, "possessions": possessions})
    value = points / possessions * 100
    if not number(value):
        return result(reason="NUMERIC_OVERFLOW", inputs={"points": points, "possessions": possessions})
    return result(round(value, 6), inputs={"points": points, "possessions": possessions}, unit="points_per_100")


def field_changes(before, after):
    if not isinstance(before, dict) or not isinstance(after, dict):
        return result(reason="TWO_OBSERVED_RECORDS_REQUIRED")
    return {key: {"before": before.get(key), "after": after.get(key)}
            for key in sorted(before.keys() | after.keys()) if before.get(key) != after.get(key)}


def roster_changes(before, after):
    if not isinstance(before, list) or not isinstance(after, list):
        return result(reason="TWO_OBSERVED_ROSTERS_REQUIRED")
    def index(rows):
        indexed = {}
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("PLAYER_IDENTITY_UNKNOWN")
            name, face = row.get("player_name"), row.get("face_id")
            if not isinstance(name, str) or type(face) is not int:
                raise ValueError("PLAYER_IDENTITY_UNKNOWN")
            key = (name.casefold().strip(), face)
            if key in indexed:
                raise ValueError("PLAYER_IDENTITY_CONFLICT")
            indexed[key] = row
        return indexed
    try:
        left, right = index(before), index(after)
    except ValueError as error:
        return result(reason=str(error))
    return result({"added": [right[key] for key in sorted(right.keys() - left.keys())],
                   "removed": [left[key] for key in sorted(left.keys() - right.keys())],
                   "changed": [{"identity": list(key), "fields": field_changes(left[key], right[key])}
                               for key in sorted(left.keys() & right.keys()) if left[key] != right[key]]},
                  inputs="Snapshot name+face_id comparison; not a persistent real-person identity")


def draft_year(completed_drafts):
    if type(completed_drafts) is not int or completed_drafts < 0:
        return result(reason="PLAYER_CONFIRMED_DRAFT_COUNT_REQUIRED", inputs=completed_drafts)
    return result({"next_class_year": 1984 + completed_drafts % 37, "cycle": completed_drafts // 37 + 1,
                   "completed_drafts": completed_drafts}, inputs=completed_drafts)


def salary_exchange(outgoing, incoming):
    sent = observed_sum(outgoing)
    received = observed_sum(incoming)
    return {"sent": sent, "received": received,
            "payroll_change": difference(received["value"], sent["value"]), "cba_legality": "UNKNOWN"}


def draft_pick_window(next_draft_year):
    if type(next_draft_year) is not int or not 2000 <= next_draft_year <= 2100:
        return result(reason='VERIFIED_NEXT_DRAFT_YEAR_REQUIRED', inputs=next_draft_year)
    return result({'tradeable_draft_years': list(range(next_draft_year, next_draft_year + 3)),
                   'protection_conditions': 'NOT_USED', 'swap_rights': 'NOT_USED'},
                  inputs={'next_draft_year': next_draft_year, 'maximum_future_drafts': 3}, unit='draft_year')
