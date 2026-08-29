# Stage 03 notes

The canonical role table lives in `mechanism/roles_v1.yml`. This document keeps
the stage narrative and does not maintain a second copy of the roles.

Model selection is owned by `model_routing`. The live catalog is
`model_routing/catalog_v1.yml`; this stage references it and does not restate it.

## What this stage produces

- a result model
- an alternatives-rejected record
- a Stage04 handoff

## What this stage must not acquire

- a second mutable role table
- a second mutable model catalog
- a copy of the context-management policy
