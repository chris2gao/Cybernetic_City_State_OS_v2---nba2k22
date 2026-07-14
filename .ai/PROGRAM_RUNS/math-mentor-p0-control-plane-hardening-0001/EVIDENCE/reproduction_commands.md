# Quantitative Evidence Reproduction

## Frozen Inputs

```text
repository: E:\newStand\study\Cybernetic_City_State_OS_v2 - teacher
source branch: master
source head: 764d03d7d0a9ad553f4f3868699b06d9de5553ea
historical Stage 0 head: cefd164472ecbb7095c1aa2c243c34fbec5b51f4
work branch: codex/math-mentor-p0-control-plane-hardening
corrected implementation head: eebd2688f099d1be035576793a70d135086d4fa6
final candidate head: report_commit_itself
```

The builder accepts only the fixed source head and reads controlled corpus,
Stage 0, and split-roadmap bytes from that Git commit. It may run from the
source commit itself or a descendant implementation commit. Its only worktree
inputs are the P0 namespace configuration and the empty resolution overlay.

The aggregate roadmap `数学知识路线图_全部.yaml` is a forbidden input. It was
not read by these commands.

## Environment

```text
Windows 10.0.19045
Python 3.14.6
Git 2.53.0.windows.2
PyYAML 6.0.3
jsonschema 4.26.0
```

Version command:

```powershell
python --version
git --version
python -B -c "from importlib.metadata import version; import platform; print(platform.platform()); print('PyYAML='+version('PyYAML')); print('jsonschema='+version('jsonschema'))"
```

## Deterministic Registry Build

Summary-only rebuild:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B '08_Domain_Applications/Math_Mentor/p0_control_plane/registry_builder.py' `
  --repo-root . `
  --expected-head 764d03d7d0a9ad553f4f3868699b06d9de5553ea
```

Materialization command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B '08_Domain_Applications/Math_Mentor/p0_control_plane/registry_builder.py' `
  --repo-root . `
  --expected-head 764d03d7d0a9ad553f4f3868699b06d9de5553ea `
  --write `
  --output-dir '08_Domain_Applications/Math_Mentor'
```

The materialization writes only the three authorized root registries. It does
not mutate any source node or roadmap.

## Complete P0 Tests

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest discover `
  -s '08_Domain_Applications/Math_Mentor/tests/p0_control_plane' `
  -p 'test_*.py' `
  -v
```

Final correction-phase result:

```text
Ran 104 tests in 52.544s
OK
```

This includes:

- all 667 root candidates normalized and JSON-Schema checked;
- deterministic UUID and registry rebuild tests;
- exact source-snapshot behavior from a descendant implementation head;
- aggregate-roadmap rejection;
- staging exclusion and masquerade rejection;
- non-empty model-writable identity resolution forgery rejection;
- authorization payload-gate forgery, scope, effect, replay, expiry, secret,
  post-gate, and fixture-in-production rejection, while explicitly proving
  that the replay snapshot is read-only and does not consume or persist a
  nonce;
- canonical eight-tier authority precedence and the separation of
  authenticated Human override from ordinary task details;
- factory-issued request, grant, decision, and admission-evidence identity,
  full-field fingerprint integrity, sealed decision immutability, immutable
  result mappings, and unrelated-resource reuse rejection;
- direct construction, copying, serialization reentry, duck typing,
  post-issuance mutation, behavioral built-in subclasses, Unicode surrogates,
  caller-object replacement after validation, and test-fixture-in-production
  red-team rejection;
- a fixed, case-insensitive protected-path floor covering `.env` variants,
  SSH/private-key material, credential filenames and directories, Git/cloud
  credential stores, control characters, Windows ADS, and non-normalized path
  forms without reading any file contents;
- legacy R5 non-promotion and bridge-admission-not-implemented checks.

## Consolidated Validator

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B '08_Domain_Applications/Math_Mentor/p0_control_plane/validate.py' `
  --repo-root . `
  --expected-source-head 764d03d7d0a9ad553f4f3868699b06d9de5553ea
