"""
VAE Knowledge Revision Manager (R08).
Fixes F03: Enforces initial status as PENDING_REVISION (not APPENDED).
Fixes F04: Enforces append-only idempotency via deterministic key de-duplication.
Fixes P1-05: Durable file-backed persistence; fresh instances reload ledger and retain duplicate protection.
"""

from typing import Dict, Any, List, Set, Tuple, Optional
import datetime
import os
import json
import uuid
from .contracts import KnowledgeRevision, RevisionStatus


class VAEKnowledgeRevisionManager:
    """
    Manages knowledge base revisions with strict append-only idempotency and state machine transitions.
    Supports durable file-based persistence (e.g. JSONL) across process restarts.
    """

    def __init__(self, ledger_path: Optional[str] = None):
        self.ledger_path = ledger_path
        self.committed_keys: Set[str] = set()
        self.ledger: List[KnowledgeRevision] = []

        if self.ledger_path and os.path.exists(self.ledger_path):
            self._load_from_file()

    def _load_from_file(self) -> None:
        """Loads committed revisions from the persistent JSONL ledger file."""
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    rev = KnowledgeRevision.from_dict(data)
                    self.ledger.append(rev)
                    self.committed_keys.add(rev.idempotency_key)
        except Exception:
            pass

    def propose_revision(
        self,
        trial_id: str,
        prior_claim_ref: str,
        new_claim: str,
        counterexamples: List[str],
        source_refs: List[str],
    ) -> KnowledgeRevision:
        """
        Creates a proposed revision.
        Initial status is strictly PENDING_REVISION (Fixes F03).
        """
        rev = KnowledgeRevision.create_pending(
            trial_id=trial_id,
            prior_claim_ref=prior_claim_ref,
            new_claim=new_claim,
            counterexamples=counterexamples,
            source_refs=source_refs,
        )
        # Check idempotency upfront
        if rev.idempotency_key in self.committed_keys:
            rev.status = RevisionStatus.DUPLICATE_REJECTED
        return rev

    def commit_append(
        self,
        revision: KnowledgeRevision,
    ) -> Tuple[bool, KnowledgeRevision, str]:
        """
        Appends a revision to the knowledge ledger.
        Fails if duplicate idempotency key is detected (Fixes F04, P1-05).
        Persists to disk if ledger_path is configured.
        """
        if revision.idempotency_key in self.committed_keys:
            revision.status = RevisionStatus.DUPLICATE_REJECTED
            return False, revision, f"DUPLICATE_REJECTED: Idempotency key {revision.idempotency_key} already committed"

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        receipt = {
            "receipt_id": f"rcpt-{uuid.uuid4().hex[:8]}",
            "committed_at": now_str,
            "ledger_index": len(self.ledger),
            "idempotency_key": revision.idempotency_key,
        }

        # Transition status from PENDING_REVISION to APPENDED
        revision.revision_time = now_str
        revision.append_receipt = receipt
        revision.status = RevisionStatus.APPENDED

        # Record in memory
        self.committed_keys.add(revision.idempotency_key)
        self.ledger.append(revision)

        # Fixes P1-05: Durable file append
        if self.ledger_path:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(self.ledger_path)), exist_ok=True)
                with open(self.ledger_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(revision.to_dict(), ensure_ascii=False) + "\n")
                    f.flush()
            except Exception as e:
                return True, revision, f"Appended in-memory, but durable write failed: {e}"

        return True, revision, "Committed successfully to durable knowledge ledger"
