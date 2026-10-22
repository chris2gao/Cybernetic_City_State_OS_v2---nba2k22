"""Read published JSON only. No source hashes, databases, network or game imports."""
from datetime import date, datetime
import json
from pathlib import Path
import re
import subprocess

from .models import PublishedData, Source


def load_json(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def safe_child(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Path leaves its data directory")
    return path


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", value):
        raise ValueError("Invalid career/run identifier")
    return value


def attach_coaching_opponents(snapshot,payload):
    """Attach one published owner file with the same source binding, offline."""
    if any(payload.get(k)!=snapshot.get(k) for k in ('career_id','source_batch_id','game_date','data_updated_at')):
        raise ValueError('Opponent source must match snapshot career/batch/date/update time')
    teams=[t for t in snapshot['teams'] if t['team_id']==payload.get('team_id')]
    if len(teams)!=1 or teams[0].get('gameplans'):
        raise ValueError('Missing team or duplicate opponent source')
    records=payload['records']
    opponents=[g['opponent_team_id'] for g in records]
    expected={t['team_id'] for t in snapshot['teams']}-{payload['team_id']}
    if len(opponents)!=29 or len(set(opponents))!=29 or set(opponents)!=expected:
        raise ValueError('Opponent source requires the exact other 29 teams')
    teams[0]['gameplans']=[dict(opponent_team_id=g['opponent_team_id'],is_in_use=g['is_in_use_raw'],
        overall_defense=g.get('overall_defense'),readiness=g['readiness']) for g in records]


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("A published timestamp is required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include its timezone")
    return parsed


def git_revision(root, relative):
    result = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%H", "--", relative],
                            capture_output=True, text=True)
    return result.stdout.strip() or None


class DataReader:
    def __init__(self, project_root):
        self.root = Path(project_root).resolve()

    def read(self, career_id, previous_data_updated_at=None):
        career_id = identifier(career_id)
        published = self.root / "published"
        entry = load_json(published / "index.json")["careers"][career_id]
        pointer_path = safe_child(published, entry["latest"])
        expected = published / "saves" / career_id / "latest.json"
        if pointer_path != expected.resolve():
            raise ValueError("Index does not select the requested career")
        pointer = load_json(pointer_path)
        if pointer.get("save_id") != career_id or pointer.get("purpose") != "production":
            raise ValueError("GM preparation requires the selected production career")
        updated = timestamp(pointer.get("data_updated_at"))
        uploaded = timestamp(pointer.get("uploaded_at"))
        if uploaded < updated:
            raise ValueError("Upload time precedes the data update")
        if pointer.get("upload_status") != "UPLOADED":
            raise ValueError("Publication has not completed")
        if previous_data_updated_at and updated < timestamp(previous_data_updated_at):
            raise ValueError("Data predates the selected previous run; use a separate branch")
        if pointer["game_date"] is not None:
            date.fromisoformat(pointer["game_date"])
        directory = safe_child(published / "saves" / career_id, Path(pointer["batch_path"]).relative_to(f"saves/{career_id}"))
        league = load_json(directory / "league.json")
        teams = {}
        for state in league["teams"]:
            abbreviation = state["team_abbr"]
            if not re.fullmatch(r"[A-Z0-9]{2,4}", abbreviation) or abbreviation in teams:
                raise ValueError("Ambiguous team identity")
            team = load_json(directory / "teams" / f"{abbreviation}.json")
            if team["identity"].get("abbreviation") != abbreviation or team["identity"].get("team_id") != state.get("team_id"):
                raise ValueError("Team identity does not match the selected published team")
            teams[abbreviation] = team
        gameplay = load_json(self.root / "config/gameplay_policy.json")
        source = Source(career_id, pointer["batch_id"], pointer["data_updated_at"], pointer["uploaded_at"],
                        pointer["game_date"], pointer.get("source_commit") or git_revision(self.root, pointer_path.relative_to(self.root).as_posix()),
                        pointer["batch_path"])
        staff_path = directory / "staff.json"
        coaching={}
        coaching_path=directory/'coaching/teams.json'
        coverage=load_json(directory / 'source_coverage.json')
        if coaching_path.exists():
            coaching=load_json(coaching_path)
            statuses={s['id']:s['status'] for s in coverage.get('sources',[])}
            if (statuses.get('coaching_tactics')!='VERIFIED_OBSERVED_SAME_BATCH'
                or coaching.get('career_id')!=career_id or coaching.get('source_batch_id')!=pointer['batch_id']
                or coaching.get('data_updated_at')!=pointer['data_updated_at']
                or coaching.get('game_date')!=pointer['game_date']):
                raise ValueError('Coaching source is not bound to the selected published batch')
            rows={t['team_id']:t for t in coaching['teams']}
            if len(rows)!=30 or len(coaching['teams'])!=30 or set(rows)!={t['identity']['team_id'] for t in teams.values()}:
                raise ValueError('Coaching source requires exactly the selected 30 teams')
            for team in teams.values():team['coaching']=rows[team['identity']['team_id']]
        return PublishedData(source, gameplay, load_json(self.root / "config/gm_policy.json"),
                             git_revision(self.root, "config/gameplay_policy.json"), league, teams,
                             coverage, load_json(directory / "calculations.json"),
                             load_json(staff_path) if staff_path.exists() else {}, self.root, directory,coaching)

    def coaching_opponent(self,data,team_id,opponent_team_id):
        rows=[t for t in data.coaching.get('teams',[]) if t['team_id']==team_id]
        if len(rows)!=1 or opponent_team_id==team_id:
            raise ValueError('Unknown coaching team or self opponent')
        payload=load_json(safe_child(data.batch_directory,rows[0]['opponent_file']))
        if (payload.get('career_id')!=data.source.career_id or payload.get('source_batch_id')!=data.source.batch_id
            or payload.get('data_updated_at')!=data.source.data_updated_at or payload.get('team_id')!=team_id
            or payload.get('game_date')!=data.source.game_date):
            raise ValueError('Opponent source batch mismatch')
        opponents=[g['opponent_team_id'] for g in payload['records']]
        expected={t['team_id'] for t in data.coaching['teams']}-{team_id}
        if len(opponents)!=29 or len(set(opponents))!=29 or set(opponents)!=expected:
            raise ValueError('Opponent source requires the exact other 29 teams')
        records=[g for g in payload['records'] if g['opponent_team_id']==opponent_team_id]
        if len(records)!=1:raise ValueError('Missing or ambiguous opponent')
        return records[0]

    def draft_catalog(self, data, year):
        catalog_root = data.batch_directory / "player_catalog"
        index = load_json(catalog_root / "index.json")
        records = []
        for relative in index["years"].get(str(year), []):
            records.extend(load_json(safe_child(data.batch_directory, relative))["records"])
        return records
