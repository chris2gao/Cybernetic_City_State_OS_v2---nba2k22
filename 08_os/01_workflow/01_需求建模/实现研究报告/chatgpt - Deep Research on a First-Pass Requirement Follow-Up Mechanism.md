# Deep Research on a First-Pass Requirement Follow-Up Mechanism

## Bottom line

**Read:** `github/spec-kit`’s `/clarify` is *logically separable* as a prompt-and-file-update workflow, but it is **not** a clean drop-in standalone component. The current command template expects a Spec Kit project layout, feature-path resolution via `check-prerequisites`, an active feature pointer in `.specify/feature.json`, optional constitution and extension-hook files, and a specific spec/checklist mutation workflow. In other words: the questioning logic is portable, but the command is materially coupled to Spec Kit’s file conventions and command runtime. citeturn7view0turn8view0turn37view0turn37view1turn12view2

**Inference:** For your v1, the most practical way to “borrow” `/clarify` is not to transplant the whole command unchanged. It is to extract its **coverage scan + one-question-at-a-time loop + write-back discipline**, while replacing Spec Kit-specific path resolution, file-section insertion rules, hook handling, and command placeholders with your own runtime.

**Read:** For “stop when the schema is filled under constraints,” the most implementable answer is **validator-driven completion**: use a canonical schema for the target requirement model, validate each round, and mechanically derive the next question from the remaining validation errors. JSON Schema gives you structural and conditional constraints; `python-jsonschema` gives you machine-readable error trees; Pydantic gives you typed parsing plus custom field/model validators for cross-field checks. Constraint solvers are available, but they are only worth the extra modeling burden when you truly have combinatorial or satisfiability-style constraints. citeturn20search2turn19search3turn19search1turn19search4turn18search6turn18search18turn20search1turn20search12

**Read:** The old slot-filling systems were not naive. Rasa, Alexa, and Dialogflow all solved “when is the dialog complete?” with explicit required-slot state, validation, reprompting, dynamic slot requirements, and a separate notion of completion before task fulfillment. Those mechanics still hold up. What has aged poorly is the assumption that the ontology is fixed and that brittle intent/entity pipelines are good enough for open-ended discovery. citeturn25view1turn25view0turn24view2turn24view5turn24view7turn24view3turn24view6turn26search15turn26search2

**Read:** ReqElicitBench / ReqElicitGym is light on *local* infrastructure and heavy on *remote* LLM usage. The repo requires Python 3.8+, a small dependency set, and an OpenAI-compatible chat-completions endpoint; the expensive part is that a full run invokes an interviewer model plus an oracle user plus a judge across 101 scenarios. The scoring dimensions can be borrowed without running the full benchmark, but only if you also preserve the benchmark’s core abstraction: a gold set of implicit requirements per scenario and turn-level judgments of whether a question elicited one of them. citeturn27view0turn28view0turn29view1turn29view3turn31view0turn32view3turn32view1

## What `/clarify` actually is in Spec Kit

**Read:** The current `templates/commands/clarify.md` describes `/clarify` as a command that “identify[ies] underspecified areas in the current feature spec by asking up to 5 highly targeted clarification questions and encoding answers back into the spec.” The workflow is concrete, not abstract: it runs a prerequisite script to locate the active feature/spec, optionally loads a constitution file, scans the current spec against a taxonomy of ambiguities, internally prioritizes candidate questions, asks **exactly one question at a time**, updates the spec after each accepted answer, validates the written result, and ends with a completion report. citeturn7view0turn8view0

**Read:** The ambiguity scan taxonomy is broad and implementation-relevant. It checks functional scope, domain/data model, interaction and UX flow, non-functional qualities, integrations, edge cases, constraints/tradeoffs, terminology, completion signals, and placeholder/vagueness markers. It is therefore not “just a few follow-up prompts”; it is a structured coverage pass over a requirements artifact. citeturn8view0

