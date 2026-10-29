# PRMS implementation decisions

These are bounded engineering choices under approved A-RC02/B-RC01. They do not
change product architecture or authorize production deployment.

1. **Python foreground adapters and canonical JSON.** Extend the existing Python
   context tooling. Reuse PyYAML, JSON Schema validation and existing lifecycle
   classification. UTF-8 canonical JSON and immutable Git blob/commit references
   allow exact reproduction without a second database or workflow engine.
2. **Single authoritative state ref initially.** Events, owner, checkpoint,
   publication record and CURRENT enter one candidate Git tree. Actual expected-
   parent `update-ref` supplies local CAS. Multiple roles may contend on this ref;
   a loser must reread rather than silently overwrite or blindly retry. There is
   no cross-ref or cross-repository atomicity claim.
3. **Enforcement is a deployment capability.** Local tests have a deliberately
   cooperative mode. Same-principal Git bypass is demonstrated and returns a
   production-blocking result. Isolated-session issuance refuses remote backends.
   A GitHub protocol adapter does not authenticate clients or prove platform ACLs;
   a separately authorized trusted ingress and negative platform tests are still
   required. No host credential is stored in a source file or receipt.
4. **Discovery is not activation.** Enumerate frozen source trees and reconcile
   registry patterns rather than freezing the planning-time counts. Source scan
   completeness, registry consistency, publication records, loading and execution
   rights are separate outputs. Core effectiveness comes from its existing
   inventory. None of these mechanisms acquires an independently verified L4
   claim from this implementation.
5. **Generic domain sources.** Consume the current domain identity and optional
   module registry reference. Legacy module registries can be discovered as
   candidates under 08; their own `module_base` constrains relative references.
   No NBA installation path is hardcoded into Core runtime discovery. Directory
   references require explicit expansion and do not trigger recursive injection.
   Core-governance navigation refers back to B0. Only matching owner/publication
   records in 09 can describe published G2, and record verification is not Human
   identity authentication.
6. **Plan-bound recovery.** A host-retained plan and this session's Human choice
   are required for verification. Re-resolve source bytes and the actual catalog;
   reject removed requirements, substituted choices and invented body hashes.
   Budget accounting uses bytes, not an invented model token multiplier. Required
   material is not truncated. Checkpoint lag and undurable history are explicit.
7. **History and copy.** Events are append-only, corrections preserve originals,
   and UTC recording time differs from observation time. Copies preserve actual
   content bytes and lineage while issuing a new target CURRENT; operational
   ownership and assignments are not inherited. Copy retries use a durable
   operation record. Derived excerpts retain omission counts and source hashes.
8. **Compatibility evidence.** A local Git three-way merge preserves domain-owned
   09 and contains no role state in the Core merge tree. The long-path fixture
   exposed that a fresh Windows clone does not inherit local `core.longpaths`;
   the domain generator now enables it for clone and the resulting checkout.
   No existing domain master was merged or modified by that experiment.

Production permissions, real model-window recovery and independent final review
are external acceptance evidence, not values this Owner may fill with assertions.
The pinned planning archive and per-scenario evidence remain the requirements
authority; passing the local suite cannot erase an unmet scenario.
