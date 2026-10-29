# Engineering entry and continuation

Task: NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01. Human supplied the full M0-M5 brief on 2026-10-28. Baseline is Draft PR18 HEAD `094f1aa641f93dec2277707ad9dbf5bdb0341247`, not master. Master at entry: `7742568ac677b3c16079887463f05e81cb1191ed`.

## Module recognition

| Module | Existing functionality/source | Evidence maturity | Task relationship |
|---|---|---|---|
| P00 | Root bootstrap, OS entry, domain runs | Existing governance | Use; do not edit core |
| P01 | V2 architecture; external world_data_prototype v24/v25 | Independent engineering candidates | Reference only |
| P02 | src/auto_pipeline_ingest.py, gm_state_io, gm_data_access, database/schema.sql | Historical implementation; external world prototype has further work | Preserve unchanged |
| P03 | source_catalog, memory_field_profile, source_extensions | Partial field/reader certification | Reuse via role-safe boundary |
| P04 | Six gameplay guides, R05 catalogs, R07 40 families/694 references | Research closed; native acceptance independent | Semantic source, targeted lookup |
| P05 | gm_core and web_gm | Existing GM components, not all-team product acceptance | Consume decided requests only |
| P06 | Coach profile, POE, Playbook/Freelance/personal defense research | Partial controls; no independent personality | Native expansion and metadata |
| P07 | Player fields, tendencies/badges/training research | Partial native fields; personality separate | Native edit vs role rights separated |
| P08 | Contract/trade/staff/scouting/draft research | Specific trade/Goal live examples; other gaps | GM/Coach execution expansion |
| P09 | rea_native_control facade/registry/transport/runtime, prior native_action PE tools | 62 actions, 38 bindings/layouts; exact live examples only | Reuse primary engine |
| P10 | PR18 183 requirements, 14 groups, 50 explicit crosswalks; batch architecture V2 | Planning, no batch implementation | Main new service and aggregation |
| P11 | web_gm knowledge, historical draft and tactics | Existing reference assets | Preserve and consult |
| P12 | Existing task/audit registers and run evidence | Historical evidence, no blanket completion | Record progress and exact gaps |

External data sources: world implementation `17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`, review fixes `a3927fb150a213201e404cca043ced4f57409bd1`. Do not reconstruct or integrate their databases in this task.

## Four-layer sources loaded

Project index and sync contract; module registry including external assets. Full REA window handoff (paged), README, discovery, role mechanism guide, validation report; registry/bindings/read/live catalogs; Facade, contracts, registry, readers, code generator and runtime entry/handlers. Gameplay README, PROGRESS and source registry navigation; six requested guides by section and relevant mechanism tables; eight requested research catalogs by structure and scoped examples, to be expanded per implemented domain. Planning reuse index, role inventory, three machine catalogs and input-value contract; architecture V2. No claim of manually rereading every historical catalog record.

Important precedence: PROGRESS latest says DEV29 research closed; historical README/catalog pending language does not reopen research. Private beliefs and role requests are not Native setters. Daily training intensity raw0..7 is distinct from old home/away intensity0..5. Ten Coach projection fields are not complete coaching. Uint8 encoding is not a UI value range.

## Reuse and maturity

Coach defense Apply, RunPlayTendency90→55, explicit unequal-salary player exchange and existing Goal setter have specific historical live evidence. Prior consumed cases must never be replayed. Trade directly uses AddPlayer/AddPick→context→Process, not salary matching or TeamID writes. Scouting goal setting, Append rejection and consuming a trip are separate operations. Multi-asset trade, training and draft retain independent untested status. Signing/editor/staff/rotation/Playbook need actual ABI/object/commit recovery.

## Implementation order and full completion requirements

1. M0: load every requirement, distinguish permission from technical maturity, provide meaningful parameters/enums and role-safe data boundary.
2. M1: immutable decided batches; cross-role agreement, duplicate/asset/field conflict handling, dependency ordering; durable pre-dispatch journaling and fail-closed unknown outcomes, no automatic replay.
3. M2-M4: reuse proven control pathways and continue local PE/caller recovery for all missing GM/Coach/Player areas. Do not call absent functions through placeholders.
4. M5: per-requirement disposition and additional discoveries, executable bindings, parameter meaning, evidence and precise technical gaps; same-PR index synchronization.
5. Complete candidate verification, separate review, Draft engineering PR. No master integration.

Live state-changing tests require a consolidated scenario plan and new Human approval. None executed. The full task remains active until M0-M5 are satisfied; a service skeleton or catalog alone is not completion.

## Environment facts

Separate clone `native-execution`, independent task branch. Initial checkout encountered Windows long paths; repaired in this newly created clone by enabling local core.longpaths and restoring its checkout; clean baseline verified. Existing data worktrees left untouched.

REA CLI6.8.0 is installed; no REA MCP tools are exposed in this active session. Doctor reports aligned Codex registration but no configured native engine path. The handoff's Ghidra installation and target executable exist; absence of configuration is not absence of installation. Never rerun the exhausted whole-game Ghidra route; reuse local PE/Capstone and CLI where supported. No configuration edited, game attached or old batch relaunched.
