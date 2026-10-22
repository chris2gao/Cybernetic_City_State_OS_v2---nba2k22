"""Read cultural reference snippets without adopting their forecasts as facts."""


def reference(data, abbreviation):
    paths = sorted((data.root / "docs/team_dossiers").glob(f"*_{abbreviation}_*.md"))
    excerpts = []
    if paths:
        with paths[0].open(encoding="utf-8-sig") as stream:
            for index, line in enumerate(stream, 1):
                if any(tag in line for tag in ("性格标签", "建队哲学", "篮球哲学")):
                    excerpts.append({"line": index, "text": line.strip(), "availability": "REFERENCE"})
                if len(excerpts) >= 3:
                    break
    return {"availability": "REFERENCE" if paths else "UNKNOWN",
            "file": paths[0].relative_to(data.root).as_posix() if paths else None,
            "excerpts": excerpts, "adoption_status": "PROPOSED_PENDING_PLAYER_CONFIRMATION",
            "owner_style": None, "spending_preference": None,
            "warning": "仅文化参考；老板身份、预定交易、冠军和数值不作为本局事实，偏好待玩家确认。"}
