from pathlib import Path
p=Path.cwd()/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/README.md'
text=p.read_text(encoding='utf-8').replace('**Schema v19: 87 STRICT SQLite tables, 1,404 columns**','**Schema v20: 88 STRICT SQLite tables, 1,471 columns**')
marker='Increment 26 adds `capture-game-mode'
at=text.index(marker)
paragraph='''Increment 28 adds `capture-finance PID SAVE_DIRECTORY LOADED_FILENAME NEW_OUTPUT_DIRECTORY`, the ordinary `finance` refresh family, and `finance DB [--team-id ID] [--unit-id UNIT] [--as-of TIMESTAMP]`. The Native TEAMDATA metadata identifies 4 unsigned scalars, 22 signed int32 accounting words, 15 float32 scalars and 4 packed flags/enums. `native_team_finance_observations` stores typed columns and original float words; NaN/infinity retain their word and a NULL REAL. The collector verifies the current primitive CRCs, complete field signature, exact enum tables and name dimensions, reads 30 core TEAM projections, repeats all identities/data/directories, and pairs the same-unit Native game-mode date/stage. Native `UnlocalizedTeamName` has25 UTF16 code units and the short name has7; the new source reads verified extents. No PLAYER value is read. `Salary` is unsigned and distinct from signed `ExpPayroll`; the legacy `payroll_raw` alias is `ExpPayroll`, and `cash_raw` is `BankBalance`. Existing unsigned legacy rows remain unchanged. The team query labels those aliases and includes the new complete-source-unit finance result. Copy-upgrade v19 to a new v20 file before acquisition. Observation season does not establish accounting duration; UI currency/scale, legal spending, cap space, profit and live financial transitions remain unproved. Packed neighbor fields are excluded, and unknown enum codes keep raw values with NULL labels. Annual history/awards cadence is unchanged.

'''
if paragraph not in text:text=text[:at]+paragraph+text[at:]
p.write_text(text,encoding='utf-8',newline='\n')