**Read:** `/clarify` is wired to the Spec Kit runtime in several specific ways. First, it expects to run the repo script `scripts/bash/check-prerequisites.sh --json --paths-only` or the PowerShell/Python equivalents, then parse fields such as `FEATURE_DIR` and `FEATURE_SPEC`. Second, the active feature is tracked by `.specify/feature.json` or `SPECIFY_FEATURE_DIRECTORY`, not merely by free text in the chat. Third, it optionally reads `/memory/constitution.md` and optional extension hooks from `.specify/extensions.yml`. Fourth, it can revalidate and update `FEATURE_DIR/checklists/requirements.md` after clarifications. citeturn7view0turn8view0turn37view1turn12view2

**Read:** The command also assumes a particular *shape* of spec. The default `spec-template.md` contains sections such as “User Scenarios & Testing,” “Requirements,” “Functional Requirements,” “Key Entities,” “Success Criteria,” and “Assumptions,” and even includes `[NEEDS CLARIFICATION: ...]` markers as first-class placeholders. `/clarify` mutates this kind of document in place and has instructions about where to insert `## Clarifications`, where to update functional requirements, data model bullets, measurable outcomes, and edge-case sections. citeturn9view0turn8view0

**Inference:** If your downstream consumer wants a structured requirement model rather than a Markdown spec, the questioning logic ports well, but the *write-back logic* does not. You will want to keep the taxonomy and prioritization, but swap the mutation target from Markdown headings to a canonical JSON object or database record.

**Read:** The command is *less* coupled to agent context files than some users assume. In a July 2026 maintainers’ discussion, a Spec Kit maintainer explained that agent context files like `AGENTS.md` and `CLAUDE.md` are now formally disconnected from the Spec Kit process itself, and that the constitution is read on demand by commands rather than ambiently injected. That makes extraction a bit easier: `/clarify` does **not** fundamentally depend on ambient agent files, but it *does* depend on the command template explicitly instructing the agent to read certain files at certain steps. citeturn16view0

**Read:** The docs also make clear that `/speckit.clarify` is intended as a repeatable quality gate before planning, and can be run multiple times with different focus areas. The current reference says only `/speckit.specify` is strictly required before `/speckit.plan`, while `clarify`, `checklist`, and `analyze` are optional quality gates; the quickstart’s “full path” places `/speckit.clarify` between `specify` and `plan`. citeturn37view0turn37view1

### Actual evidence of people trying to reuse or stretch `/clarify`

**Read:** I did **not** find a clean public write-up titled “we extracted `/clarify` from Spec Kit and ran it standalone.” What I did find was a cluster of users trying to use `/clarify` **outside its clean happy path**: as a mid-stream refinement tool, in alternative agents, or by passing focused guidance to it. Several discussion threads show users using `/speckit.clarify` to refine existing specs or add changes after the original generation pass, and at least one user explicitly said `/speckit.specify` did not work for this edit flow but `/speckit.clarify` did. citeturn14view1turn17view2

**Read:** A user reported that using `/prompts:speckit.clarify` with Codex CLI resulted in “recommended actions with no clarifying question,” even when the user explicitly tried to force a focused questioning pass. Another user reported that using `/speckit.clarify.md` in Kilocode caused the model to start making code changes after updating `spec.md`, before planning or task generation. Those are not extraction guides, but they are real-world evidence that `/clarify` behaves differently across agent runtimes and that the boundary between “clarify requirements” and “take action” is not universally well enforced. citeturn15view0turn15view1

**Read:** There are also concrete runtime failures tied to `/clarify`’s dependencies. One issue reported that after the fifth clarification answer, the agent tried to run a prerequisite check in `/root` instead of the actual project root. Another user hit shell-script resolution failures because `.specify/scripts/bash/common.sh` could not be found. Another issue documented that `check-prerequisites.sh --paths-only` contradicted its own help text by still running branch validation and failing on non-feature branches. Yet another bug showed that `--paths-only` used to rewrite `.specify/feature.json`, dirtying the working tree, and the current script comments now note a `--no-persist` workaround for precisely that side effect. citeturn14view5turn15view4turn15view5turn12view3

