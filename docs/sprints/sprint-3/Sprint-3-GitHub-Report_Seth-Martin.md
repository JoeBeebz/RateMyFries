# Sprint 3 GitHub Report — Seth Martin

- **Repository URL:** https://github.com/JoeBeebz/RateMyFries
- **Student:** Seth Martin
- **GitHub username:** `SethMart1`
- **Sprint:** FRY Sprint 3 — October 20–November 3, 2026
- **Reporting cutoff:** main revision [`ed9d4e75fa9614ef2b9ff5bbf8726756a06991a6`](https://github.com/JoeBeebz/RateMyFries/commit/ed9d4e75fa9614ef2b9ff5bbf8726756a06991a6), October 20, 2026, 10:05:16 p.m. CDT
- **Time zone:** America/Chicago (CDT, UTC−05:00). GitHub's UTC timestamps are also provided for merges.

## PRs Merged During the Sprint

Only PRs verified as merged within the sprint window are included below. Both were authored by `SethMart1`, approved by `JoeBeebz`, and merged into `main` by `JoeBeebz`.

| PR title | PR link | Author | Reviewers | Merge date (CDT) | Merge timestamp (UTC) |
| --- | --- | --- | --- | --- | --- |
| Sprint 3: unified discovery and moderated business listings | [#4](https://github.com/JoeBeebz/RateMyFries/pull/4) | SethMart1 | JoeBeebz — Approved | October 20, 2026, 7:13:44 p.m. | 2026-10-21 00:13:44 UTC |
| Sprint 3 demo video | [#5](https://github.com/JoeBeebz/RateMyFries/pull/5) | SethMart1 | JoeBeebz — Approved | October 20, 2026, 10:05:16 p.m. | 2026-10-21 03:05:16 UTC |

PR #4 delivered the unified restaurant/fry search, address and Google Places integration code, account roles, private profile addresses, business submission and admin review workflows, updated requirements, organized Sprint 2 artifacts, and Sprint 3 reports/static-analysis evidence. PR #5 added the Sprint 3 demo recording. Merge status does not establish successful live Google API acceptance testing; that requires configured credentials and billing.

Verified merged-only query:

```text
repo:JoeBeebz/RateMyFries is:pr is:merged author:SethMart1 merged:2026-10-20..2026-11-03
```

[Run the merged-only search](https://github.com/JoeBeebz/RateMyFries/pulls?q=is%3Apr+is%3Amerged+author%3ASethMart1+merged%3A2026-10-20..2026-11-03).

## Commit Activity

| Metric | Value |
| --- | --- |
| Total work commits authored by Seth Martin and included in merged sprint PRs | **22** |
| Work commits in PR #4 | 21 |
| Work commits in PR #5 | 1 |
| Merge commits authored by JoeBeebz | 2 |
| Total new commits on main, including merge commits | **24** |
| Direct pushes to main counted toward delivery | **0** |
| First work commit | October 20, 2026, 1:59:54 a.m. CDT — [`644f748`](https://github.com/JoeBeebz/RateMyFries/commit/644f748ceea31a4c56e38d364654c2b840ad192c) |
| Last work commit | October 20, 2026, 9:56:07 p.m. CDT — [`d4a29e5`](https://github.com/JoeBeebz/RateMyFries/commit/d4a29e53813e28d44f6573276c21c285d775a3c2) |
| Work commit date range | **October 20, 2026–October 20, 2026** |
| Last commit including merges | October 20, 2026, 10:05:16 p.m. CDT — [`ed9d4e7`](https://github.com/JoeBeebz/RateMyFries/commit/ed9d4e75fa9614ef2b9ff5bbf8726756a06991a6) |

The count covers commits after the pre-sprint main revision `8c94203f8925febc66ce18f8ddb0fbcc1bdae245` through the reporting cutoff above. The 22 work commits use the Git author names `SethMart1` and `Seth Martin`, associated with the same `SethMart1` GitHub account. The two merge commits are reported separately to avoid presenting them as additional student work commits. Open PRs, closed-but-unmerged PRs, local-only commits, and this replacement report's subsequent submission commit are excluded.

## Evidence and Reproduction

- [PR #4 commits](https://github.com/JoeBeebz/RateMyFries/pull/4/commits) — 21 commits; merge commit [`ed776f4`](https://github.com/JoeBeebz/RateMyFries/commit/ed776f40783ebdacdc4c2c9651f5374c282b3f8f).
- [PR #5 commits](https://github.com/JoeBeebz/RateMyFries/pull/5/commits) — 1 commit; merge commit [`ed9d4e7`](https://github.com/JoeBeebz/RateMyFries/commit/ed9d4e75fa9614ef2b9ff5bbf8726756a06991a6).
- [Exact reporting comparison](https://github.com/JoeBeebz/RateMyFries/compare/8c94203f8925febc66ce18f8ddb0fbcc1bdae245...ed9d4e75fa9614ef2b9ff5bbf8726756a06991a6).

Reproduce the fixed snapshot after fetching the repository (PowerShell):

```powershell
$reportBase = '8c94203f8925febc66ce18f8ddb0fbcc1bdae245'
$reportCutoff = 'ed9d4e75fa9614ef2b9ff5bbf8726756a06991a6'
git rev-list --count --no-merges "$reportBase..$reportCutoff" # 22 work commits
git rev-list --count --merges "$reportBase..$reportCutoff"    # 2 merge commits
git rev-list --count "$reportBase..$reportCutoff"             # 24 total commits
git log --reverse --format='%H %aI %an %s' "$reportBase..$reportCutoff"
```

This report replaces the earlier pre-merge Sprint 3 GitHub report. It records verified merged activity through a fixed cutoff while Sprint 3 is still scheduled to continue; later activity requires a new snapshot.
