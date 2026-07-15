# Human–AI Communication Compliance Gate — validation evidence

## Release topology

- parent: `4530b4f684f64cc7928884cf96d9a221aa5a2b8a`
- semantics precursor: `c9f10d3bb311e51c082c25d885349ada35866aca`
- final semantics: `65fb2a0a7b4979b887aa1ba2aef454bb7b783ca4`
- binding: immediate child, exact SHA carried only by the external review pointer
- policy `source_mailbox_base_head`: `d235e602c14250d16b91f2897cb8308e031cc13c`
- policy `protocol_release_head`: `65fb2a0a7b4979b887aa1ba2aef454bb7b783ca4`

## Executed checks

1. `python -m py_compile` for validator, generator and tests: pass.
2. Draft 2020-12 validation for every local schema: pass.
3. Deterministic fixture regeneration: aggregate generated digest
   `80399fe788e519172a90b479da1cf49c4e683b7b8cbd918d09c76d3baa847e54`
   on two consecutive runs.
4. Full suite: `161/161`, comprising `79` immutable inherited parent cases and
   `82` executed v2 cases; exact results, exit codes and violation sets match.
5. Unit/CLI suite: `14/14` pass, including tree-object, symlink, submodule,
   mutable test-fixture cache, state graph and release topology checks.
6. Cross-environment suite stdout: SHA-256
   `aad755419bf02fca47c15dba2284bc0c4f928bed93150608e7d87346d8f815c7`
   for both UTC/hash-seed 1 and Pacific-Kiritimati/hash-seed 98765.
7. Required proof attacks: schema-valid handcrafted pass with matching artifact
   digest; fabricated resolved status; post-validation event mutation; another
   event/task result; mutable/missing/tree/symlink/submodule/digest attacks for
   event, STATE, validation and pointer refs; from-state mismatch; unreachable
   edge; Human role impersonation; C2 missing/wrong/replayed/forged authority;
   ledger deletion/mutation/reorder/rollback/mutable recurrence — all rejected.
8. Positive flow: four release receipts, Human direct dispatch, exact optional
   stored result, full dispatch/completion/revision/completion/acceptance loop,
   C2 test-boundary authority and valid ledger append — all pass.

## Boundary assertions

- Validation provenance is fresh repository evidence, not Human authority.
- Human origin attestation authenticates an actor channel, not C2 permission.
- `AuthorizationContext` is separately injected and never model-self-issued.
- A transition proof is not an execution lock; host CAS and atomic authority
  consumption remain required.
- Repository validation does not intercept arbitrary live UI/model output.
