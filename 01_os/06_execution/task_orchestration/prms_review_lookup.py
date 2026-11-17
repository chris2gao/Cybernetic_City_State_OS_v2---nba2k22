"""Read-only PRMS Run review lookup; no new approval store or identity platform.

Only an EXPLICIT exact-digest Human prototype review can be used as approval.
General Human architecture/mode decisions never become prototype approvals.
The Host chooses the Run directory and independently verifies the Human source.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Callable

from reviewed_prototypes import HumanReview


SCHEMA = "citystate.prms.human-prototype-reviews.v1"


@dataclass(frozen=True)
class PRMSReviewLookup:
    """Host-supplied Run path and source provenance verifier, read-only."""

    run_root: Path
    task_scope: str
    verify_human_source: Callable[[Path, str, str], bool]

    def __call__(self, prototype_key: str, prototype_digest: str) -> HumanReview | None:
        if not (self.task_scope and len(prototype_digest) == 64):
            return None
        manifest = self.run_root / "HUMAN_PROTOTYPE_REVIEWS.json"
        if not manifest.is_file():
            return None
        try:
            doc = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if (not isinstance(doc, dict) or doc.get("schema") != SCHEMA
                or doc.get("task_scope") != self.task_scope
                or not isinstance(doc.get("reviews"), list)):
            return None
        matched = [item for item in doc["reviews"] if (
            isinstance(item, dict)
            and item.get("prototype_key") == prototype_key
            and item.get("prototype_digest") == prototype_digest)]
        if len(matched) != 1:
            return None
        rec = matched[0]
        if (set(rec) != {"prototype_key", "prototype_digest", "decision", "decision_ref",
                         "source_file", "source_sha256"}
                or rec["decision"] != "APPROVED"
                or not isinstance(rec["decision_ref"], str)
                or not rec["decision_ref"].strip()
                or not isinstance(rec["source_file"], str)
                or not isinstance(rec["source_sha256"], str)):
            return None
        # Review source must be an existing local PRMS file, not an arbitrary
        # absolute path or caller-provided approval flag.
        relative = Path(rec["source_file"])
        if (relative.is_absolute() or ".." in relative.parts
                or len(relative.parts) != 1 or relative.suffix != ".md"):
            return None
        path = self.run_root / relative
        try:
            content = path.read_bytes()
        except OSError:
            return None
        if hashlib.sha256(content).hexdigest() != rec["source_sha256"]:
            return None
        # Caller must be a trusted Host/foreground Human reviewing PRMS,
        # not an Agent-generated lambda that declares its own approval.
        if self.verify_human_source(path, prototype_key, prototype_digest) is not True:
            return None
        return HumanReview(prototype_key, prototype_digest, rec["decision_ref"], True)
