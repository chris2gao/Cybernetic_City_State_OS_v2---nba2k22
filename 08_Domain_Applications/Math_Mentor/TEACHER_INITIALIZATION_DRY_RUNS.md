# Math Mentor Teacher Initialization Dry Runs

Status: LRP-01 validation fixtures.

These dry runs are documentation fixtures. They do not activate runtime, production Coordinator execution, external apps, node generation, bridge generation, or learning-history writes.

## Fixture Format

Each fixture records:

- input condition;
- expected file loading order;
- expected `actually_read_files` behavior;
- expected compressed state dump fields;
- expected stop/continue decision;
- must-not-have list.

## Dry Run 1: Empty Context To Teacher Initialization

Input condition:

- new independent model;
- no Math Mentor files in context;
- Human asks for Math Mentor teaching within existing scope.

Expected file loading order:

1. current Human request;
2. `06_Silicon_Index/AI_Bootstrap_Sequence.md`;
3. `3号方案.md`;
4. `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`;
5. `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`;
6. `08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md`;
7. `08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md`.

Expected `actually_read_files` behavior:

- every file above is listed exactly once;
- no full repository directory is listed;
- no full Math Mentor directory is listed.

Expected compressed state dump fields:

- `Target_Node` may be `not_yet_identified`;
- `Mode` may be `pending_target_node`;
- `actually_read_files` is non-empty;
- forbidden actions are explicit.

Expected decision:

- continue to target-node routing if the user supplied a target;
- otherwise ask one target-node clarification question.

Must not have:

- request for Human to upload repository files;
- full-repo ingestion;
- runtime activation.

## Dry Run 2: Known Target Node Request

Input condition:

- user asks: "I want to learn n_15 mapping";
- bootstrap and Coordinator manuals have been read.

Expected file loading order:

1. target-node locator or index if needed;
2. exact target node YAML;
3. immediate prerequisite nodes only if required;
4. matching bridge records only if explicit endpoints or unambiguous legacy content match the target;
5. learned-history state if available.

Expected `actually_read_files` behavior:

- includes bootstrap and Coordinator manuals from prior stage;
- adds target-node file and only required adjacent context;
- records learned-history state as `unavailable` if not found.

Expected compressed state dump fields:

- `Target_Node`;
- `Mode`;
- `Routing_Basis`;
- `Core_Definition`;
- `Sub_Topics`;
- `Bridge_Slots`;
- `Next_Node_Outlook`;
- `Mapping_Status`;
- `Current_Agent_Active`;
- `actually_read_files`.

Expected decision:

- continue to guided teaching when target node is loaded;
- block with exact missing path if target node cannot be resolved.

Must not have:

- loading all node YAML files;
- assuming lower node ID means mastery;
- bridge endpoint invention.

## Dry Run 3: Manual Absent From Current Context But Present In Repository

Input condition:

- `V9.1_认知映射引擎_终极实装蓝图.md` text is absent from current context;
- file exists at `08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md`.

Expected file loading order:

1. Coordinator preflight checks current context;
2. Coordinator loads the file by repository path;
3. Coordinator records the path in `actually_read_files`;
4. Coordinator proceeds.

Expected compressed state dump fields:

- `actually_read_files` includes the operational manual;
- `Mapping_Status` is not claimed until mode and node evidence are known.

Expected decision:

- continue.

Must not have:

- `[FATAL_ERROR: MISSING_PAYLOAD]` solely because the file was not already in current context;
- request for Human upload.

## Dry Run 4: Manual Missing From Repository

Input condition:

- required operational manual is absent from current context;
- repository path cannot be read.

Expected file loading order:

1. check current context;
2. try exact repository path;
3. stop.

Expected `actually_read_files` behavior:

- does not list the missing file as read;
- records the attempted path in the error/report context.

Expected compressed state dump fields:

- no teaching state dump is emitted because the teacher is not initialized.

Expected decision:

- block with exact missing path.

Must not have:

- invented summary of the missing manual;
- teaching continuation;
- request to activate runtime as a workaround.

## Dry Run 5: Learned-History State Unavailable

Input condition:

- target node and prerequisites are loaded;
- persisted learned-history state cannot be found.

Expected file loading order:

1. target node;
2. immediate prerequisites;
3. matching bridges;
4. attempted learned-history path or known state source.

Expected `actually_read_files` behavior:

- includes files actually read;
- marks learned history as `unavailable`, not `learned`.

Expected compressed state dump fields:

- bridge slots use `teaser_only`, `hidden`, or `unavailable` where learned-history requirements are unsatisfied;
- `learned_history_state: unavailable`.

Expected decision:

- continue only with formal teaching content that does not require unverified mastery;
- use prerequisite teaching or Human clarification when mastery is required.

Must not have:

- integer node ordering as proof of mastery;
- classroom pass or graduation claims.

## Dry Run 6: Context-Boundary Reload

Input condition:

- same target-node lesson resumes after context compaction or new window;
- previous `actually_read_files` cannot be trusted.

Expected file loading order:

1. current Human request or handoff;
2. bootstrap minimal set;
3. Coordinator and Teaching Flow Spec;
4. operational manual;
5. target node and matching context.

Expected `actually_read_files` behavior:

- regenerated for the resumed context;
- stale entries are not treated as current unless re-read.

Expected compressed state dump fields:

- `context_boundary_reload: true`;
- updated `actually_read_files`;
- same target node if resolvable.

Expected decision:

- continue after reload if evidence is complete;
- block with exact missing path if evidence cannot be reloaded.

Must not have:

- hidden-memory continuation;
- stale bridge or learned-history claims.

## Dry Run 7: Drift Recovery And New-Window Reset

Input condition:

- teacher starts mixing Mode A everyday metaphor with Mode B canonical teaching, or references a file not in `actually_read_files`.

Expected file loading order:

1. stop the current teaching turn;
2. reload the smallest missing authority file;
3. reload target node if target evidence is stale;
4. emit corrected state dump.

Expected `actually_read_files` behavior:

- includes reloaded authority file;
- identifies previously unsupported reference.

Expected compressed state dump fields:

- `drift_detected: true`;
- corrected `Mode`;
- corrected `Mapping_Status`;
- updated `actually_read_files`.

Expected decision:

- continue after correction if single-lane evidence is restored;
- if drift is irreversible, request new-window reset with a minimal reset payload.

Must not have:

- continuing with mixed, unsupported metaphors;
- claiming semantic or computational validation without evidence;
- starting LRP-02 or later tasks.

