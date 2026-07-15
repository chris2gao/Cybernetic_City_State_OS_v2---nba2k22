# Branch Consolidation and Repository Ledger Validation

## Validation target

- Task: `branch-consolidation-and-repository-ledger-0001`.
- Exact starting master: `22cf4731cd29a2ebe271fe67fd561df1d0701d01`.
- Work branch: `codex/branch-consolidation-and-repository-ledger`.
- Candidate head: `commit_containing_this_report` (exact SHA resolved in the
  post-merge review handoff).
- Publication PR: the ready PR publishing this report (exact number resolved in
  the post-merge review handoff).
- Final remote/local master: `merge_commit_containing_this_report`; exact SHA
  and three-way equality are resolved in the post-merge review handoff.

## Candidate validation matrix

| Check | Expected | Candidate result |
|---|---:|---|
| normalized logical branches | 84 | pass: 84 |
| local branch refs | 77 | pass: 77 |
| concrete origin branch refs | 62 | pass: 62 |
| branch summary rows | 84 unique | pass: 84 rows / 84 unique names |
| classification total | 84 exactly once | pass |
| merged / safe / reconciliation / superseded / historical / blocked | 39 / 1 / 3 / 3 / 38 / 0 | pass: 39 / 1 / 3 / 3 / 38 / 0 |
| required ledger sections | 12/12 | pass: 12/12 |
| unfinished memo YAML | strict parse | pass: PyYAML strict load, schema `plan3_unfinished_task_memo.v3` |
| task-created source paths | exact allowlist subset | pass: exact five paths |
| source mailbox neutrality | unchanged and neutral | pass: no diff in INBOX/OUTBOX/STATE/HUMAN_BRIEF |
| `git diff --check` | pass | pass |
| scoped high-confidence secret scan | zero findings | pass: zero findings; values were not logged |
| prohibited activation indicators in changed paths | zero | pass: no runtime/Coordinator/Gateway/writer/poller path changed |

## Publication validation

- Ready PR mergeability/checks: resolved and recorded in the post-merge
  review-branch copy of this report.
- Expected head binding before merge: resolved and recorded in the post-merge
  review-branch copy of this report.
- Merge method: `merge` only.
- Direct master push: prohibited and not used.
- Published tree contains the five intended source paths only: verified after
  merge and recorded in the post-merge review-branch copy.
- Post-merge root ledger and refreshed memo existence: verified after merge and
  recorded in the post-merge review-branch copy.

## Local sync validation

After publication, the required commands are executed without an elaborate
unique-commit or dirty-tree preflight:

```text
git switch master
git pull origin master
```

Final equality evidence:

- local `HEAD`: exact value recorded in the post-merge review-branch copy.
- `origin/master`: exact value recorded in the post-merge review-branch copy.
- GitHub remote master: exact value recorded in the post-merge review-branch copy.
- equality result: required to be true and recorded after the direct pull.
- local worktree status: recorded after the direct pull.

## Final reclassification rule

The root ledger freezes the exact pre-publication audit so every discovered ref
can be recorded without attempting to predict the SHA of the commit containing
the ledger. After normal merge, the task branch changes from the audit
classification `safe_to_merge` to the final physical relation `merged`; the
post-merge exact counts and SHA are recorded here on the review handoff branch.
