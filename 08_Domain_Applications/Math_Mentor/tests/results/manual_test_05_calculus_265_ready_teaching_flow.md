# Manual Test 05: CALCULUS-265 Ready Teaching Flow

Status: pass

Scope: manual-chat readiness simulation only. This test does not activate the production Coordinator, runtime, external tools, apps, MCP servers, visualization, LLM API, learning-state writer, learned-history writer, or spaced-review scheduler.

## Target

- Node: `CALCULUS-265`
- Roadmap identity: `n_265`
- Expected behavior: `ready_teaching_flow`
- Lane: `MathLane_A`
- Evidence state: semantic-only, no deterministic tool execution claimed

## Result Summary

| Requirement | Result |
| --- | --- |
| Coordinator can generate ready `SYSTEM_STATE_DUMP` | pass |
| Prep can generate complete `lesson_plan` | pass |
| Socratic can teach average rate -> limit -> instantaneous rate / tangent slope | pass |
| Handles derivative-as-ordinary-division misconception | pass |
| Handles large-interval-average-as-instantaneous-speed misconception | pass |
| Handles continuity-implies-differentiability misconception | pass |
| Handles missing left/right derivative equality misconception | pass |
| Exam_Agent can generate trap test | pass |

## Coordinator Readiness

The target node is ready for manual teaching:

- `formal_definition_status: present`
- `prerequisites_status: present`
- `mapping_boundary_status: present`
- `validation_status: semantic_ready_for_manual_teaching`
- `tool_truthfulness.tool_status: not_run`

Compressed state dump is represented in `manual_test_05_calculus_265_ready_teaching_flow.json`.

## Prep Lesson Plan

The generated manual-test lesson plan covers all five source subtopics exactly once:

1. 导数作为增量比值的极限定义
2. 物理意义：质点运动的瞬时速度与加速度
3. 几何意义：曲线切线的斜率与割线的极限
4. 函数可导性与连续性的关系
5. 单侧导数（左导数与右导数）

`coverage_map` is complete: `source_subtopic_count: 5`, `planned_subtopic_count: 5`, `coverage_status: complete`, `handoff_status: ready`.

Subtopic coverage: `5/5`.

## Socratic Teaching Flow

The planned Socratic flow starts from the occurrence crisis:

1. A finite interval average rate cannot answer what happens exactly at one instant.
2. Shrinking the interval motivates a limit.
3. The formal compression is `f'(a)=lim_{h->0}(f(a+h)-f(a))/h` when the limit exists.
4. Physical meaning: instantaneous velocity.
5. Geometric meaning: secant slopes approaching tangent slope.
6. Boundary: continuity is necessary but not sufficient.
7. Boundary: left and right derivative limits must agree.

This satisfies the required chain: average rate -> limit -> instantaneous rate / tangent slope.

## Common Error Handling

- Derivative as ordinary division: repaired by distinguishing a fixed difference quotient from the limit of quotients.
- Large interval average as instantaneous speed: repaired by asking whether speed can vary inside the interval, then shrinking the interval.
- Continuous implies differentiable: repaired with `f(x)=|x|` at `0`.
- Ignoring left/right derivative equality: repaired by requiring the two one-sided slope limits to match.

## Exam_Agent Trap Test

Generated Stage 1 check:

```text
For f(x)=x^2, what limit expression defines f'(3)?
```

Generated Stage 2 trap:

```text
A function is continuous at a point and its left-side slopes approach -1 while its right-side slopes approach 1. Does the derivative at that point exist? Give the boundary reason in one sentence.
```

Expected pass boundary:

```text
No. The derivative does not exist because the left and right derivative limits disagree, even though continuity alone may still hold.
```

No classroom pass is claimed because no real student answer was collected. The test proves readiness to hand off a valid trap, not actual student mastery.
