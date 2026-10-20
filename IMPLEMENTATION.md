# Sprint 3 implementation evidence

Sprint: FRY Sprint 3 (Jira sprint ID 3), started October 20, 2026. Commitment: 12 Stories / 46 story points, all assigned to Seth Martin (`sethdmartin1000`). No old backlog work is included.

| Jira | Implementation | Validation |
| --- | --- | --- |
| FRY-45 | `/search` combines restaurant/fry discovery; legacy URLs redirect | Combined style/price/rating/name/distance tests; browser layout |
| FRY-46 | Explicit current-location button and server Places address lookup | Mocked coordinates, permission/error fallback UI; live Google check blocked |
| FRY-47 | Additive role migration, DB CHECK/default, role read from server identity | Forged registration/profile roles rejected; migration tests |
| FRY-48 | Atomic admin approval/rejection with reviewer, time, note and publication | Pending isolation, approve/reject and repeated decision tests |
| FRY-49 | Authenticated business form and my-request history | Required/length/duplicate/CSRF validation, cross-user isolation |
| FRY-50 | Optional owner-only address, clear/save, explicit private use | Profile isolation, no address in public/search page URL, clear test |
| FRY-51 | Address and radius inputs replace coordinate menu | Mocked geocoding, composed distance filters and unavailable-service tests; live Google check blocked |
| FRY-52 | `import-kenosha` persists only Google place IDs; details fetched live | Mocked idempotent 3-business import, no invented reviews/menus; actual import blocked by missing key |
| FRY-53 | Server admin guard for stores and fry options | Direct regular-user GET/POST denied; admin creation succeeds |
| FRY-54 | Admin-only pending/history inbox | User/anonymous denial, escaped content, review actions |
| FRY-55 | Admin-only promotion of existing account with audit; one-time operator bootstrap | Forged role/CSRF attempts fail; promotion idempotent; second bootstrap refused |
| FRY-56 | Debounced Google suggestions after 3 characters; keyboard listbox and fallback | API contract, stale-request cancellation code, browser unavailable state; live Google check blocked |

The operator bootstrap is the sole first-admin initialization exception. No real user account is promoted automatically, and no credentials are committed. Profile addresses remain owner-only; approved business addresses are intentionally public.

Google Places is used for discovering third-party businesses rather than the Business Profile API for managing owned listings. Google details are retrieved live to avoid persisting restricted content. The real Kenosha import was not run successfully without a key; mocked test businesses are not published as real businesses.

Automated validation: 47 passing integration/regression tests, JavaScript syntax validation, and patch whitespace check. Static analysis evidence is produced after the Jira and GitHub reporting steps. Browser acceptance checks and any remaining review constraints are recorded in the sprint reports.
