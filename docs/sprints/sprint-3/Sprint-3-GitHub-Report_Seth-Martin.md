# Sprint 3 GitHub Report - Seth Martin

- **Repository:** [JoeBeebz/RateMyFries](https://github.com/JoeBeebz/RateMyFries)
- **Student / GitHub author:** Seth Martin / `SethMart1`
- **Sprint:** FRY Sprint 3, scheduled October 20-November 3, 2026
- **Snapshot date:** October 20, 2026, including the commit containing this final report refresh.
- **Report type:** In-progress sprint snapshot. The sprint is active and required review/merge remains unfinished.

## PRs Merged During the Sprint

**No PRs were merged during this reporting period.** The merged-only list is empty, so there are no merged PR titles, authors, reviewers or merge dates to list.

Verified query:

```text
repo:JoeBeebz/RateMyFries is:pr is:merged author:SethMart1 merged:2026-10-20..2026-11-03
```

[Run the merged-only search](https://github.com/JoeBeebz/RateMyFries/pulls?q=is%3Apr+is%3Amerged+author%3ASethMart1+merged%3A2026-10-20..2026-11-03).

Open PRs, closed-but-unmerged PRs and direct pushes to main are not counted as merged delivery. The implementation submission is awaiting the repository's required approving review; it is excluded from the merged-only list and Jira Done totals.

## Commit Activity

| Metric | Value |
| --- | --- |
| Total authored sprint commits in this submitted snapshot | **21** |
| Commits included in merged sprint PRs | **0** |
| Direct pushes to main during this work | **0** |
| Date of first commit | October 20, 2026 (01:59:54 CDT) |
| Date of last commit | October 20, 2026 (this report-refresh commit) |
| Date range | **October 20, 2026 - October 20, 2026** |
| Author | SethMart1 |

The 21 commits are on `feature/sprint-3-discovery-and-business-moderation`, after pre-sprint main revision `8c94203f8925febc66ce18f8ddb0fbcc1bdae245`. The first 12 implement/test/document the stories and relocate Sprint 2 artifacts, two submit the Jira/GitHub reports in that order, three address scan findings and expand regression coverage, three submit the PDFs/raw evidence, and one refreshes both sprint reports after validation. These are actual GitHub commits, not local-only commits. Commit activity is not accepted merged delivery.

Evidence: [branch commit history](https://github.com/JoeBeebz/RateMyFries/commits/feature/sprint-3-discovery-and-business-moderation/). The 20 commits preceding this report refresh end at [`301ce9353a2fee023506ae23e646fc7dacb4dfeb`](https://github.com/JoeBeebz/RateMyFries/commit/301ce9353a2fee023506ae23e646fc7dacb4dfeb).

Reproduce the snapshot from the feature branch (PowerShell):

```powershell
$reportCommit = git log -1 --format=%H -- docs/sprints/sprint-3/Sprint-3-GitHub-Report_Seth-Martin.md
git rev-list --count "8c94203f8925febc66ce18f8ddb0fbcc1bdae245..$reportCommit"
git log --reverse --format="%H %cI %an" "8c94203f8925febc66ce18f8ddb0fbcc1bdae245..$reportCommit"
```

## Validation and Submission Status

The final application passed **48** isolated integration/regression tests and JavaScript syntax validation. Desktop/mobile search layout and missing-key fallback were inspected in browser. Final SonarQube findings are zero across required categories with a passing quality gate; Trivy CRITICAL/HIGH/MEDIUM/LOW dependency vulnerability counts are zero. [Scan PDFs and raw evidence](static-analysis/) identify the exact scanned code revision; later commits only add report/evidence files.

Google credential-dependent live checks remain unfinished. Details and Jira mapping are in [IMPLEMENTATION.md](../../../IMPLEMENTATION.md). No repository review requirement was bypassed, no PR was closed unmerged to simulate delivery, and no unmerged work is represented as merged. Refresh this report after approval/merge or sprint closure for a completed-sprint submission.
