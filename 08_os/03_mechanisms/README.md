# 03_mechanisms

General reusable capabilities. Each mechanism is self-contained: it can be described,
loaded and verified on its own, and a workflow references it rather than reimplementing
it.

## Holds

One subdirectory per mechanism. The communication protocol is one. Release binding,
lane coordination, and compliance validation are others in the first-generation system.

Each mechanism directory should be able to answer, from its own contents: what it does,
what loads it, what it needs on disk, and how a break would show up.

## Does not hold

Workflow-specific steps. If it only makes sense inside one workflow, it is a workflow
stage, not a mechanism.

## The one property every mechanism here must declare

**When a failure surfaces.** This is the field the first-generation system lacked and
paid for twice. A missing test fixture turns the suite red on the next run. A missing
permission policy produces no signal at all — the system simply stops refusing things,
and nobody learns of it until something that should have been refused happens.

A mechanism whose breakage is silent needs a registry entry more than one whose
breakage is loud, not less.

## Candidates for porting

The communication protocol stack, the release binding cycle, the lane epoch mechanism
and the compliance validator all work in the first-generation system and all have
measured failure histories worth carrying over with them. Porting is selective:
assessed one at a time, not copied wholesale.

Empty until the first mechanism is ported or written.
