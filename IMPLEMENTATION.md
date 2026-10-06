# Implementation and acceptance record

## Scope

Initial implementation for the 29 app stories in the FRY backlog. All requirement
IDs R1–R130 map to the story descriptions already in Jira. The repository's two
additional search requirements (distance and price) are included as well.
Assignment-report generation is not part of this change.

## Story mapping

| Jira | Feature | Evidence |
|---|---|---|
| FRY-6 | Account registration | Duplicate/invalid-account tests; live Edge registration |
| FRY-11 | Login and logout | Session-revocation, login-error and throttle tests |
| FRY-15 | Profile and history | Profile-edit/uniqueness and per-user history tests |
| FRY-19 | Delete account | Password/confirmation check; cascading deletion tests |
| FRY-20 | Browse restaurants | List, name/location, alphabetical-sort tests |
| FRY-21 | Restaurant details | Stored averages, all associated written reviews; live detail view |
| FRY-22 | Add restaurants | Normalized duplicate detection and invalid data tests |
| FRY-23 | Fry information | Style, seasoning, optional price, description/image validation |
| FRY-24 | Submit rating | Authentication, 1–5 validation and uniqueness tests |
| FRY-25 | Change/remove rating | Update-in-place, removal and average-recalculation tests |
| FRY-26 | Averages/counts | Multiple-user averages, count and unrated state tests |
| FRY-27 | Write reviews | Text/range/length validation and live Edge submission |
| FRY-28 | Read reviews | Newest-first ordering, author/date/context display tests |
| FRY-29 | Edit reviews | Identity/ownership, update-in-place and text preservation tests |
| FRY-30 | Delete reviews | Confirmation/cancellation/ownership and database deletion tests |
| FRY-31 | Detailed fry qualities | All seven scores and optional-score validation tests |
| FRY-32 | Quality averages | Missing-score exclusion and averaging tests |
| FRY-33 | Dining context | Validated dine-in/takeout/delivery values; live Edge selection |
| FRY-34 | Restaurant search | Matching and no-results tests |
| FRY-35 | Rating filters/sorts | Minimum-rating and ascending/descending-sort tests |
| FRY-36 | Fry search/filter | Fry type/style/price tests |
| FRY-37 | Homepage | Recent reviews, high-rated fries, navigation and account-state views |
| FRY-38 | Navigation | Shared base layout; live Edge traversal between major pages |
| FRY-39 | Forms | Required fields, server errors, draft preservation and input tests |
| FRY-40 | Responsive/cross-browser UI | Responsive CSS implemented; full agreed browser/contrast matrix still pending |
| FRY-41 | Persistence/relationships | Restarted-app read, foreign-key and cascade tests |
| FRY-42 | Safe errors | Missing pages and simulated database-failure tests |
| FRY-43 | Protected operations | Server identity/ownership enforcement; CSRF and revoked-session tests |
| FRY-44 | Performance | Not accepted yet: agree load target and representative dataset/network/device, then measure |

## Automated validation

`python -m pytest -q`: 38 passing tests on Python 3.11, Windows.
Coverage includes real SQLite constraints, cross-user requests, session revocation,
CSRF rejection, restart persistence, invalid inputs, escaping, aggregate updates,
search filters, and deletion policy. Tests use temporary data.

Live Edge verification also passed registration, profile display, restaurant/fry
browsing, review submission, editing without increasing the rating count, and the
delete-confirmation page. At a 390px viewport the fry detail page had no horizontal
overflow. The local test account/review is explicitly labeled demo data and is
excluded from source uploads along with the entire `instance/` directory.

## Review status

Functional stories are implementation-ready for team review. FRY-40 and FRY-44
remain unfinished acceptance work; neither a multi-browser pass nor a performance
target is claimed. Public deployment has not been performed.

## Manual review checklist

- Start with the README, create two accounts, add a restaurant and fry option.
- Submit/edit a review, verify the profile/history and restaurant/fry averages.
- Attempt another user's protected operations and confirm rejection.
- Confirm/cancel deletion, then verify averages and data persistence after restart.
- Check the full agreed browser matrix, keyboard navigation, narrow-screen layouts,
  and text contrast before accepting FRY-40.
- Agree a concrete page-load threshold, representative data volume and environment;
  record measured results before accepting FRY-44.
