# 04_skills_and_tools

External skills and tools that extend what a model can do here. Bolted on rather than
built in: the system works without them, and works better with them.

## Holds

- skill definitions the model can invoke
- tool wrappers and their usage contracts
- for each: what it requires to be installed, and how to check that it actually is

## Does not hold

Mechanisms the system itself runs on. If the city-state cannot operate without it, it
is a mechanism, not an extension.

## The check that must not be skipped

**Availability is measured, not assumed.** The first-generation system instructed every
agent to search with `rg`, on a workstation where `rg` was not installed. The
instruction sat there being wrong until someone checked. A separate note recorded
PowerShell behaviour that belonged to a version that was not the one running.

Every entry here declares how to verify the tool is present and at what version, and
that check is part of the entry rather than a note beside it.

Empty until the first skill or tool is registered.
