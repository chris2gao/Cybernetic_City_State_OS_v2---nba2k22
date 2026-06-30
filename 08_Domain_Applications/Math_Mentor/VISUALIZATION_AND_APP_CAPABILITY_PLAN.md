# Math Mentor Visualization And App Capability Plan

## 1. Purpose And No-Runtime Boundary

This document plans future visualization, app, skill, and MCP capability integration for Math Mentor.

It does not generate diagrams, plots, images, apps, browser sessions, notebooks, UI, MCP calls, external app connections, production Coordinator execution, runtime state, node YAML, bridge YAML, evaluator changes, prompt changes, student-state writes, learned-history writes, or scheduler writes.

## 2. Visualization Capability Classes

| class | teaching use | default state | evidence required before artifact claim |
| --- | --- | --- | --- |
| `verbal_sketch` | Student-facing verbal description of a picture, graph, or diagram. | `available` | No artifact claim; label as verbal sketch. |
| `static_diagram` | Future generated or manually authored diagram. | `planned` | artifact ref plus generation/authorship record. |
| `plot_or_graph` | Future plotted numeric or symbolic relationship. | `planned` | input data/ref, plotting command/log, artifact ref. |
| `interactive_widget` | Future manipulable teaching object. | `runtime_required` | app/runtime log, artifact URL/ref, privacy check. |
| `app_block` | Future app/skill/MCP-backed teaching surface. | `runtime_required` | Human authorization, app invocation log, output ref. |

## 3. Verbal Sketch Versus Generated Artifact

A verbal sketch is text such as:

- "Imagine the graph bending upward."
- "Picture a rotating vector with a shrinking radius."
- "A future diagram could show this as a surface."

A generated artifact is a concrete file, URL, rendered image, plot, widget, or app output.

Math Mentor may always use verbal sketches when pedagogically appropriate. It must not say a visualization was generated, rendered, plotted, opened, or displayed unless a future authorized run provides an artifact reference and log.

## 4. App / Skill / MCP Future Integration Constraints

Future app integration must declare:

```yaml
future_app_skill_handoff:
  capability: "future_app_skill"
  app_or_skill_name: "<name>"
  authorization_ref: "<Human-approved task ref>"
  input_refs: []
  privacy_status: "safe | redacted | blocked"
  invocation_log_ref: "<required after run>"
  output_artifact_ref: "<required after run>"
  failure_state: "unavailable | blocked | review_required | null"
  consumed_by: "Coordinator | Socratic_Router | Human"
```

No app, skill, or MCP call may be inferred from a plan document. Runtime connection requires future Human approval.

## 5. Student Privacy And State Boundaries

Visualization/app input must not contain:

- real student identity;
- private student notes outside the current authorized teaching state;
- secrets, tokens, `.env`, SSH keys, or private keys;
- unlisted hidden memory;
- full student-state directories;
- real learned-history or scheduler writes.

If private data would be required, mark the capability `human_only`, `blocked`, or `review_required`.

## 6. Human Authorization Gates

Human authorization is required before:

- generating a real visualization artifact;
- opening or connecting any app, plugin, skill, browser, notebook, or MCP server as part of Math Mentor runtime;
- storing generated artifacts in a student record;
- using private student data;
- activating production Coordinator or runtime integration;
- changing prompts, nodes, bridges, evaluator behavior, or source/master branches.

## 7. Future Implementation Checklist

- [ ] Identify whether the lesson needs a verbal sketch or a generated artifact.
- [ ] Use `planned` if no artifact exists.
- [ ] Use `run_with_log` only when invocation log and artifact ref exist.
- [ ] Record privacy status.
- [ ] Preserve artifact limitations.
- [ ] Keep semantic teaching separate from app/runtime execution.
- [ ] Route unresolved or contradictory visual evidence to `review_required`.
