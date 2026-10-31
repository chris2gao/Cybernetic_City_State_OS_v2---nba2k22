# NBA2K22 VAE GPT External Single-Field Loop — 115/204

Task: `NBA2K22-VAE-GPT-EXTERNAL-SINGLE-FIELD-LOOP-20261030-001`
Role: `execution`; model GPT-6 conversation-declared, not host-signed.
Branch: `task/nba2k22-vae-gpt-external-single-field-loop-20261030`
NBA master base: `45cc45cae0550ddcda192a2179ea48509b27f6ee`.
Seed queue: `6436515330f77c0cc5cc675b521590adeb69c5d4`, blob `af5567e14e03cd9f7761e396a978311e347d7c17`.
Run state commit before pointer: `a20d69aed051f6d5500ee14a3f49889bea585737`.

## Current checkpoint

- Sweep 1: **115 of 204 researched-with-explicit-unknown**, **89 remaining**.
- This invocation resumed from 90, recovered previously committed 094–095, and completed **091–115** (25 fields including those recovered).
- Latest `WORLD_REG_016` / candidate `settings.trade_rules.cpu_trade_frequency` at +`0x178`; next **`WORLD_REG_017`** / `settings.trade_rules.blockbuster_trade_frequency` candidate +`0x17C`.
- `NO_DIRECT_NATIVE_FIELD_IDENTITY_SOURCE`: **51** total (recount from 115 consecutive iteration rows). World setting candidate offsets are similarly unverified, but **not** counted as new NO_DIRECT_SOURCE result flags in this batch.
- Exact authoritative resume files: `06_执行/current_checkpoint.json` + `06_执行/iteration_ledger.jsonl` at actual latest branch HEAD.

## New per-field findings and source limitations

**Player tendencies 091–099:** Flashy Pass, Alley-Oop Pass, Pass Interception, Take Charge, On Ball Steal, Contest Shot, Block Shot, Foul, Hard Foul. Same-version roster and official gameplay materials establish named categories and system changes; none validates PC22 candidate offsets `0x4B2–0x4BA` or native decision coefficients. Attempted actions, successful steals/blocks, resulting fouls and global CPU/User sliders must be measured separately.

**World settings 001–008:** Quarter Length, Game Speed, Free Throw Difficulty, Shot Clock, Foul Out, Injuries Enabled, Simulated Quarter Length, Normalize Stats. Differentiated played versus simulated quarters, player and CPU modes, per-minute versus per-stat normalization, injury On/Off vs injury frequency/effects. `WORLD_REG_004` `shot_clock` is a semantic collision (HUD On Court Shot Clock vs 24-second rule); `WORLD_REG_008` `normalize_stats` not yet uniquely mapped to Normalize Played to Sim Stats. Only the actual in-game UI and read-only memory evidence can decide.

**World trade settings 009–016:** CPU-CPU Trades, Trade Override, Trade Deadline, Financial Trade Rules, Recently Signed Restrictions, Recently Traded Restrictions, Trade Difficulty, CPU Trade Frequency. Same-release trade menu proves distinct concepts, not exact native offsets or actual PC22 validators. Human-authorized external GM simulation remains a separate rule source; no trade or change to game configuration was performed. No imported NBA2K21/2K15 CBA detail was elevated to established PC22 behavior.

Each new dossier has an external source question, URLs and author/date/version/platform limitations, caveats and confounders, suggested observable denominators, and **one** bounded read-only Gemini REA identity/readback question. The external research stream never runs Gemini or the game.

## Evidence and correction

- 25 field dossiers: `06_执行/field_records/TENDENCY_NATIVE_091.json`–`099.json` and `WORLD_REG_001.json`–`016.json`.
- 25 per-field static receipts: `07_测试执行/sweep01_field0091_static_verification.json`–`sweep01_field0115_static_verification.json`.
- Consolidated receipt: `07_测试执行/sweep01_fields0091_0115_readback.json`.
- `07_测试执行/sweep01_field0092_0093_id_correction.json` explicitly documents prior field-ID zero-padding correction, with original Git parent commit preserving historic proof. The new canonical dossiers are `TENDENCY_NATIVE_092/093` and old unpadded files are absent. No source/game finding was changed by correction.
- 115 chronological iteration records and exact next queue ID verified, all 115 dossiers and receipts present; only this Run changed, expected master merge base unchanged.
- `run.yml` now has cursor 115 and remaining 89.

Not done: game runtime, REA validation, independent audit, PRMS task-context publication, formal Communication v2, Core/master merge, scheduler. No native mapping, causal weight, optimal number or simulation outcome claimed.

**Status: `SWEEP1_CURSOR_115_CHECKPOINTED_LOOP_OPEN`.**
