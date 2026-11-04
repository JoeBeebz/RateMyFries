# Sprint 4 GitHub Report - Seth Martin

**Student:** Seth Martin | **Project:** Rate My Fries (FRY) | **Submission:** Sprint 4.

**Report date:** November 3, 2026. GitHub status and submitted reviews rechecked November 3, 2026, 10:55:37 p.m. CST (November 4, 04:55:37 UTC); earlier Jira evidence is retained; times use America/Chicago. October 20 was CDT (UTC-05:00); November 3 is CST (UTC-06:00).

**Reporting scope:** Sprint 4 is the owner-confirmed submission label. The underlying Jira record still uses FRY Sprint 3 (ID 3), October 20-November 3, 2026. Its recorded scope and the prior merged work are retained as context; this report does not invent a separate Sprint 4 commitment or change Jira history.

**Repository:** https://github.com/JoeBeebz/RateMyFries | **GitHub account:** SethMart1.

**Merged-main cutoff:** `7ad236428b0f6cc9fce55f5fb2bac43cf2eafaa0`. The latest main merge was October 20, 2026, 10:24:01 p.m. CDT. A fresh fetch and live GitHub PR/review responses confirm that main has not advanced. Current PR states and review timestamps are retained in github-review-refresh.json; the earlier github-snapshot.json remains preserved. The report submission PR #12 is listed separately and excluded from implementation delivery counts.

## Prior merged work: Sprint 3 baseline