**Read:** Packaging and integration have also broken in practice. In late 2025, users reported release ZIPs and generated Spec Kit prompt files being empty, which made all commands behave incorrectly. Separately, a feature request for Claude integration noted ambiguity in the current response schema for `/clarify`: free-text replies like “recommended” or “the second one” can be misrouted because the question UI is encoded in prose/Markdown rather than in a native structured question tool. citeturn15view3turn14view4

**Read:** There is evidence that the current `/clarify` template has already incorporated fixes driven by these practical pain points. For example, an issue asked for `requirements.md` to be updated automatically after clarify because the spec changed but the checklist did not; the current template now has an explicit step to re-evaluate and update `FEATURE_DIR/checklists/requirements.md` after writing the spec. citeturn15view2turn8view0

### Practical answer to your first question

**Inference:** Yes, `/clarify` can be peeled away **conceptually**. The reusable core is:

1. load current requirement artifact,  
2. score ambiguity by a fixed taxonomy,  
3. prioritize unresolved items,  
4. ask one constrained question at a time,  
5. integrate accepted answers into the artifact,  
6. stop after resolution, user stop, or quota.

That core is genuinely valuable and not Spec Kit-specific. It is directly visible in the template. citeturn8view0

**Inference:** No, `/clarify` is not a “copy this one file and you are done” module. The parts you must replace are: feature discovery, file layout assumptions, Markdown section mutation rules, optional constitution/hook integration, command placeholders like `__SPECKIT_COMMAND_PLAN__`, and the checklist update path. If you omit those replacements, you inherit exactly the kinds of failures users have already reported. citeturn7view0turn8view0turn14view5turn15view4turn15view5turn15view3

## A mechanical stop condition for filling a schema under constraints

**Read:** JSON Schema already gives you a practical vocabulary for “what is still missing or invalid.” At minimum, `required` marks absent fields, `dependentRequired` expresses presence dependencies, and `if` / `then` / `else` expresses conditional requirements. Draft 2020-12 also includes a recommended output schema, and the Python `jsonschema` library exposes `ValidationError`, `iter_errors`, and `ErrorTree` so you can inspect all failures programmatically rather than relying on a single pass/fail bit. citeturn20search2turn19search3turn19search1turn19search4

**Read:** Pydantic gives you the same idea in typed-Python form: parse into a model, get a structured `ValidationError` when parsing or validation fails, and use field or model validators where the constraint is not easily expressible as a basic schema keyword. Pydantic’s `TypeAdapter` also lets you validate non-`BaseModel` Python types without inventing wrapper models. citeturn18search6turn18search18turn19search5turn18search2

**Read:** If your LLM endpoint supports constrained structured output, you can reduce the “garbage JSON” problem before validation even starts. OpenAI’s Structured Outputs documentation states that the model can be constrained to adhere to a supplied JSON Schema, which avoids omitted required keys or invalid enum values at generation time. citeturn18search3turn18search7

**Inference:** For a v1 requirement-follow-up system, the most robust architecture is:

- a **canonical requirement model** in JSON Schema or Pydantic,  
- a **validator** that returns a full error set,  
- a **question planner** that converts the highest-priority remaining error into one user-facing question, and  
- a **stop rule** of “no blocking validation errors remain.”

This is mechanically decidable, debuggable, and easy to instrument.

### A practical completion ladder

**Inference:** In implementation terms, I would split “done” into three machine states:

**Structural completion.** All required fields exist, enum/type checks pass, and no conditional requirements remain unmet. This is the part JSON Schema handles best. citeturn20search2turn19search3turn19search1

**Semantic completion.** Cross-field rules pass, such as “if deployment is on-prem, data residency cannot be unknown,” or “if authentication is SSO-only, local password-reset flow must be absent.” This is where Pydantic field/model validators are usually the easiest implementation. citeturn18search18turn18search6

