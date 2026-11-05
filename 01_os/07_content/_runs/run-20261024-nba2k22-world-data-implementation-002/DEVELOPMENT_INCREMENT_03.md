# Increment 03 — registered PLAYER families and actual owner acquisition

Parent task remains **active and incomplete**. This is implementation/evidence progress, not final Native, independent or Human whole-system acceptance.

## Actual code and data

- Schema **v3 / 62 STRICT tables / 659 columns**. Added typed `native_box_observations`, because real source controls demonstrated that Native PlayerID is not unique across the observed pool. Staging retains actual Box values while accepted canonical identity is unresolved; it is not a universal JSON replacement or an accepted Player API.
- `family_codec.py` parses exact registered bit widths, including fields crossing a byte boundary. Original contract years at byte 833 bit 4–6 and extension length at bit 7–9 do not overlap. This corrects the earlier shared-byte ambiguity at the registry level, not its game/UI semantics.
- Three actual historical PLAYER samples now load public names, 54 attribute values, 17 contract fields, 48 named tendencies and four ordered PlayType slots per player. Unknown badge tiers remain gaps, and no hidden Potential is emitted.
- New-file v1/v2→v3 copy upgrades retain original source bytes, old domain facts and old registry evidence, adding only missing catalog fields. Old files are never overwritten.

## Actual current-process evidence

After Human's administrator grant, the worker successfully opened test PID 2564 using 0x1010 read/query rights. It read a SEASON header, one 60-byte game and a complete 624-byte/26-row Box window.

The historical report contains an arithmetic conflict: hex `0x1B6AC` is 112300, not its documented decimal 112308. Reading the hex candidate produced nonconserving Box sums 1050/1034 versus period totals 122/106. Reading **112308 = 0x1B6B4** produced exact 122/106 conservation for this game. Both byte samples and complete instrumented read traces are retained; neither result proves every game/window/UI field.

Descriptor-bounded lookup observed **3390 PLAYER records and 9773 Slot24 records**. It read only 2-byte PLAYER IDs, bounded public names and current season indices/48-byte records, not full PLAYER structures or hidden Potential. Native ID 1607 appeared at indices 16/742 (both Jrue Holiday); ID 2328 appeared at 249/3389 (both Kyrie Irving). One candidate in each pair had a current 2022 season record and expected native team, while the other had sentinel 65535. These are useful active/template controls, not permission to automatically merge records or claim a stable save binding.

## Actual database/query behavior

`replay-owner-capture` consumes the recorded source artifacts, checks hashes and matching read-trace entries, re-decodes the raw bytes, rejects the wrong-offset negative control even if JSON claims PASS, and loads one research source unit with two native team Box fragments, eight regulation-period rows and **26 typed unresolved player Box rows**. `inspect-source` reports their 122/106 sums. No canonical players or player-game Boxes are invented from duplicate IDs. Unknown persistent save identity and calendar UI semantics remain explicit gaps; canonical game date stays NULL.

This database is a research replay of this task's actual live acquisition, not a persistently bound production world file. `RESEARCH_FIXTURE` describes the replay/candidate maturity; provenance records its current owner-captured origin. Ordinary GM queries cannot read owner source staging. There are no implicit Q10 exceptions.

## Evidence and remaining work

Raw controls: `world_data_prototype/tests/fixtures/owner_capture_20261024/`. Full traces and identity controls: `06_执行/increment03/native_sources/`. Compressed trace files preserve complete original bytes, with SHA256 of the uncompressed report in the manifest. Tests verify raw-data behavior and negative cases; a fixture replay is not a fresh live read or an independent review.

The actual owner worker is no longer blocked by the earlier error-5 permission mismatch. Main remaining work includes persistent save/active-player identity binding, complete schedule and other source-domain adapters, UI/calendar/badge/contract semantics, coverage and role outputs, capacity/recovery tests, completed-candidate managed verification and separate review/Human acceptance. The full engineering goal is not narrowed to the work already built. Gemini remains optional batch support through Human; Codex retains ownership and can continue Native research directly.
