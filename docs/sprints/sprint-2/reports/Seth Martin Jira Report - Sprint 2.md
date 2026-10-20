# Seth Martin Jira Report - Sprint 2

- **Jira project:** [Crispy Team (FRY)](https://ratemyfries.atlassian.net/browse/FRY)
- **Sprint name/number:** Sprint 2 — Rate My Fries backlog implementation
- **Reporting dates:** September 15–October 9, 2026
- **Student:** Seth Martin
- **Report date:** October 9, 2026

## Sprint Scope

Sprint 2 is intended to contain all of the Rate My Fries backlog implementation work. Seth Martin confirmed that the Jira sprint setup was incorrect: the implementation issues remained in the backlog instead of being grouped into Sprint 2. Jira currently records FRY Sprint 0 and an empty FRY Sprint 1; it does not provide a configured Sprint 2 with a starting commitment or closure history.

The intended implementation scope comprises **29 stories and 9 subtasks (38 issues)**: FRY-6 through FRY-13 and FRY-15 through FRY-44. This includes accounts, profiles, restaurant and fry discovery, ratings, reviews, navigation, forms, persistence, security, responsive design, and performance. [Merged PR #2](https://github.com/JoeBeebz/RateMyFries/pull/2) connects this work to Seth's contribution. The setup and placeholder issues FRY-1, FRY-3, FRY-4, FRY-5, and FRY-14 are outside this implementation scope.

## Sprint Commitment vs Delivery

| Metric | Count |
| --- | ---: |
| Issues committed at sprint start | N/A — no recorded Sprint 2 starting commitment |
| Issues completed | 36 |
| Issues not completed | 2 |
| Issues added mid-sprint | N/A — no recorded Sprint 2 membership history |

Delivery counts reflect the intended 38-issue scope and Jira statuses at the report date. They do not reconstruct an undocumented sprint-start commitment. Parent stories and their subtasks are counted as separate Jira issues.

| Scope group | Issue keys | Done | In Progress |
| --- | --- | ---: | ---: |
| Account and profile stories | FRY-6, FRY-11, FRY-15 | 3 | 0 |
| Account and profile subtasks | FRY-7–10, FRY-12–13, FRY-16–18 | 9 | 0 |
| Remaining implementation stories | FRY-19–44 | 24 | 2 |
| **Total** | **38 issues** | **36** | **2** |

The two incomplete issues are [FRY-40 — Use a consistent interface on desktop and mobile](https://ratemyfries.atlassian.net/browse/FRY-40) and [FRY-44 — Load normal pages within an agreed performance target](https://ratemyfries.atlassian.net/browse/FRY-44). Both remain In Progress.

## Issue Breakdown by Type

| Type | To Do | In Progress | Done |
| --- | ---: | ---: | ---: |
| Story | 0 | 2 | 27 |
| Task | 0 | 0 | 0 |
| Bug | 0 | 0 | 0 |
| Subtask | 0 | 0 | 9 |
| **Total** | **0** | **2** | **36** |

## Per-Student Work Allocation

| Student | Issues Assigned | Issues Completed |
| --- | --- | --- |
| Seth Martin | 0 recorded in Jira | 36 Done issues in the intended implementation scope |

All 38 issues are currently Unassigned in Jira. The completed-work figure describes the implementation scope attributed to Seth through his six commits in [PR #2](https://github.com/JoeBeebz/RateMyFries/pull/2/commits), rather than a Jira assignee query. Seth is the sole student included in this report.

## Estimation & Accuracy

| Metric | Value |
| --- | --- |
| Total story points committed | N/A — no recorded Sprint 2 commitment or point baseline |
| Total story points completed | N/A — no Sprint 2 point total available |
| Completion % | N/A by story points; **94.7% by issue count (36 / 38)** |

Missing sprint membership and estimation records prevent a comparison of committed and completed story points. Issue-count completion includes both stories and subtasks and is not a velocity measurement.

## Workflow Discipline

- [x] Issues moved through workflow states (To Do → In Progress → Done).
- [ ] Issues closed only after acceptance criteria met.
- [ ] Sprint completed/closed in Jira.

[FRY-6's History tab](https://ratemyfries.atlassian.net/browse/FRY-6) records To Do → In Progress on October 5, followed by In Review, then Done on October 6. PR #2 describes automated tests and manual validation, but the available evidence does not establish acceptance verification for every closed issue. Sprint 2 was not configured or closed in Jira.

## Blockers & Scope Changes

- **Major blockers:** FRY-40 still requires the browser/device and contrast validation described in PR #2. FRY-44 requires an agreed performance target and measured load results.
- **Scope correction:** All backlog implementation work belongs to Sprint 2. Incorrect Jira sprint setup left these issues outside their intended sprint, so formal starting-commitment and mid-sprint scope-change counts are unavailable.
- **Spillover:** FRY-40 and FRY-44 remain In Progress because their remaining validation is incomplete. No formal rollover to a subsequent Jira sprint is recorded.

## Jira Evidence Links (No Screenshots)

- [Sprint report — project burndown](https://ratemyfries.atlassian.net/jira/software/projects/FRY/boards/1/reports/burndown?source=overview): the available report covers FRY Sprint 0. A Sprint 2 report is unavailable because Sprint 2 was not configured.
- [Project backlog](https://ratemyfries.atlassian.net/jira/software/projects/FRY/boards/1/backlog): contains the implementation issues intended for Sprint 2.
- [Project board](https://ratemyfries.atlassian.net/jira/software/projects/FRY/boards/1): a board filtered to Sprint 2 is unavailable because that sprint was not configured.
- [Intended Sprint 2 implementation scope — filtered Jira issue list](https://ratemyfries.atlassian.net/issues/?jql=project%20%3D%20FRY%20AND%20key%20NOT%20IN%20%28FRY-1%2C%20FRY-3%2C%20FRY-4%2C%20FRY-5%2C%20FRY-14%29%20ORDER%20BY%20key%20ASC).
- Supporting records: [FRY-6](https://ratemyfries.atlassian.net/browse/FRY-6), [FRY-40](https://ratemyfries.atlassian.net/browse/FRY-40), [FRY-44](https://ratemyfries.atlassian.net/browse/FRY-44), and [merged implementation PR #2](https://github.com/JoeBeebz/RateMyFries/pull/2).