**Policy completion.** Your product-specific question policy says there are no more *blocking* unknowns. This layer is usually not in pure schema form; it is an application rule such as “launch-blocking fields must not be `unknown` or `assumed`,” while lower-priority fields may remain deferred. This part is your own control logic.

**Inference:** Stopping on pure schema validity is often not enough, because many requirement systems need a tri-state such as `{known, unknown, deferred}` rather than just “field present.” The practical trick is to encode uncertainty explicitly. For example, instead of omitting `sla_target`, allow a discriminated structure like `{status: "unknown" | "deferred" | "specified", value: ...}` and then make your stop rule depend on which statuses are permitted for v1. That gives you machine-readable “we still need to ask” logic without pretending every field is binary.

### How to derive the next question mechanically

**Inference:** The simplest deterministic planner is:

1. validate the current requirement object;  
2. collect all errors;  
3. normalize them into “slots” or “constraints” such as `missing.auth.method`, `invalid.retention.period`, `dependent.billing_address`;  
4. assign each one a priority;  
5. ask exactly one question for the top-ranked unresolved item;  
6. merge the answer and validate again.

With `python-jsonschema`, `iter_errors` and `ErrorTree` are enough to implement steps 2–3; with Pydantic, `ValidationError.errors()` serves the same purpose. citeturn19search1turn19search4turn18search6

**Inference:** A good v1 prioritization order is usually:

- missing required fields that block downstream codegen,  
- field-level invalid values,  
- unmet dependencies,  
- cross-field contradictions,  
- nice-to-have or deferred metadata.

That order is not theoretically pure, but it is highly implementable.

### When to bring in a constraint solver

**Read:** OR-Tools CP-SAT is a full constraint programming solver, but its core constraints are integer-based and it introduces a real modeling layer. Z3 is an SMT solver for symbolic logic and is far more expressive than a normal schema validator. citeturn20search1turn20search12turn20search15

**Inference:** For your use case, solvers are usually **overkill for v1** unless you have one of these specific patterns:

- multiple interdependent numeric limits,  
- alternative configuration bundles where only some combinations are legal,  
- scheduling/allocation-style constraints,  
- or “find me a consistent assignment over partially specified variables.”

If the real problem is just “what else do we need to ask?”, JSON Schema + Pydantic is cheaper to implement and easier to explain.

### The implementability verdict

**Inference:** If I map the options to “what would I build first,” the order is:

**First:** JSON Schema or Pydantic as the single source of truth.  
**Second:** validator-driven next-question generation.  
**Third:** optional constrained decoding at model output if your provider supports it.  
**Last:** solvers, only for genuinely combinatorial constraints.

That sequence is more boring than elegant, but it is the best fit for a first productionable version.

## What the classic slot-filling era still teaches

**Read:** The classic frame-based view is simple: the system keeps a frame of required information, fills slots over multiple turns, and proceeds when the frame is complete. Jurafsky’s current chapter on frame-based dialogue systems still describes the system’s goal as filling the frame slots needed to perform the task. citeturn26search2

**Read:** Rasa operationalized this as forms with `required_slots`. A form automatically deactivates once all required slots are filled, and Rasa exposes explicit unhappy-path behavior when the user does not provide the requested slot, interrupts, or changes intent. Rasa also allows dynamic `required_slots`, where later required fields depend on earlier answers, and now supports real-time slot validation rules in the domain file outside form logic. citeturn25view1turn25view0turn24view2

**Read:** Alexa solved the same problem with a dialog model and a built-in dialog state machine. Required slots must be filled with valid values; optionally, slots or the full intent can require confirmation before proceeding; the runtime exposes dialog states `STARTED`, `IN_PROGRESS`, and `COMPLETED`. Alexa also added slot validation rules with reprompts for invalid values. citeturn24view5turn24view7turn23search3turn23search4