| PR | Title | Author | Reviewer | Merge time (Chicago) |
| --- | --- | --- | --- | --- |
| [#4](https://github.com/JoeBeebz/RateMyFries/pull/4) | Sprint 3: unified discovery and moderated business listings | SethMart1 | JoeBeebz - Approved | Oct 20, 2026 07:13:44 PM CDT |
| [#5](https://github.com/JoeBeebz/RateMyFries/pull/5) | Sprint 3 demo video | SethMart1 | JoeBeebz - Approved | Oct 20, 2026 10:05:16 PM CDT |
| [#6](https://github.com/JoeBeebz/RateMyFries/pull/6) | Replace Sprint 3 GitHub report with merged PR evidence | SethMart1 | JoeBeebz - Approved | Oct 20, 2026 10:24:01 PM CDT |

All three PRs were approved by JoeBeebz and merged by JoeBeebz. PR #4 delivered unified discovery, Google integration code, account roles, private addresses and moderated businesses, plus tests and initial reporting. PR #5 added the demo. PR #6 refreshed the earlier GitHub report. Live Google acceptance happened later during configuration and is not inferred from merge status alone.

Exact merge-event UTC times: #4 - 2026-10-21 00:13:44Z; #5 - 2026-10-21 03:05:16Z; #6 - 2026-10-21 03:24:01Z. A merge commit's author timestamp can differ from the PR merge event by a second.

## Commit activity in the prior merged baseline

| Metric | Verified value |
| --- | --- |
| Seth-authored work commits included in the prior merged PRs | 23 |
| PR #4 work commits | 21 |
| PR #5 work commits | 1 |
| PR #6 work commits | 1 |
| Merge commits authored by JoeBeebz | 3 |
| Prior baseline main commits including merges | 26 |
| Direct-to-main work counted in this baseline | 0 |
| First work commit | 644f748 - Oct 20, 2026, 01:59:54 a.m. CDT |
| Last work commit | 388cf2c - Oct 20, 2026, 10:10:23 p.m. CDT |
| Work-commit date range | October 20-October 20, 2026 |

Counts cover `8c94203f8925febc66ce18f8ddb0fbcc1bdae245` (main before the Sprint 3 baseline) through the cutoff. The 23 work commits use the Git author names SethMart1 and Seth Martin for the same student's contribution. The three merge commits are separate. Open PR commits, local integration merges and this report submission are not added to accepted delivery.

## Current Sprint 4 delivery status

| Metric | Verified value at refresh |
| --- | --- |
| Implementation PRs checked (#7-#11) | 5 |
| Implementation PRs merged into main | 0 |
| Implementation PRs still open | 5 |
| Open implementation PRs with teammate approval | 2 (#7 and #11) |
| Open implementation PRs without submitted reviews | 3 (#8, #9 and #10) |
| Report/demo submission PR #12 | Open; no submitted reviews |

Approval and merging are separate GitHub steps. JoeBeebz has approved #7 and #11; both still have null merged_at and remain open. GitHub's merge_commit_sha field can identify a proposed test merge while a PR is open, so that field alone is not merge evidence.

## Implementation PRs awaiting merge

| PR | Work | Target | Head revision | Review |
| --- | --- | --- | --- | --- |
| [#7](https://github.com/JoeBeebz/RateMyFries/pull/7) | FRY-56: restore Google address suggestions on the class HTTP site | main | 3068d83 | JoeBeebz - Approved |
| [#8](https://github.com/JoeBeebz/RateMyFries/pull/8) | FRY-57: populate verified local restaurants, fry menus and photos | main | bb9673a | No submitted reviews |
| [#9](https://github.com/JoeBeebz/RateMyFries/pull/9) | FRY-58: autofill catalogue search with exact listed matches | main | be7e01b | No submitted reviews |
| [#10](https://github.com/JoeBeebz/RateMyFries/pull/10) | FRY-40 FRY-44: improve mobile contrast and live discovery response time | feature/FRY-56-google-live-acceptance | dea72e4 | No submitted reviews |
| [#11](https://github.com/JoeBeebz/RateMyFries/pull/11) | FRY-59: migrate Fry to a private EC2 development server | main | d7b7bf5 | JoeBeebz - Approved |

No newer implementation merges are verified after the October 20 cutoff. All five implementation PRs remain open and unmerged. The latest approval on #7 was submitted by JoeBeebz on November 3 at 10:54:24 p.m. CST (04:54:24Z November 4); #11 was approved at 10:52:17 p.m. CST (04:52:17Z November 4). #8, #9 and #10 have no submitted reviews. #7 restores address suggestions; #8 supplies reproducible catalogue content; #9 adds generic prefix autofill and exact listed-name search; #10 covers mobile contrast, concurrency/performance and location fallback; #11 supplies private EC2 infrastructure and migration tooling.

PR #10 is stacked on #7 and targets its feature branch. Complete the approved merge of #7 first, then retarget #10 to main and reconcile/retest it with #9 before its approved merge. PR commit lists can share ancestry, so summing their commit counts would double-count work. Pending work is visible here without being included in the 23 merged work commits.

## Report and demo submission

[PR #12](https://github.com/JoeBeebz/RateMyFries/pull/12), "Sprint 4: Jira, GitHub, SonarQube/Trivy reports and demo video", remains open against main with no submitted reviews. At the refresh snapshot its head is 7859f31f9b846c86ffa0befb9a13ac0ab4c8833d. This follow-up report edit is excluded from the fixed activity counts. The Sprint 4 files and video currently exist on that PR branch; their main-branch links become available after its merge.

## Deployment versus main

The class test application at `d094cd8e52b1dcf413ed1a36209a367abe525262` combines pending runtime changes from #7/#9/#10. The catalogue database was populated separately. The same runtime was copied to the private EC2 test server. These deployments preserve existing data and demonstrate behavior; they do not merge the open PRs or replace teammate review. The EC2 instance was left stopped after acceptance and the personal deployment was preserved.

The reporting scan uses a documented, analysis-only combination of that runtime plus catalogue source `bb9673abc28c0a0060d6292facdc77363a69145b` and infrastructure source `d7b7bf5ed9ffa6c6562f91223609e65a0635c1c9`. It is not represented as a GitHub merged revision. The source-file SHA-256 manifest is retained with the static-analysis evidence. Its 72 Python and 12 JavaScript passing checks do not automatically approve the PRs. Four scanner findings remain for review, including the pending infrastructure permissions/network settings.

## Reproduce the counts

```powershell
git fetch origin
git rev-list --count --no-merges 8c94203f8925febc66ce18f8ddb0fbcc1bdae245..7ad236428b0f6cc9fce55f5fb2bac43cf2eafaa0
git rev-list --count --merges 8c94203f8925febc66ce18f8ddb0fbcc1bdae245..7ad236428b0f6cc9fce55f5fb2bac43cf2eafaa0
git rev-list --count 8c94203f8925febc66ce18f8ddb0fbcc1bdae245..7ad236428b0f6cc9fce55f5fb2bac43cf2eafaa0
```

Expected counts are 23, 3 and 26. Merged-only query:

```text
repo:JoeBeebz/RateMyFries is:pr is:merged author:SethMart1 merged:2026-10-20..2026-11-03
```

## Evidence

- [Exact main comparison](https://github.com/JoeBeebz/RateMyFries/compare/8c94203f8925febc66ce18f8ddb0fbcc1bdae245...7ad236428b0f6cc9fce55f5fb2bac43cf2eafaa0).
- [PR #4 commits](https://github.com/JoeBeebz/RateMyFries/pull/4/commits), [PR #5 commits](https://github.com/JoeBeebz/RateMyFries/pull/5/commits), [PR #6 commits](https://github.com/JoeBeebz/RateMyFries/pull/6/commits).
- Current PR/review responses are preserved in static-analysis/raw/2026-11-03/github-review-refresh.json. The original GitHub PR and review responses, issue snapshots, source hashes, tool JSON and logs remain alongside that new snapshot. No screenshots or unverifiable reviewer/merge claims are substituted for those records.
