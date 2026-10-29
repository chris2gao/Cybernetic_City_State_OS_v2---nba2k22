# Checkpoint003 — precise Native daily training suboperations

Human M0-M5 objective remains active; base remains PR18 `094f1aa641f93dec2277707ad9dbf5bdb0341247`.

Two real code paths, `TRAIN_TEAM_PATCH_FOCUS_RAW` and `TRAIN_TEAM_PATCH_PROFILE_RAW`, now copy the existing daily record into caller-owned input, patch only the requested region and call the original Native Apply. They do not write live object fields, choose another date, infer UI units or generate a training strategy. Full original request, per-action identity and phase checks, durable no-replay journal and independent readback boundary remain in effect.

Six offline tests execute the real JS handler against a bounded private-pointer memory model, verify every input byte and exact Native call sequencing, check missing-day/invalid-array negatives and test batch conflicts versus independent day fields. No real Native call occurred. Current source counts:64 Native action records,39 binding/layout records (one non-callable new signing candidate),56 effective role mappings,183 retained requirements.

The signing caller at `0xea9d20` was recovered to1120 bytes. It clarifies selected arguments to acquire/reset, while exposing prior player-state side effects; those UI arguments cannot be promoted into universal safe defaults. See SIGNING_RECOVERY_PROGRESS.md.

Source inventory now retains the initial checkout hash and adds immutable baseline Git blob hashes. Source regression verifies those fixed historical blobs and current path existence, permitting authorized updates to README and other source documents without falsifying the initial observations. Current implementation/coverage tests remain separate from those historical anchors.

Next: continue full GM/Coach/Player Native recovery and domain parameter meaning; add actual readback/current-context adapters and concentrated live test scenarios when callable contracts are concrete. This checkpoint does not satisfy full M0-M5 completion.
