# 06_execution

The loaders. Given the registry, this is where a mechanism, a workflow part, the
environment, a skill or a tool gets initialised or reloaded — so that a model picks up
the right thing, correctly, every time.

## Holds

One subdirectory per area it can load, mirroring the structure it loads from:

```
06_execution/
  workflow/      loads a workflow and its stages
  boot/          establishes the environment
  mechanisms/    initialises or reloads one mechanism
  skills/        makes a skill available and verifies it is present
  tools/         same, for tools
```

Each loader states what it reads from the registry, what it puts in context, in what
order, and how to tell afterwards whether it worked.

## Does not hold

Definitions. A loader for the communication protocol lives here; the protocol itself
lives in `03_mechanisms/`. Keeping them apart is what allows a mechanism to be reloaded
without being rewritten.

## What "correct loading" has to mean here

Not "the files were read". The first-generation system could already prove which files
a session loaded, by receipt, and that proof was genuinely useful. What it could not
do was answer what happens when a load is partial or stale — and the cost showed up as
sessions that believed a stale routing snapshot over physical Git state.

So each loader declares its own failure mode: what a partial load looks like, and what
the model should do when it detects one. Failing loudly is a requirement, not a
nicety — this is the area whose failures would otherwise be silent by construction.

Empty until the first loader is written.
