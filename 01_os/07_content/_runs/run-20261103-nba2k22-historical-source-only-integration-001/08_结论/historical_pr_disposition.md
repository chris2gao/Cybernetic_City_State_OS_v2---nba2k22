# Unmerged historical PR disposition — current source-only strategy

Source: GitHub PR metadata at 2026-11-03 and exact Git tree/blob comparisons with the **original** Host at `1fc2965ae10ef2a34abb37d800d86cd548f24aeb`. **Matching Git blobs indicate content match, not completion or shared ancestry.** A blank/absent matching blob does not prove different semantics are absent.

The Human superseded the full Host merge; this branch imports useful **Host source blobs** only and intentionally does not import earlier old REA development branches wholesale. Any old task `CLOSED_WITH_DEFERRED_SCOPE` remains deferred.

| PR | Historical HEAD | Historical scope and non-merge cause | Files matching old Host at same path | Source-only disposition | Executed in this integration |
|---|---|---|---|---|---|
| [#8](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/8) | `be9178b9cae23ee822d5c415eb02cd41f98f4122` | Human-driven game loop and 8 prototype scenes / 12 capture nodes, ready for independent review at the time; open while awaiting integration | 0/9 | **EXTRACT_PENDING**: historical contract is useful but must not override newer Human capture cycle policy; preserve PR and source document | No file extraction from #8; HOLD |
| [#10](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/10) | `cfce2c88bcaf38362ff7270242cd982bd9757415` | Research prototype + read-only identity guard; not production native mechanism | 0/155 | **RESEARCH_ONLY / EXTRACT_PENDING**: mechanism knowledge/experiment evidence may remain useful; no full-branch merge | No extraction; HOLD |
| [#12](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/12) | `f6b2f5deb73218406f034c5418896c4bfade8e64` | Native coach/trade original live invocation and partial receipts; awaiting integration | 0/188 | **EXTRACT_PENDING**: retain original reports/readback evidence, do not imply transaction certification | No extraction; HOLD |
| [#14](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/14) | `2bdda79c6513f463252d7d01834218edb590eec9` | Broader static NativeActionRegistry/Facade; new live tests explicitly not run | 47/89 | **PARTIAL_INCLUDED**: shared sources updated by Host; independent old evidence remains in PR | Included matching Host source only; older gaps HOLD |
| [#16](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/16) | `b7e0f51e8e00be4c3233af2c73c26c73b4958e80` | Real native Coach/Scout/Trade evidence; planned integration was deferred | 14/355 | **EXTRACT_PENDING**: separate evidence files not equivalent to Host updates | No missing historical evidence extracted; HOLD |
| [#17](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/17) | `84195f471354400a75877f16c3c3de8a3af6b5b2` | Old integration vehicle for #10 + #12 + #14 + #16 | 60/764 | **SUPERSEDED / HOLD**: do not re-merge old full chain into source-only mainline | No |
| [#18](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/18) | `094f1aa641f93dec2277707ad9dbf5bdb0341247` | Planning inventory, 183 action requirements are **not** 183 implemented functions | 9/20 | **PARTIAL_INCLUDED / EXTRACT_PENDING**: planning seeds not falsely promoted to executable capability | Historical plan only, no new implementation |
| [#19](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/19) | `6151ef5d484914edcec2fbcfcf3bcce83a848907` | Checkpoint014 explicitly `CLOSED_WITH_DEFERRED_SCOPE`, `full_goal_complete=false` | 260/269 | **PARTIAL_INCLUDED**: Host contains identical bulk of completed sources; 9 missing/different paths remain separately visible | Matching Host blobs included; no full old-PR merge |

**Important decision boundary:** `PARTIAL_INCLUDED` does not mark all historical PR requirements fully complete. The old missing independent document/experiment sources are still present on their original unmodified PR branches; the Human must separately choose if/when to extract them. Existing old PRs are neither auto-closed nor deleted.

## New source-only integration and old full-history staging
- [Clean source-only PR #26](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/26) is the active integration candidate.
- Old staging PR #24 merged Host into **an ordinary staging branch**, not master.
- Old full-history [PR #25](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/25) was marked superseded/closed without merging master; its Git ref and large objects are left untouched.
- Core [PR #13](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/pull/13) already merged to Core master `d463b83c74c17d74cacf64c4d82e4abce5004b75` under the separate Human-approved verification gate waiver.

No historical test receipt is rewritten and no new old-feature acceptance is claimed.
