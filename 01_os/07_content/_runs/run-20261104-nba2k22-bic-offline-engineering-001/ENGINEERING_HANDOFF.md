# BIC Batch1 offline engineering candidate

Human authorization is fixed at `f082f853ca4388d498371a101621ce176e6e22ee`, planning Run `HUMAN_OFFLINE_ENGINEERING_AUTHORIZATION_20261104.md`. Base is P0 `17bca5c5e34a4bc3b153c38634681962e1600ec7`; business source remains NBA `66f8f73f1a91597f4562b834c2acad332ad9de5b`. Delivery head is the exact Git commit in the Human-facing handoff. Review owner is GPT-6 decision_architecture via Human relay.

## Delivered behavior

`world_data_prototype/bic_baseline.py` composes existing cards and the historical observation scope with an optional season filter. Default callers retain all-season behavior. BIC requires explicit save/season/cutoff, preserves field age and provenance, rejects conflicting or explicitly mismatched Native identities, and exposes NULL legacy season binding as DATABASE_LOCAL_ONLY. Existing restricted queries retain WITHHELD semantics. Current/effective game context remains distinct from base raw values.

`bic_cli.py` is a runnable one-shot player/team JSON entrypoint. `coverage_report` lists actual contributing units and missing/stale observation counts. `badge_intelligence` carries historical ownership/level observations with UNKNOWN eligibility, XP, growth and effects. `bic_experiments.py` computes labelled synthetic 2x2 arithmetic and exposes real-data confounding/behavior limits. Read `world_data_prototype/BIC_READONLY.md` for examples.

## Verification and limitations

Run `python -B -X utf8 <this-run>/verify_offline.py --historical-database <existing-v24.sqlite>`. Omitting the optional database runs synthetic/related regressions only. The script stores raw stdout/stderr, actual command/exit code/timing and historical example summaries. The selected test group covers BIC, existing observation scope and player-detail decoder. Historical query examples use Jokic and Siakam plus the teams resolved through their Native source observations. They retain UNBOUND header, null fingerprint/build, unverified player identity and multiple source units. Production/real-data admission remains REAL_DATA_NOT_VERIFIED.

The first BIC run had three failures because existing season rows permit NULL save_id. The correction accepts database-local season membership only after matching the database header, exposing that weaker link explicitly. Four tests then passed. Subsequent increments added Native conflict rejection, badge negatives, season isolation, CLI and factorial examples. Final raw receipts supersede earlier construction-test summaries, without inventing archived logs for those earlier chat calls.

No game acquisition, date advancement, Native/REA execution, data migration or master integration occurred. Formal Stage01–07 acceptance, frozen-test certification and independent acceptance are not claimed. This is an authorized offline candidate for series review. PRMS save was not invoked; recovery_source is this Git Run and its published commit.

## Remaining review questions

General cards retain UNKNOWN per-game mode because FRANCHISE/REGULARSEASON metadata does not distinguish Fast Sim, CPU3D and Human3D. Any future game-specific consumer needs source-linked game mode. Qualification predicates and effects require version-specific evidence. Database-local identity needs independent save/build provenance. Synthetic factorial contrasts provide no game causal proof or confidence interval.

P02/P07/P10 discovery entries and the project index were updated in this candidate. Stage02 targeted evidence in `run-20261104-nba2k22-bic-stage02-targeted-evidence-001` is research input for the same review; its evidence adjudication is separate from formal OS Stage02 acceptance.
