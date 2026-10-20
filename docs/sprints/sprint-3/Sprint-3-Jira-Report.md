# Sprint 3 Jira Report

- **Project:** [Crispy Team (FRY)](https://ratemyfries.atlassian.net/browse/FRY)
- **Sprint:** FRY Sprint 3, Jira sprint ID 3
- **Scheduled dates:** October 20-November 3, 2026 (America/Chicago)
- **Snapshot date:** October 20, 2026; this is an in-progress sprint report, not a claimed completed sprint.
- **Student:** Seth Martin (`sethdmartin1000` in Jira; `SethMart1` on GitHub)
- **Implementation:** [PR #4](https://github.com/JoeBeebz/RateMyFries/pull/4)

## Sprint Commitment vs Delivery

| Metric | Count |
| --- | ---: |
| Issues committed at sprint start | 12 |
| Issues completed (Done) | 0 |
| Issues not completed | 12 |
| Issues added mid-sprint | 0 |

All 12 stories were created, assigned, estimated and added before the sprint was started on October 20. Jira's Sprint 3 burndown reports no scope changes and no completed issues. Eight stories are In Review; four are In Progress with live Google acceptance blockers. Implementation/test completion is not counted as Jira Done.

## Issue Breakdown by Type

| Type | To Do | In Progress | In Review | Done |
| --- | ---: | ---: | ---: | ---: |
| Story | 0 | 4 | 8 | 0 |
| Task | 0 | 0 | 0 | 0 |
| Bug | 0 | 0 | 0 | 0 |

An additional In Review column preserves the actual Jira workflow instead of misclassifying those eight stories as Done or In Progress.

| Issue | Story | Points | Exact Jira status |
| --- | --- | ---: | --- |
| [FRY-45](https://ratemyfries.atlassian.net/browse/FRY-45) | Unify restaurant and fry search | 5 | In Review |
| [FRY-46](https://ratemyfries.atlassian.net/browse/FRY-46) | Current and nearby Google location assistance | 5 | In Progress |
| [FRY-47](https://ratemyfries.atlassian.net/browse/FRY-47) | Admin and user roles | 3 | In Review |
| [FRY-48](https://ratemyfries.atlassian.net/browse/FRY-48) | Admin review before business publication | 5 | In Review |
| [FRY-49](https://ratemyfries.atlassian.net/browse/FRY-49) | Regular-user business submission form | 3 | In Review |
| [FRY-50](https://ratemyfries.atlassian.net/browse/FRY-50) | Private optional profile address | 3 | In Review |
| [FRY-51](https://ratemyfries.atlassian.net/browse/FRY-51) | Address-based nearby search | 3 | In Progress |
| [FRY-52](https://ratemyfries.atlassian.net/browse/FRY-52) | Google-sourced Kenosha businesses | 3 | In Progress |
| [FRY-53](https://ratemyfries.atlassian.net/browse/FRY-53) | Admin-only direct store creation | 3 | In Review |
| [FRY-54](https://ratemyfries.atlassian.net/browse/FRY-54) | Admin business-request inbox | 3 | In Review |
| [FRY-55](https://ratemyfries.atlassian.net/browse/FRY-55) | Admin-authorized administrator accounts | 5 | In Review |
| [FRY-56](https://ratemyfries.atlassian.net/browse/FRY-56) | Google address autocomplete | 5 | In Progress |

## Per-Student Work Allocation

| Student | Issues Assigned | Issues Completed |
| --- | ---: | ---: |
| Seth Martin | 12 | 0 |

All 12 assignments are recorded in Jira. PR #4 contains implementation work across all 12 stories; this is not a substitute for accepted/merged delivery.

## Estimation & Accuracy

| Metric | Value |
| --- | ---: |
| Total story points committed | 46 |
| Total story points completed | 0 |
| Completion % | 0% (0 / 46 points) |

Eight In Review stories represent 30 points. Four Google-dependent In Progress stories represent 16 points. No velocity or final estimation-accuracy claim is made while the sprint is active.

## Workflow Discipline

- [ ] Issues moved through workflow states (To Do -> In Progress -> Done).
- [ ] Issues closed only after acceptance criteria met.
- [ ] Sprint completed/closed in Jira.

The observed path is To Do -> In Progress for all 12, then In Review for eight. No issue was closed, so the full Done workflow and closure checklist are not claimed. The sprint remains active because required review/merge and live acceptance work remain.

## Blockers & Scope Changes

- **Review/merge:** GitHub requires at least one approving review. PR #4 is open and unmerged; it has not been counted as delivered work.
- **Google configuration:** Seth confirmed no Google Cloud project, API key or billing configuration exists. Code and mocked tests are present, but live autocomplete/geocoding and actual Google-sourced Kenosha import are not verified. No Google businesses, menu prices or ratings were invented.
- **API choice:** Places API (New) discovers third-party businesses; Google Business Profile APIs manage owned businesses. This implementation clarification is documented in FRY-52 and the repository.
- **First admin:** One-time trusted-operator bootstrap initializes an existing registered account; later promotions require an existing admin and record an audit entry.
- **Scope changes:** None after sprint start. Old placeholder/backlog issues and Sprint 2 spillover were not silently added to Sprint 3.
- **Potential spillover:** If review or Google setup is unavailable by the scheduled end, affected stories must remain unfinished or be moved through Jira's normal sprint-completion flow. No rollover has been claimed.

## Validation Evidence

48 isolated integration/regression tests passed against the final submitted application, including signed-CSRF forgery/cross-client/session-rotation checks; JavaScript syntax validation passed. Browser inspection verified the unified search on desktop and a 390px viewport with no horizontal overflow, plus the missing-key/manual-entry fallback. See [implementation mapping](../../../IMPLEMENTATION.md) for per-story checks and live-service limits.

## Jira Evidence Links (No Screenshots)

- [Sprint report: burndown, with FRY Sprint 3 selected](https://ratemyfries.atlassian.net/jira/software/projects/FRY/boards/1/reports/burndown?source=overview). Verified report heading: FRY Sprint 3; no scope changes and no completed issues. Select FRY Sprint 3 if Jira remembers another selection later.
- [Project backlog](https://ratemyfries.atlassian.net/jira/software/projects/FRY/boards/1/backlog).
- [Board routed to Sprint 3](https://ratemyfries.atlassian.net/secure/GHGoToBoard.jspa?sprintId=3).
- [Sprint 3 scope only: issue navigator](https://ratemyfries.atlassian.net/issues/?jql=project%20%3D%20FRY%20AND%20sprint%20%3D%203%20ORDER%20BY%20key%20ASC).


Final static-analysis evidence: [PDF folder](static-analysis/) contains the actual SonarQube dashboard/API export and converted Trivy summary. SonarQube reports 0 bugs, 0 vulnerabilities, 0 code smells, 0 security hotspots and a passing quality gate; Trivy reports 0 CRITICAL/HIGH/MEDIUM/LOW dependency vulnerabilities. The original CSRF/form findings were fixed and rescanned, without suppressions. These results do not remove the required PR approval/merge or missing Google live acceptance checks.
