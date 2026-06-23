# Architecture

## Root Structure

- `01_Research_Reports/`: research reports and source material.
- `02_Protocols/`: system protocols and operating rules.
- `03_Daily_Execution/`: daily execution artifacts and applied task outputs.
- `04_Parliament/`: issues, proposals, verdicts, archived debates, and resolved records.
- `05_Carbon_Index/`: human-facing index area.
- `06_Silicon_Index/`: AI-facing index area, scripts, skills, personas, sandbox tests, and factory pipeline code.
- `07_Compiler/`: compiler-related support code.
- `07_Execution_Plans/`: task execution plans and closed-loop records.
- `07_Silicon_Private_Zones/`: private work zones and passports for named AI agents.
- `08_Domain_Applications/`: domain-specific systems. The active domain is `Math_Mentor`.
- `Math_Nodes_V9/`: V9 math node material, currently including `Level_4`.
- `short_term_tasks/`: short-term outsourcing task files and task templates.

## Math Mentor Structure

- `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/`: main YAML knowledge-node database.
- `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/_Staging_Level*/`: staging areas for generated node batches.
- `08_Domain_Applications/Math_Mentor/知识图谱_节点映射索引.md`: node mapping index.
- `08_Domain_Applications/Math_Mentor/学习期prompt/`: teaching-period prompts and LLM/math architecture references.
- `08_Domain_Applications/Math_Mentor/复习巩固期prompt/`: review-period prompts.
- `08_Domain_Applications/Math_Mentor/Universal_Layer_Execution_Protocol.md`: layer generation, validation, and merge protocol.
- `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`: coordinator prompt for teaching execution.

## Main Responsibilities

- Root OS: provide routing, protocol storage, review history, and AI/human operating surfaces.
- `06_Silicon_Index/factory_pipeline/`: run sandbox and bulk validation for generated math YAML nodes.
- `Math_Mentor`: maintain the math knowledge graph, teaching prompts, spaced review artifacts, generated node batches, and outsourcing instructions.
- `short_term_tasks`: keep concrete outsourcing task specifications and templates.

## Known Unclear Areas

- `README.md` instructs AI agents to read `06_Silicon_Index/AI_Bootstrap_Sequence.md`, but that file is not present in the current checkout.
- `INSTANCE_CONFIG.md` still contains placeholder values.
- Some staging directories are committed alongside merged generated nodes; future agents should verify whether staging folders are intended as permanent audit artifacts or temporary build output.
- The local branch `subagent-Calculator-Developer-engine-a-fable-worker-3c74b6f0` is tied to a separate worktree path and may not be part of the normal publish path.