**Read:** Dialogflow ES and CX use required parameters / form parameters. In ES, `allRequiredParamsPresent` is the explicit completion flag. In CX, required parameters “must be filled before form filling concludes,” are collected in a defined order, and support reprompt handlers after failed attempts. Session/context propagation can auto-fill later parameters from previously collected values. citeturn24view6turn24view3turn24view4

### What still survives into the LLM era

**Inference:** Four things from that era remain completely valid:

**Explicit required-vs-optional modeling.** This is still the backbone of “when are we done?” Rasa `required_slots`, Alexa required slots, and Dialogflow required parameters are the same underlying idea. citeturn25view1turn24view5turn24view3

**Validation is separate from extraction.** Rasa validation actions, Alexa slot validation, and Dialogflow reprompt logic all reflect the same durable insight: “I extracted something” is not the same as “I have an acceptable value.” citeturn24view1turn23search3turn24view3

**Dynamic requirement sets.** Rasa’s dynamic `required_slots` and Alexa’s runtime dialog control both show that the list of “still needed” fields can depend on earlier answers. That is exactly what a requirement-follow-up mechanism needs. citeturn25view0turn24view7

**A separate completion state before fulfillment.** Alexa’s `COMPLETED` and Dialogflow’s `allRequiredParamsPresent` are important: the system should have an internal “elicitation complete” state before it starts downstream planning or execution. citeturn24view7turn24view6

### What has aged badly

**Read:** The main structural weakness of classical slot filling is ontology rigidity. Research on slot discovery in task-oriented conversation explicitly notes that existing systems rely on predefined slot ontologies and candidate values, and that these assumptions are hard to meet in practical settings with new requirements and evolving scenarios. citeturn26search15turn26search0

**Inference:** In your setting, that means the old systems are strongest when the requirement space is **closed and known in advance**: booking, ordering, support workflows, compliance intake, configuration forms. They are weakest when the user is still discovering the problem, when latent tradeoffs matter, or when new dimensions emerge during the interview.

**Inference:** What LLMs have mostly obsoleted is not the *state machine*, but the brittle front-end around it: hand-authored intent classification, static synonym tables, and overfit entity extractors. LLMs are better at mapping natural phrasing to candidate fields and at proposing unseen follow-ups. But the old state concepts—required slots, validation, reprompt, confirmation, completion—still deserve to be your control plane.

### My judgment on whether this old direction is actually useful for you

**Inference:** This direction is **not** obsolete. It is valuable if you reinterpret “slot filling” as **schema-backed dialog state management** rather than as “old-school NLU with regexes and intent classifiers.”

For your product, the enduring lessons are:

- maintain an explicit state of filled / missing / deferred fields,  
- ask one targeted question against that state,  
- validate every answer against a schema,  
- allow the required set to change dynamically,  
- and separate “requirements complete” from whatever downstream program consumes them.

What you should *not* inherit is the assumption that the field ontology is always complete on day one.

## What ReqElicitBench and ReqElicitGym actually require

**Read:** The repository positions itself as the official implementation of the paper and contains four main pieces: a dataset, an oracle user, a task evaluator, and scripts that produce conversations and metrics. The README says the dataset has **101 website requirements-elicitation scenarios spanning 10 application types**; the paper says the environment evaluates interview competence by interacting with an evaluation dataset, an oracle user, and a task evaluator. citeturn27view0turn31view0

**Read:** The paper also provides useful validation evidence for whether the environment is worth trusting at all. It reports that the oracle user and task evaluator were validated on **33 real interview dialogues comprising 555 turns**, with Cohen’s kappa of **0.73** for the oracle user against real users and **0.72** for the task evaluator against expert judgments. citeturn31view0

**Read:** Local infrastructure is modest. The repo requires Python 3.8+ and a small dependency list: `gymnasium`, `numpy`, `pyyaml`, `openai`, `together`, `google-genai`, `boto3`, `pyarrow`, and `fastparquet`. There is no sign of local training code or GPU-hungry deep-learning frameworks in the published requirements or quickstart. citeturn27view0turn28view0

**Inference:** So the bottleneck is not local compute. It is external-model access and API cost.

