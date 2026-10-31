from __future__ import annotations

import json
import os
import subprocess
from typing import List, Optional

from src.vae_rea_research.contracts import FieldEntry


class SharedQueueManager:
    """
    Manages the deterministic traversal of the 204 seed fields from VAE_FIELD_INVENTORY_SHARED_V1.json.
    """

    DEFAULT_QUEUE_REL_PATH = os.path.join(
        "01_os", "07_content", "_runs",
        "run-20261030-nba2k22-vae-rea-single-field-loop-001",
        "01_任务输入", "VAE_FIELD_INVENTORY_SHARED_V1.json"
    )
    GIT_QUEUE_REF = "6436515330f77c0cc5cc675b521590adeb69c5d4:01_os/07_content/_runs/run-20261030-nba2k22-vae-stage01-001/01_任务输入/VAE_FIELD_INVENTORY_SHARED_V1.json"

    def __init__(self, repo_root: Optional[str] = None) -> None:
        if repo_root is None:
            # infer repo root from file location
            cur = os.path.abspath(__file__)
            # jump up 5 levels: contracts.py -> vae_rea_research -> src -> Antigravity_GM_Engine -> 08_Domain_Applications -> repo_root
            repo_root = os.path.abspath(os.path.join(cur, "..", "..", "..", "..", ".."))
        self.repo_root = repo_root
        self._entries: List[FieldEntry] = []
        self._load_queue()

    def _load_queue(self) -> None:
        local_path = os.path.join(self.repo_root, self.DEFAULT_QUEUE_REL_PATH)
        raw_json_str = ""
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                raw_json_str = f.read()
        else:
            # fallback to git show
            try:
                proc = subprocess.run(
                    ["git", "show", self.GIT_QUEUE_REF],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                raw_json_str = proc.stdout
            except Exception as e:
                raise RuntimeError(f"Unable to load shared queue from {local_path} or git ref: {e}")

        data = json.loads(raw_json_str)
        entries_raw = data.get("field_entries", [])
        self._entries = [
            FieldEntry(
                field_id=item["field_id"],
                family=item["family"],
                source_ordinal=item["source_ordinal"],
                candidate_native_key=item["candidate_native_key"],
                display_name=item["display_name"],
                source_status=item["source_status"],
                offset_hex=item.get("offset_hex"),
                declared_raw_range=item.get("declared_raw_range", [0, 100]),
                ui_mapping=item.get("ui_mapping", "UNKNOWN"),
                consumer=item.get("consumer", "UNKNOWN"),
                effect=item.get("effect", "UNKNOWN"),
                source_ref=item.get("source_ref", ""),
            )
            for item in entries_raw
        ]

    @property
    def total_count(self) -> int:
        return len(self._entries)

    def get_entry_at(self, cursor: int) -> Optional[FieldEntry]:
        if 0 <= cursor < len(self._entries):
            return self._entries[cursor]
        return None

    def get_entry_by_id(self, field_id: str) -> Optional[FieldEntry]:
        for e in self._entries:
            if e.field_id == field_id:
                return e
        return None

    def find_cursor_for_id(self, field_id: str) -> int:
        for idx, e in enumerate(self._entries):
            if e.field_id == field_id:
                return idx
        return -1
