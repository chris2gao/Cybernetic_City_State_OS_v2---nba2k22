"""
VAE Knowledge Revision Manager (R08).
Fixes F03: Enforces initial status as PENDING_REVISION (not APPENDED).
Fixes F04: Enforces append-only idempotency via deterministic key de-duplication.
"""

from typing import Dict, Any, List, Set, Tuple, Optional
import datetime
import uuid
from .contracts import KnowledgeRevision, RevisionStatus


class VAEKnowledgeRevisionManager:
    """
    Manages knowledge base revisions with strict append-only idempotency and state machine transitions.
    """

    def __init__(self):
        # Set of committed idempotency keys
        self.committed_keys: Set[str] = set()
        self.ledger: List[KnowledgeRevision] = []

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
        Fails if duplicate idempotency key is detected (Fixes F04).
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

        # Record in ledger
        self.committed_keys.add(revision.idempotency_key)
        self.ledger.append(revision)

        return True, revision, "Committed successfully to knowledge ledger"
