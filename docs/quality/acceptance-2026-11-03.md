# FRY-40 / FRY-44 / FRY-46 acceptance evidence

## Agreed scope

On November 3, Seth approved normal page responses under **2 seconds** on the
class LAN, with **16 restaurants and 37 fry listings**, plus desktop / 390px
layout checks and WCAG AA text contrast. These targets were recorded in Jira
before implementation. The response target measures the complete HTML response;
third-party photo downloads and browser paint time are outside that metric.

## Changes

Live Google business lookups now run through a shared pool of at most eight
workers instead of waiting for each listing in sequence. Database reads remain
on the request thread. Results retain their input order and Google details are
fetched again for each request; no response cache or Google-content persistence
was introduced. Homepage recent-business lookups use the same bounded pool.

Rating stars previously fell below 4.5:1 contrast. Darker stars and control
borders now pass the checks below. Long text and narrow-screen form/navigation
layouts wrap without clipping. Search submits announce “Finding fries…” even
when the search uses a private POST body; account forms announce “Saving…”.

Location controls now explain the secure-origin requirement on LAN HTTP,
announce progress, clear stale coordinates, and ignore an older GPS response
after the user edits/selects an address or chooses another location method.

## Response measurements

Windows client to the existing Linux class server over the LAN. The isolated
server preview used Waitress, the configured live Google service and a private
copy of the current class database. The client connected through a loopback SSH
tunnel; this still traverses the LAN. Single-client, no artificial throttling,
five complete responses per page, no application Google-response cache.

| Page | Baseline range, 3 runs | After median, 5 runs | After maximum |
| --- | --- | --- | --- |
| Homepage | 15–30 ms | 61 ms | 63 ms |
| Unified restaurant list | 2,005–3,475 ms | 402 ms | 1,288 ms |
| Wingstop restaurant details | 73–185 ms | 136 ms | 299 ms |
| Fry details / review view | 15–28 ms | 62 ms | 63 ms |

All measured normal responses meet the agreed target. Raw values are in
`response-times-2026-11-03.json`. This is a small class-dataset acceptance check,
not a load-capacity claim. Google outages/timeouts can still exceed the normal
response target and show the existing service-unavailable message.

## Layout, contrast and browser evidence

Executed browser: **Microsoft Edge 156.0.4314.58 on Windows**, Chromium engine.
Desktop live preview was inspected at a 1,897px content width. A same-origin
static layout harness rendered 17 server-generated pages at **390×844** and
**1280×844**, using isolated demonstration users/listings/reviews and the same
templates, styles and scripts. No class accounts/reviews were changed.

Pages: login, registration, privacy, home, search, restaurant, fry/review,
profile, business submission, add restaurant, add fries, admin accounts,
account deletion confirmation, review deletion confirmation, my requests,
admin inbox and validation errors. All **34 layouts** had no horizontal page
overflow or overflowing visible content controls. Long unbroken review text was
included. Raw dimensions are in `layout-results-2026-11-03.json`.

Live preview verification additionally covers registration, profile/address
entry, Google suggestions, catalogue keyboard selection, saved-address search,
and location failure fallback. Earlier FRY-56 acceptance covers ArrowDown/Enter
selection on search, profile and business address fields. The static harness
checks layout, not authentication or submitted-form behavior; integration tests
cover those server workflows.

`python tools/check_contrast.py` passes **31 shared-palette combinations**:
normal text at least 4.5:1 and control/focus boundaries at least 3:1. Rating stars
are 6.40:1 on the page background; muted text is at least 4.92:1 across the tested
surfaces; button text is 6.19:1; control borders are at least 3.50:1.
This palette check does not claim a complete accessibility audit.

Only Edge was available through the connected desktop browser. Chrome,
Firefox and Safari have **not** been separately accepted. The team should review
this explicit browser matrix when approving FRY-40; no unexecuted engine pass is
claimed.

## Location acceptance and merge status

Seth explicitly authorized a real device-location request on the private
`localhost` preview. The browser/device did not return a position and the
address fallback appeared. A successful real GPS result was not claimed.
Browser GPS on the class `http://192.168.1.76:8000` origin still requires a
browser-trusted HTTPS origin; do not disable browser security checks. A local
SSH tunnel can provide a trustworthy localhost origin for a user acceptance
test, without exposing another public listener.

Automated checks cover click-only GPS success, denial/unavailable handling,
insecure-origin guidance and stale-result cancellation. FRY-46 remains
**In Progress** for actual trusted-origin/device acceptance. FRY-40 and FRY-44
are implementation-ready for review, not Done before approved merge.

This branch builds on pending PR #7. Its PR targets that feature branch so the
quality diff is reviewable separately. Merge PR #7 only after teammate approval,
then retarget this PR to main and resolve/retest alongside PR #9 before its own
approved merge. PR #8 carries the independent catalogue import tooling/content.
No pending PR was merged or self-approved during this work.
