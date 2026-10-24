# Human save binding — 2026-10-24

Human chose the simple engineering ID `nba2k22_test_01` and declared the currently loaded dedicated test file:

`E:\games\NBA 2K22\data\steam\steam_settings\1644960\remote\MyLEAGUE0003`

Human will announce multi-save switches in advance and supply the actual filename. Initialize a separate facts database for each independent save; reuse the existing ID/database when reopening the same save. Opening a fresh career initializes its own world records. Do not require PID, pointer or player-data fingerprints to prove long-term identity, and do not introduce cross-save ancestry/merge relations.

The actual file exists (4,322,888 bytes when checked). This is an operator declaration, not a claim that the game embeds the engineering ID. File size/timestamps/hashes can change as a save progresses. PID and pointers are reacquired for each capture and do not define the save identity.

Runtime binding: `_runtime/world-saves/nba2k22_test_01/save.json`; facts: adjacent `world.sqlite`. Durable binding copy: `06_执行/increment04/native_sources/save_binding.json`. This operation initialized only engineering files and read the game process; it did not modify the native save or advance the game date.