```

Main-agent result:

```json
{"byte_identical_repeatability":true,"committed_blob_bytes_match_generated":true,"committed_materialization_head":"eebd2688f099d1be035576793a70d135086d4fa6","materialized_outputs_match":true,"output_sha256":{"ALIAS_CONFLICT_REGISTRY.json":"03a402f97501f85cc2eaced46d651234f57ddbce53533af92b0f82810dfd7c21","CANONICAL_NODE_CROSSWALK.json":"3be77ebc9bc7a826607d28af7def16477aa01d32ab67ba5117d8d411d49697d1","ROOT_CORPUS_REGISTRY.json":"cb04084040aa00dc0dd80b7bfb39215cbf96a7e50358038dc85a24b45dbc49ac"},"quantitative":{"candidate_edges_unapproved":420,"consumer_allowed":0,"explicit_alias_conflicts":53,"fullwidth_alias_diagnostics":7,"roadmap_entries":770,"root_candidates_parsed":667,"staging_assets_excluded":229,"staging_basename_shadows":195,"staging_identity_overlap":180,"staging_yaml_parse_fail":15,"staging_yaml_parse_pass":213,"tracked_assets":1014,"unclaimed_source_files":194},"repeat_builds":2,"runtime_activation_performed":false,"source_head":"764d03d7d0a9ad553f4f3868699b06d9de5553ea","status":"passed","worktree_json_content_matches_generated":true,"worktree_raw_bytes_used_for_commit_proof":false}
```

The validator makes two different claims deliberately. Canonical generated
bytes from two independent builds are identical and equal the immutable Git
blob bytes at the corrected implementation head. The Windows worktree files
are parsed and canonicalized as JSON before comparison, so CRLF conversion is
allowed but any JSON content drift fails. Raw worktree bytes are not used as
proof of the committed materialization.

## Explicit Format, Schema, Scope, And Hygiene Checks

The correction checkpoint records the following final static checks:

```text
JSON parse: passed
YAML parse: passed
JSON Schema validation: passed
generated payload-hash validation: passed
git diff --check: passed
source-to-implementation paths matching the Human allowlist: 45/45
source-to-final-candidate paths matching the Human allowlist: 46/46
high-confidence credential-pattern scan: 0 findings
bytecode cache directories remaining after cleanup: 0
```

The final report commit is necessarily self-referential as
`report_commit_itself`; its exact SHA is supplied by the external handoff after
that commit exists. The one additional final-candidate path is the new
`CHECKPOINTS/correction-validated.yml`; every other report update is on a path
already counted in the 45-path implementation diff.

## Stage 0 Drift Measurement

The original inventory recorded Windows worktree byte counts. The following
uses the same 1,014 recorded paths and therefore reproduces the reviewed
10,989,541 to 11,203,054 comparison:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
@'
from pathlib import Path
import json

manifest_path = Path(
    '.ai/PROGRAM_RUNS/math-mentor-knowledge-completion-stage-0-inventory-0001/'
    'inventory/corpus_manifest.json'
)
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
old_bytes = sum(record['bytes'] for record in manifest['files'])
current_bytes = sum(Path(record['path']).stat().st_size for record in manifest['files'])
changed = [
    record['path'] for record in manifest['files']
    if Path(record['path']).stat().st_size != record['bytes']
]
print(old_bytes, current_bytes, current_bytes - old_bytes, len(changed))
'@ | python -B -
```

Result:

```text
10989541 11203054 213513 28
```

Canonical Git blob-byte totals were also measured with
`git ls-tree -r -l -z <head> -- 08_Domain_Applications/Math_Mentor`:

```text
cefd164472ecbb7095c1aa2c243c34fbec5b51f4  1014  10819458
764d03d7d0a9ad553f4f3868699b06d9de5553ea  1014  11030554
```

The difference between worktree and blob totals is Git text conversion, not a
hidden asset-count change.

Exact changed paths:

```powershell
git -c core.quotepath=false diff --name-only `
  cefd164472ecbb7095c1aa2c243c34fbec5b51f4 `
  764d03d7d0a9ad553f4f3868699b06d9de5553ea `
  -- '08_Domain_Applications/Math_Mentor'
```

## Staging Diagnostic Reproduction

The staging scan is read-only and uses the frozen Git snapshot: select tracked
assets below `Pure_Math_Intuition_DB/_Staging_*`, parse each YAML document,
compare exact basenames, compare strict IDs, and compare raw SHA-256 values
with the root candidate set.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B '08_Domain_Applications/Math_Mentor/p0_control_plane/staging_diagnostics.py' `
  --repo-root . `
  --expected-source-head 764d03d7d0a9ad553f4f3868699b06d9de5553ea
```

The exact result is asserted by `test_staging_diagnostics.py` and the
consolidated validator.

Result:

```json
{
  "staging_tracked_assets": 229,
  "yaml_files": 228,
  "python_files": 1,
  "yaml_parse_pass": 213,
  "yaml_parse_fail": 15,
  "parsed_without_top_level_id": 7,
  "basename_shadows": 195,
  "strict_identity_overlap": 180,
  "raw_content_identical": 0,
  "identity_resolution_from_staging": 0
}
```

## Method-Sensitive Alias Finding

The frozen review counted only ASCII `(n_*)` tags and produced 473 explicit
source claims and 420 consistent candidate edges. Seven current E4 nodes use
fullwidth `（n_*）` punctuation. P0 preserves both facts:

- the frozen 473/420 figures are reproduced exactly;
- the seven fullwidth values are recorded as exact diagnostic evidence;
- no normalization, edge, Human approval, or consumer permission is inferred.

This is a parser-method delta, not a claim that the seven concepts are
semantically identical to roadmap entries.

## Limitations

- Structural parse and schema validation are not mathematical review.
- The UUID materialization is a bootstrap because no accepted prior crosswalk
  existed at the base. A future path/alias migration needs a reviewed prior-row
  preservation input.
- Non-empty identity resolution overlays are intentionally rejected until an
  external Human-authenticated adapter exists.
- The authorization verifier can reject a nonce already present in a
  host-supplied read-only snapshot. It does not atomically consume a successful
  nonce, persist replay state, or provide cross-process replay protection.
- Factory-issued and fingerprint-intact objects provide a static in-process
  trust boundary only. Verifier and admission code consume checked snapshots
  after validation so later caller-owned field replacement cannot affect the
  decision. Production authentication, evidence ingress, durable replay state,
  and trusted decision rehydration remain unimplemented.
- Production authentication transport, trusted decision rehydration,
  persistence, runtime, Coordinator, state writer, scheduler writer, UI, and
  bridge admission remain unimplemented and inactive.
- No secret, credential, real signing key, or real student identity was read,
  created, committed, or logged.