### Service dependencies and runtime gotchas

**Read:** The README says you need an **OpenAI-compatible chat-completions API endpoint**, configured via `OPENAI_API_KEY` and optionally `OPENAI_BASE_URL`, with optional separate credentials for the judge and oracle user. The runner script defaults the benchmark to an interviewer model and a separate “gym model” used by judge and oracle user, and configures judge/user temperatures, timeouts, result directories, and a `max_steps=20` turn budget. citeturn27view0turn29view1turn29view3

**Read:** A practically important detail that is easy to miss: while the README presents the setup generically, the published `run_reqelicitgym.py` currently defaults `OPENAI_BASE_URL` to `https://api.chatanywhere.tech/v1` if not otherwise provided. That is a concrete operational dependency/assumption in the script, not just a documentation example. citeturn29view3

**Read:** Another non-obvious mismatch: the paper says the oracle user is played by **GPT-5.1** in the validated environment description, while the repo README and runner now default the shared gym model for judge+user to **`gpt-5.2`**. citeturn31view0turn27view0turn29view3

**Read:** The repo also has **no license file** in the snapshot published on GitHub, and as of my browse time the repository showed **0 GitHub issues**. The absence of public issues means I did not find a bug trail of “this benchmark won’t run,” but it also means there is very little public troubleshooting history to lean on. citeturn27view0

### What data and outputs look like

**Read:** Each task in `ReqElicitGym/data/test.json` includes a system name, an application type, an underspecified `initial_requirements` string, a list of hidden `Implicit Requirements` labeled by aspect (`Interaction`, `Content`, `Style`), and a `URL` field pointing to a complete user-story list/reference artifact. The environment saves both aggregate metrics and full conversation traces. citeturn27view0

**Read:** On the metric side, the paper defines:
- **IRE** as the ratio of elicited implicit requirements to the scenario’s gold implicit-requirement set,
- **ESR** as the fraction of turns under a strategy such as `clarify` or `probe` that successfully elicit at least one implicit requirement,
- **TKQR** as a turn-discounted measure that rewards asking key questions earlier. citeturn32view3turn32view1

**Read:** The README additionally advertises **ORA** in output files, but in the parts of the paper I examined I found formal definitions for IRE, ESR, and TKQR—not ORA. I also did not surface an ORA definition from the code snippets I could access through GitHub’s line-limited web rendering. citeturn27view0turn31view0turn32view3turn32view1

**Inference:** Treat ORA as a repo-level metric you should inspect in code before adopting. At the moment, I would not reuse ORA blindly, because the surfaced paper evidence is much clearer for IRE/ESR/TKQR than for ORA.

### Can you borrow only the scoring dimensions?

**Read:** The answer is yes in principle, because the core metrics are defined over two things: a scenario-level set of gold implicit requirements and a turn-by-turn determination of whether a question elicited one of them, plus turn strategy labels like `clarify` and `probe`. The benchmark’s task evaluator does that automatically with an LLM-as-a-judge pipeline, but the *metric definitions themselves* do not require the full interactive environment. citeturn32view3turn32view1

**Inference:** The minimal subset you can borrow is:

- **IRE** if you have your own gold missing-requirement set,  
- **ESR** if you can label each question as `clarify` / `probe` / `finish` and determine whether it elicited a gold item,  
- **TKQR** if you can track *when* the hits happened turn by turn.

You do **not** need the benchmark’s oracle user for this. You only need your own conversation logs and a credible way to judge which hidden requirements were elicited when.

**Inference:** The moment you drop the benchmark’s oracle user, however, you lose strict comparability to the published setup. So if your goal is internal product evaluation rather than paper-to-paper comparison, borrowing the dimensions is realistic. If your goal is to compare your system against published ReqElicitGym numbers, you need the full environment and its oracle/judge protocol.

## Search log, empty results, truncation, and overlap estimate

### What I searched

