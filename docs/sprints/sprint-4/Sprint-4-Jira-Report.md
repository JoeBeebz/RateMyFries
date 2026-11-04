# Sprint 4 Jira Report - Seth Martin

**Student:** Seth Martin | **Project:** Rate My Fries (FRY) | **Submission:** Sprint 4.

**Report date:** November 3, 2026. Snapshot verified from live Jira/GitHub; times use America/Chicago. October 20 was CDT (UTC-05:00); November 3 is CST (UTC-06:00).

**Reporting scope:** Sprint 4 is the owner-confirmed submission label. The underlying Jira record still uses FRY Sprint 3 (ID 3), October 20-November 3, 2026. Its recorded scope and the prior merged work are retained as context; this report does not invent a separate Sprint 4 commitment or change Jira history.

## Recorded Jira commitment versus delivery

| Metric | Verified value |
| --- | --- |
| Original committed issues | 12 |
| Issues Done | 10 |
| Issues not Done | 2 |
| Issues added after sprint start | 0 |
| Committed story points | 46 |
| Completed story points | 36 |
| Point completion | 36/46 = 78.26% |
| Issue completion | 10/12 = 83.33% |
| Sprint closure | Still active; Complete sprint control remains available |

The Jira burndown selected FRY Sprint 3 and Story points, displayed the scheduled October 20-November 3 dates, and reported no scope changes. Its completed and incomplete tables agree with the 12-issue navigator query. These are observed Done totals at this snapshot, not a claim that the sprint was formally closed.

## Issue breakdown by type and status

| Type | To Do | In Progress | In Review | Done |
| --- | --- | --- | --- | --- |
| Story | 0 | 1 | 1 | 10 |
| Task | 0 | 0 | 0 | 0 |
| Bug | 0 | 0 | 0 | 0 |

## Stories in the recorded Jira scope

