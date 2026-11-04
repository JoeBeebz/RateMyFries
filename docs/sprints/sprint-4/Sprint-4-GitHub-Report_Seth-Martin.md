# Sprint 4 GitHub Report - Seth Martin

**Student:** Seth Martin | **Project:** Rate My Fries (FRY) | **GitHub:** SethMart1.

**Repository:** https://github.com/JoeBeebz/RateMyFries

**Verified snapshot:** November 3, 2026, 10:57:35 p.m. CST (November 4, 04:57:35 UTC). PRs were being merged during this refresh; all statuses and counts below apply to this fixed snapshot.

**Merged-main cutoff:** `a5b525fa60167a9b35c6d2b14ba7cd79fd0db951`. **Sprint 4 baseline:** `7ad236428b0f6cc9fce55f5fb2bac43cf2eafaa0`, the final prior Sprint 3 merge. Sprint 4 is the project owner's submission label; historical Sprint 3 reports remain preserved.

## Sprint 4 merged delivery

| PR | Work | Review | Merge time (Chicago) |
| --- | --- | --- | --- |
| [#11](https://github.com/JoeBeebz/RateMyFries/pull/11) | FRY-59: private EC2 development migration | JoeBeebz - Approved | Nov 3, 10:55:59 p.m. CST |
| [#7](https://github.com/JoeBeebz/RateMyFries/pull/7) | FRY-56: Google address suggestions on class HTTP site | JoeBeebz - Approved | Nov 3, 10:57:20 p.m. CST |

Both PRs are closed with merged=true and have merge timestamps. Their heads are ancestors of the fetched main cutoff. PR #11 contributes three work commits; PR #7 contributes two. The two merge commits have Git author JoeBeebz. Approval is tracked separately from the actual merge event.

PR #11's merge event is 2026-11-04T04:55:59Z; its merge commit timestamp is one second earlier. PR #7's event is 2026-11-04T04:57:20Z. The latest recorded teammate approvals were #11 at 04:52:17Z and #7 at 04:54:24Z on November 4 (both November 3 in Chicago).

## Commit activity

| Metric | Sprint 4 since baseline | Cumulative including prior Sprint 3 |
| --- | --- | --- |
| Seth-authored work commits (non-merge) | 5 | 28 |
| Merge commits | 2 | 5 |
| Total commits on main | 7 | 33 |
| Verified merged PRs | 2 (#7, #11) | 5 (#4, #5, #6, #7, #11) |

The five Sprint 4 work commits all use Git author Seth Martin, with author timestamps on November 3 from 1:53:37 a.m. to 9:49:06 p.m. CST. They are distinct commits reachable from main after the baseline. Pending PR commits and this report's submission are excluded. Shared PR ancestry is not summed twice.

The previous Sprint 3 baseline contributes 23 work commits and three merge commits, delivered through #4, #5 and #6 on October 20. Their historic titles and dates remain unchanged; those 26 commits are not presented as new Sprint 4 delivery. The cumulative range starts at `8c94203f8925febc66ce18f8ddb0fbcc1bdae245`.

## Work still awaiting merge at the snapshot

| PR | Work | Target | Review |
| --- | --- | --- | --- |
| [#8](https://github.com/JoeBeebz/RateMyFries/pull/8) | FRY-57: verified restaurants, fry menus and photos | main | No submitted reviews |
| [#9](https://github.com/JoeBeebz/RateMyFries/pull/9) | FRY-58: catalogue autofill and exact listed matches | main | No submitted reviews |
| [#10](https://github.com/JoeBeebz/RateMyFries/pull/10) | FRY-40/44: mobile contrast and page response time | feature/FRY-56-google-live-acceptance | No submitted reviews |
| [#12](https://github.com/JoeBeebz/RateMyFries/pull/12) | Sprint 4 reports and demo video | main | No submitted reviews |

Three implementation PRs remain open and unmerged: #8, #9 and #10. The report/demo PR #12 is separately open. No later merge or review is inferred. #10 is still stacked on the now-merged #7 branch; it needs retargeting to main, reconciliation/testing with #9, and teammate approval before merge. This reporting task does not perform those implementation merges.

## Deployment, validation and acceptance limits

The previously tested class runtime `d094cd8e52b1dcf413ed1a36209a367abe525262` combines #7/#9/#10 changes. The catalogue database was populated separately. The same runtime was copied to the private EC2 server; it was left stopped after acceptance, and the personal deployment was preserved. Those deployment observations are separate from the GitHub merge counts above. Only #7 and #11 are newly verified in main at this cutoff.

The earlier analysis-only source combination passed 72 Python tests and 12 JavaScript checks. It combined the deployed runtime, catalogue revision `bb9673abc28c0a0060d6292facdc77363a69145b`, and infrastructure revision `d7b7bf5ed9ffa6c6562f91223609e65a0635c1c9`. This is not a fresh test or static scan of the merged main cutoff. No application tests were rerun for this report-only edit.

The existing SonarQube vulnerability and three Trivy infrastructure findings remain documented; merging does not resolve them. Device-position acceptance, initial collaborator sign-ins and Jira completion are not inferred from a GitHub merge. Jira and the static-analysis reports were not edited during this GitHub report refresh.

## Reproduce the Sprint 4 counts

```powershell
git fetch origin
git rev-list --count --no-merges 7ad2364..a5b525f
git rev-list --count --merges 7ad2364..a5b525f
git rev-list --count 7ad2364..a5b525f
```

Expected counts are 5 work commits, 2 merge commits and 7 total. Use the full cutoff hashes above if a short hash becomes ambiguous. Cumulative counts from 8c94203 to a5b525f are 28, 5 and 33 respectively.

## Evidence

- [Sprint 4 main comparison](https://github.com/JoeBeebz/RateMyFries/compare/7ad236428b0f6cc9fce55f5fb2bac43cf2eafaa0...a5b525fa60167a9b35c6d2b14ba7cd79fd0db951).
- [Merged PR #7 commits](https://github.com/JoeBeebz/RateMyFries/pull/7/commits) and [merged PR #11 commits](https://github.com/JoeBeebz/RateMyFries/pull/11/commits).
- Current PR states, merge timestamps and approval responses: static-analysis/raw/2026-11-03/github-refresh-045735Z.json. The included review responses were fetched before the merges; their exact submission timestamps are retained.
- Reachable commit IDs, author dates and messages: static-analysis/raw/2026-11-03/merged-main-commits-045735Z.txt. Earlier snapshots and scanner evidence remain preserved.
