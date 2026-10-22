"""Player-confirmed game context, bound into the audited SQLite snapshot notes."""
import base64
from datetime import date
import json

PREFIX = "CAPTURE_CONTEXT_V1:"


def decode_context(notes):
    if not isinstance(notes, str) or not notes.startswith(PREFIX):
        return {"purpose": "validation", "game_date": None, "game_date_provenance": "UNCONFIRMED", "event": "legacy_capture"}
    context = json.loads(base64.b64decode(notes[len(PREFIX):], validate=True).decode("utf-8"))
    if context.get("trigger") != "PLAYER_INITIATED":
        raise ValueError("Capture context must declare the player trigger")
    if context.get("purpose") not in ("production", "validation"):
        raise ValueError("Invalid capture purpose")
    if context.get("game_date"):
        date.fromisoformat(context["game_date"])
    explicit_current_unknown = context.get('game_date') is None and context.get('game_date_provenance') == 'PLAYER_AUTHORIZED_CURRENT_DATE_UNKNOWN'
    if context["purpose"] == "production" and not explicit_current_unknown and (not context.get("game_date") or context.get("game_date_provenance") != "USER_CONFIRMED"):
        raise ValueError("Production context requires a player-confirmed game date")
    return context