| Issue | Story | Points | Jira status |
| --- | --- | --- | --- |
| [FRY-45](https://ratemyfries.atlassian.net/browse/FRY-45) | Unify restaurant and fry search in one menu | 5 | Done |
| [FRY-46](https://ratemyfries.atlassian.net/browse/FRY-46) | Find current and nearby locations with Google location services | 5 | In Progress |
| [FRY-47](https://ratemyfries.atlassian.net/browse/FRY-47) | Support administrator and regular user account roles | 3 | Done |
| [FRY-48](https://ratemyfries.atlassian.net/browse/FRY-48) | Review regular-user business submissions before publishing | 5 | Done |
| [FRY-49](https://ratemyfries.atlassian.net/browse/FRY-49) | Provide a business submission form for regular users | 3 | Done |
| [FRY-50](https://ratemyfries.atlassian.net/browse/FRY-50) | Store a private optional profile address for nearby discovery | 3 | Done |
| [FRY-51](https://ratemyfries.atlassian.net/browse/FRY-51) | Search nearby fries using an address instead of latitude and longitude | 3 | Done |
| [FRY-52](https://ratemyfries.atlassian.net/browse/FRY-52) | Import Kenosha businesses from Google business data | 3 | Done |
| [FRY-53](https://ratemyfries.atlassian.net/browse/FRY-53) | Restrict direct store creation to administrators | 3 | Done |
| [FRY-54](https://ratemyfries.atlassian.net/browse/FRY-54) | Provide an administrator inbox for business requests | 3 | Done |
| [FRY-55](https://ratemyfries.atlassian.net/browse/FRY-55) | Allow only existing administrators to create administrator accounts | 5 | Done |
| [FRY-56](https://ratemyfries.atlassian.net/browse/FRY-56) | Autocomplete address inputs using Google location services | 5 | In Review |

## Per-student allocation and estimation

| Student | Assigned committed issues | Done issues | Done points |
| --- | --- | --- | --- |
| Seth Martin | 12 | 10 | 36 |

The committed 46 points have not changed. Five points remain In Progress and five In Review. Point completion improved from 0/46 in the October 20 snapshot to 36/46; ten issues advanced to Done. No time-spent accuracy or team velocity estimate is invented because reliable actual-effort data and a closed sprint are unavailable. No extra backlog work is added to these totals.

## Workflow discipline and remaining acceptance

- [x] Jira records the original stories progressing from initial In Progress/In Review to ten Done outcomes; representative issue links and the prior committed report retain the progression evidence.
- [x] The base implementation PR #4 is merged with teammate approval; account, moderation and search regression checks and live Google address/import acceptance were completed.
- [ ] All committed acceptance is finished: FRY-46 still needs a successful real device-position result, and FRY-56 still needs the follow-up PR #7 approval/merge.
- [ ] Sprint closed in Jira: it remains active; this report does not close or roll over issues.

FRY-46's authorized device-location attempt returned no position. The LAN HTTP origin limitation and late-callback handling were addressed in test code, and the address-entry fallback works. Successful real-device location remains unverified. FRY-56's class HTTP initialization/accessibility fix works in the test deployment but remains unmerged. Do not equate that deployment with approved main delivery.

## Additional work outside the original sprint commitment

| Issue | Work | Current status |
| --- | --- | --- |
| [FRY-40](https://ratemyfries.atlassian.net/browse/FRY-40) | Use a consistent interface on desktop and mobile | In Review |
| [FRY-44](https://ratemyfries.atlassian.net/browse/FRY-44) | Load normal pages within an agreed performance target | In Review |
| [FRY-57](https://ratemyfries.atlassian.net/browse/FRY-57) | Expand Kenosha restaurant catalogue with verified fry menus and photos | In Review |
| [FRY-58](https://ratemyfries.atlassian.net/browse/FRY-58) | Autofill catalogue search and return only exact listed matches | In Review |
| [FRY-59](https://ratemyfries.atlassian.net/browse/FRY-59) | Migrate Fry from the personal server to a private EC2 development instance | In Review |

FRY-40/44 are older backlog quality items. FRY-57/58/59 are new catalogue, autofill and private-migration stories created before their implementations. None appears in the Sprint 3 scope query, so their points and completion are excluded from the recorded scope totals. FRY-3, FRY-5 and FRY-14 were closed with the owner's explanation that they were obsolete setup placeholders; those closures are not implementation delivery. The requested unused-EC2 cleanup had no Jira story and is excluded from these metrics.

The private migration preserved the personal server and copied the actual deployed application, 16 restaurants and 37 fry listings. It was left stopped after reboot/private-access acceptance. Individual first sign-ins/password choices, PR review and the new infrastructure scan findings remain open for FRY-59. No AWS account names, passwords or sign-in details are included here.

## Validation and static review

An analysis-only combination of the deployed application and pending catalogue/EC2 files passed 72 Python tests and 12 JavaScript checks. This is separate from merged-main acceptance. SonarQube reports 0 bugs, 1 vulnerability, 0 code smells and 0 security hotspots. Trivy reports 0 dependency vulnerabilities, 3 infrastructure misconfigurations and 0 secrets. The four tool findings remain visible; no suppressions, source fixes or live AWS permission/network changes were made for this reporting task. See the separate static-analysis reports for severity, scope and review recommendations.

## Jira evidence links (no screenshots)

- [Sprint 3 burndown and commitment](https://ratemyfries.atlassian.net/jira/software/projects/FRY/boards/1/reports/burndown?source=overview) - select FRY Sprint 3 and Story points if Jira remembers another choice.
- [Sprint 3 issue scope](https://ratemyfries.atlassian.net/issues/?jql=project%20%3D%20FRY%20AND%20sprint%20%3D%203%20ORDER%20BY%20key%20ASC).
- [Active board and workflow](https://ratemyfries.atlassian.net/jira/software/projects/FRY/boards/1).
- [Backlog](https://ratemyfries.atlassian.net/jira/software/projects/FRY/boards/1/backlog).
- [Merged implementation PR #4](https://github.com/JoeBeebz/RateMyFries/pull/4), [address follow-up PR #7](https://github.com/JoeBeebz/RateMyFries/pull/7), [quality PR #10](https://github.com/JoeBeebz/RateMyFries/pull/10), [private migration PR #11](https://github.com/JoeBeebz/RateMyFries/pull/11).

The prior October 20 Sprint 3 report remains in its original repository folder. This snapshot supersedes its no-Google-configuration blocker and 0 Done totals; it preserves the unresolved device-location and review distinctions.
