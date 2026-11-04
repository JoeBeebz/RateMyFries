# FRY-58: catalogue-only search autofill

Story created before implementation: https://ratemyfries.atlassian.net/browse/FRY-58

Both the homepage and discovery form offer a keyboard-accessible combobox of public catalogue names. The list is fetched once per page, filtered locally by case-insensitive name prefix, sorted alphabetically, and limited to six options total across all search types. Each additional character narrows the list; names containing the text elsewhere do not appear. Restaurant names, fry names and styles currently used by fries are eligible; pending business requests and private addresses are not exposed. IDs-only restaurant placeholders resolve their names live; Google response content is not cached. Known independently sourced restaurant names do not require Google for suggestions. Google address autocomplete remains separate.

The server enforces full-name/style equality after normalization of case and whitespace. Selecting a restaurant or typing its complete name includes its fries. Unknown text, partial names, SQL wildcards and misspellings return zero matches even without JavaScript; blank input still browses the directory. Existing style, price, rating, sorting and location filters compose with the name match. Search length supports the application's 120-character listing names; queries over 240 characters are rejected instead of silently matching a truncated value.

## Verification

- 61 Python tests passed, including exact restaurant matches on GET/POST, all fries for that restaurant, case/whitespace, misspellings/partial names, special characters/wildcards, fry/style/blank search, composed filters, long names, public-only suggestions and live Google placeholder handling.
- Four Node interaction checks passed for keyboard/pointer selection, changed and cleared input, Escape/blur with late responses, retries after unavailable suggestions safe text rendering, and generic prefix narrowing with a six-option combined limit. JavaScript syntax and whitespace checks passed (preserving existing tracked CRLF endings).
- A private preview used a copy of the live database with 16 restaurant listings and 37 fry options. Browser checks confirmed homepage ArrowDown/Enter selection, directory pointer selection, and typo submission. `Wingstop` returned one restaurant and four fry options; `wngstop` returned zero restaurants and zero fry options. A captured homepage at 390 px confirmed readable, full-width suggestions. Prefix follow-up browser checks returned six options for `W`, four for `Wa`, three for `Waf`, and only Wendy's for `We`. The combined six-option cap is also tested with more than six matching fixture entries.

The description-only cleanup was applied separately to live content with a private SQLite backup. Visitors now see only the restaurant/dish description; its source metadata remains in the catalogue manifest on the FRY-57 branch. No new story was created for that cleanup, per the user's instruction.

The FRY-58 runtime changes remain on their feature branch for teammate review before merge/deployment. Keep Jira In Review until approval, merge and live acceptance. The separate Google address JavaScript fix remains in PR #7 and is not bundled into this change.
