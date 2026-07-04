# Math Mentor Teaching Flow Static Tests

This directory contains deterministic, no-runtime validation for the Math Mentor manual teaching-flow layer.

## Scope

The validator checks:

- static prompt/spec contract phrases and safety boundaries;
- tool-truthfulness state coverage;
- unsafe affirmative tool-execution wording;
- fixture-level expected behavior for:
  - `TRIG-006` as a ready `MathLane_A` positive fixture;
  - `CALCULUS-265` as a `request_reprep` negative fixture.

## Boundaries

The harness does not call any LLM, runtime Coordinator, external app, MCP, Z3, SymPy, PyTorch, calculator, browser, visualization, sandbox, or teaching session executor.

It reads repository text files and fixture JSON files only. It writes result reports under `tests/results/`.

## Run

From the repository root:

```powershell
python 08_Domain_Applications/Math_Mentor/tests/teaching_flow_static_validator.py
```

The script exits nonzero if any required check fails.
