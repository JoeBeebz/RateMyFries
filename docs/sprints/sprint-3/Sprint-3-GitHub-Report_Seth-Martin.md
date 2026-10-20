# Sprint 3 GitHub Report - Seth Martin

- **Repository:** [JoeBeebz/RateMyFries](https://github.com/JoeBeebz/RateMyFries)
- **Student / GitHub author:** Seth Martin / `SethMart1`
- **Sprint:** FRY Sprint 3, scheduled October 20-November 3, 2026
- **Reporting cutoff:** October 20, 2026 at 02:10:47 CDT (`2026-10-20T07:10:47Z`)
- **Cutoff revision:** [`5e0fedf387a9fe2b4b95a4e725c2c0ea553fd352`](https://github.com/JoeBeebz/RateMyFries/commit/5e0fedf387a9fe2b4b95a4e725c2c0ea553fd352)
- **Report type:** In-progress snapshot. Later report/static-analysis commits and future review/merge activity are outside this explicit cutoff.

## PRs Merged During the Sprint

**No PRs were merged during the reporting period.** The required merged-only list is empty; therefore there are no merged PR titles, authors, reviewers or merge dates to list.

Verified query:

```text
repo:JoeBeebz/RateMyFries is:pr is:merged author:SethMart1 merged:2026-10-20..2026-11-03
```

[Run the merged-only search](https://github.com/JoeBeebz/RateMyFries/pulls?q=is%3Apr+is%3Amerged+author%3ASethMart1+merged%3A2026-10-20..2026-11-03).

Open PRs, closed-but-unmerged PRs and direct pushes to main are not counted as merged delivery. The implementation submission is awaiting the repository's required approving review, so it has not been included in the merged-PR list or Jira Done totals.

## Commit Activity

| Metric | Value |
| --- | --- |
| Total authored sprint commits through the cutoff | **13** |
| Commits included in merged sprint PRs | **0** |
| Direct pushes to main during this work | **0** |
| Date of first commit | October 20, 2026 at 01:59:54 CDT |
| Date of last commit at cutoff | October 20, 2026 at 02:10:47 CDT |
| Date range | **October 20, 2026 - October 20, 2026** |
| Author | SethMart1 |

The 13 commits are on `feature/sprint-3-discovery-and-business-moderation`, after the pre-sprint main revision `8c94203f8925febc66ce18f8ddb0fbcc1bdae245`. Twelve implement/test/document the new scope and relocate Sprint 2 artifacts; the thirteenth submits the Jira report. These are actual GitHub commits, not local-only commits. They are activity, not accepted merged delivery.

Evidence: [branch commit history](https://github.com/JoeBeebz/RateMyFries/commits/feature/sprint-3-discovery-and-business-moderation/) and [cutoff tree](https://github.com/JoeBeebz/RateMyFries/tree/5e0fedf387a9fe2b4b95a4e725c2c0ea553fd352).

Reproduction against the captured cutoff:

```text
git rev-list --count 8c94203f8925febc66ce18f8ddb0fbcc1bdae245..5e0fedf387a9fe2b4b95a4e725c2c0ea553fd352
git log --reverse --format="%H %cI %an" 8c94203f8925febc66ce18f8ddb0fbcc1bdae245..5e0fedf387a9fe2b4b95a4e725c2c0ea553fd352
```

## Validation and Submission Status

The submitted implementation passed 47 isolated integration/regression tests and JavaScript syntax validation. Desktop/mobile search layout and missing-key fallback were inspected in browser. Google credential-dependent live checks remain unfinished; all details and Jira mapping are in [IMPLEMENTATION.md](../../../IMPLEMENTATION.md).

This file is submitted through the same feature-branch PR workflow. No repository review requirement has been bypassed and no unmerged work is represented as merged. The final report must be refreshed after approval/merge or sprint closure if a completed-sprint submission is required.
