# Bridge Slot Teaching Contract

Status: LRP-02 canonical contract draft for review.

This document defines how a Math Mentor bridge record can appear inside a target-node lesson as a first-class teaching slot. It does not generate bridges, migrate legacy bridges, change `BRIDGE_SCHEMA.md`, update indexes, activate Coordinator runtime, or approve any bridge for formal consumption.

## 1. Purpose

A bridge slot is the teaching-time representation of a knowledge-graph edge. It lets the student see how the current node connects to prior knowledge, same-level structure, cross-layer structure, or future outlook.

Bridge slots must support system-building without becoming metadata dumps.

## 2. Source Bridge Types

Allowed bridge types inherit from `BRIDGE_SCHEMA.md`:

- `intra_layer`;
- `cross_layer`;
- `prerequisite_bridge`;
- `forward_outlook_bridge`.

Only canonical bridge records with explicit endpoints can be consumed as formal teaching content. Legacy bridge records with ambiguous endpoints are omitted and flagged for migration.

## 3. Bridge Slot Object

```json
{
  "slot_id": "bridge-slot-1",
  "bridge_id": "BRIDGE-015",
  "title": "bridge title",
  "bridge_type": "intra_layer | cross_layer | prerequisite_bridge | forward_outlook_bridge",
  "mode": "A | B | mixed",
  "from_nodes": [],
  "to_nodes": [],
  "endpoint_evidence": {},
  "learned_status": "verified | unavailable | unlearned | not_required",
  "validation_status": "computational_audit_passed | semantic_audit_passed | mixed_audit_passed | pending | legacy_unresolved | failed",
  "index_status": "indexed | unindexed",
  "teaching_status": "formal_teaching_content | teaser_only | hidden | omitted_for_migration",
  "one_sentence_connection": "logical connection to the target lesson",
  "first_use_display_required": true,
  "first_use_display_done": false,
  "comprehension_check": "one compact question",
  "limits": []
}
```

## 4. First-Use Display Rule

On first use within a target-node lesson, the teacher must display a compressed bridge slot:

```text
BRIDGE-015 / bridge title
type: intra_layer
learned_status: verified
connection: one sentence
```

When node endpoints are relevant, display endpoint identity compactly:

```text
from: n_418 / Euler formula
to: n_442 / complex-root oscillation
```

Rules:

- show bridge identity once per target-node lesson;
- include bridge id or node id, name/title, bridge type, learned status, and one-sentence logical connection;
- avoid repeatedly dumping bridge metadata after first use;
- then treat the bridge as an embedded association slot.

## 5. Learned-History Gating

Formal bridge teaching requires:

- every endpoint status is `present`;
- `prerequisite_status` is `verified`;
- `validation_status` has passed for the declared bridge mode;
- `index_status` is `indexed`;
- `learned_history_rule` is satisfied by persisted learned history, spaced-review state, registered learned state, or an explicitly valid strict-sequence fallback;
- node-ID comparison alone is not treated as mastery.

If learned history is unavailable:

- prerequisite and structural bridges become `hidden` or `teaser_only`;
- forward outlook may remain a one-sentence teaser;
- bridge content cannot become an assessment requirement.

## 6. Teaser-Only Behavior

`forward_outlook_bridge` records pointing to unlearned knowledge may appear only as:

- one sentence;
- no new definitions;
- no new notation obligations;
- no exam requirement;
- no claim that the future node has been learned.

Teasers should motivate continuity without expanding the current lesson's formal scope.

## 7. Endpoint Evidence

`endpoint_evidence` must identify why the bridge endpoints are trusted:

```json
{
  "source": "canonical_bridge_schema | unambiguous_legacy_record",
  "bridge_file": "BRIDGE-015.yaml",
  "from_nodes_resolved": true,
  "to_nodes_resolved": true,
  "node_files_checked": [],
  "limits": []
}
```

Formal use requires canonical explicit endpoint evidence. Unambiguous legacy records may inform planning but remain migration candidates unless a later stage validates them.

## 8. Legacy Bridge Omission Rule

If a legacy bridge lacks explicit endpoint and history fields:

- do not invent endpoints;
- do not infer endpoints from nearby prose when ambiguous;
- omit the bridge from formal teaching;
- add a migration note or report entry;
- use `teaching_status: omitted_for_migration`.

Legacy omission is not a teaching failure. It prevents false graph structure.

## 9. Compact Comprehension Check

The first use of a formal bridge slot requires exactly one compact comprehension check.

Example shape:

```text
Which part of the prior concept is doing work in the current definition?
```

Rules:

- one question only;
- tied to the current target lesson;
- not a full quiz;
- not repeated after the bridge has already been accepted in the same lesson;
- omitted for `hidden` slots;
- optional and non-assessable for `teaser_only` slots.

## 10. Mode-Specific Bridge Teaching

Bridge mode follows canonical bridge schema:

- Mode `A`: use everyday physical intuition and computational-audit status.
- Mode `B`: use LLM-architecture mapping and semantic-audit status; everyday physical metaphor is not the primary mapping.
- Mode `mixed`: use a reviewed transition between computable intuition and pure structure; it cannot be a fallback for uncertainty.

The lesson plan may render bridge mode as `MathLane_A`, `MathLane_B`, or `mixed` to avoid confusion with Plan 3 engine names.

## 11. Bridge Slot Failure States

Use these statuses rather than silently teaching:

- `hidden`: bridge depends on unlearned or unverifiable prerequisites.
- `teaser_only`: bridge can motivate but not define or assess.
- `omitted_for_migration`: legacy record is ambiguous.
- `blocked`: bridge is required but evidence is missing.
- `request_reprep`: current lesson cannot safely continue without fixing slot evidence.

## 12. Validation Checklist

- [ ] First-use display includes identity, title/name, type, learned status, and connection.
- [ ] Formal teaching only uses bridges with present endpoints and passed validation status.
- [ ] Learned-history gating does not use node-ID ordering as proof of mastery.
- [ ] Forward outlook to unlearned knowledge is teaser-only.
- [ ] Ambiguous legacy bridges are omitted and flagged, not invented.
- [ ] One compact comprehension check exists for each formal first-use bridge slot.
- [ ] Repeated bridge metadata dumping is forbidden.
- [ ] Bridge slots do not generate, index, migrate, or approve bridge records by themselves.