For **Spec Kit /clarify**, I searched combinations of:
- `github/spec-kit clarify`
- `site:github.com/github/spec-kit clarify issue`
- `spec-kit standalone clarify`
- `spec-kit detach clarify`
- `prompts speckit.clarify`
- related issues around `check-prerequisites`, `feature.json`, and runtime failures.

For **stop conditions / schema completion**, I searched combinations of:
- `JSON Schema required dependentRequired if then else official`
- `python-jsonschema ErrorTree ValidationError`
- `Pydantic validation errors validators`
- `structured outputs json schema official`
- `Z3Py guide`
- `OR-Tools CP-SAT official`.

For **legacy slot filling**, I searched combinations of:
- `Rasa forms required_slots validate official`
- `Alexa required slots confirmation official`
- `Dialogflow required parameters slot filling official`
- plus a small amount of older slot-filling/DST literature around frame-based dialogue and slot ontology limits.

For **ReqElicitBench / ReqElicitGym**, I searched combinations of:
- `ReqElicitBench ReqElicitGym arXiv GitHub`
- repo README / requirements / runner details,
- metric definitions in the paper,
- and public issue/complaint traces.

### What returned empty or effectively empty

I did **not** find:
- a clean public write-up of someone successfully extracting `/clarify` from Spec Kit as a standalone reusable component;
- a directly surfaced public complaint trail specifically about ReqElicitBench being impossible to run;
- or a clearly surfaced definition of **ORA** in the portions of the paper and code that were accessible through GitHub/arXiv web rendering.

Searches around “standalone/detach clarify” were especially noisy and often returned repo docs, unrelated dictionary pages, or broad preset discussions rather than real extraction reports.

### Where results were truncated or awkward

GitHub code pages were the biggest friction point. Several long files rendered with partial line access, `Uh oh!` placeholders, or snippet-only search results, so I had to rely on repeated `find`/`open` calls around specific anchors instead of reading full raw files cleanly. The arXiv HTML paper was readable for metric definitions and environment description, but not every repo-specific metric surfaced equally clearly there.

### What I found that felt genuinely new

The most **non-obvious** findings were:

- `/clarify` now revalidates `checklists/requirements.md`, which looks like a concrete response to a user-reported sync problem between clarified specs and requirements checklists. citeturn15view2turn8view0
- `check-prerequisites --paths-only` had real side-effect and validation bugs around branch checking and `.specify/feature.json` persistence, which matter if you try to reuse `/clarify` outside the happy path. citeturn15view5turn12view3
- The runner for ReqElicitGym defaults `OPENAI_BASE_URL` to a third-party gateway rather than a neutral null/default. citeturn29view3
- The paper and repo are not perfectly aligned today: paper says the oracle used GPT-5.1, repo defaults judge+user to GPT-5.2, and README exposes ORA while the surfaced paper sections clearly define IRE/ESR/TKQR. citeturn31view0turn27view0turn29view3

### What was obvious and others will likely also find

The most **obvious** findings were:

- `/clarify` asks up to five questions and edits the spec in place. citeturn7view0turn37view0
- JSON Schema and Pydantic can mechanically tell you what is missing or invalid. citeturn20search2turn19search1turn18search6
- Rasa/Alexa/Dialogflow all have explicit notions of required slots/parameters and completion. citeturn25view1turn24view7turn24view6
- ReqElicitGym has 101 scenarios and uses an oracle user plus judge. citeturn27view0turn31view0

### Final synthesis

**Inference:** If your team already picked the three components and only needs implementation guidance, the strongest reusable pattern across all four questions is this:

- keep a **canonical structured requirement state**,  
- run a **mechanical validator** after every user answer,  
- derive the **next question from the validator’s remaining failures**,  
- preserve a **separate completion state** before downstream consumption,  
- and evaluate with **gold hidden requirements + per-turn hit tracking** rather than with vague “did the conversation feel complete?” judgments.

That is the shared practical core behind Spec Kit’s best ideas, the classic slot-filling systems’ durable ideas, and the parts of ReqElicitGym that are most worth stealing.