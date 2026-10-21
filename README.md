# Rate My Fries

A Flask/SQLite website for discovering restaurants and fries, sharing ratings, and submitting businesses for administrator review.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
```

Open http://127.0.0.1:5000. Data and the generated signing key remain in ignored `instance/` files. Existing Sprint 2 databases upgrade automatically and retain their accounts/listings/reviews. Back up the database before deployment. `flask --app app seed-demo` optionally adds three clearly fictional restaurants without reviews or users.

## Accounts and businesses

Public registration always creates a regular user. Users can review fries, edit their own profile, save/clear a private address, and submit business requests. Only administrators can directly add stores/fry options, access the request inbox, approve/reject submissions, or authorize another administrator. Pending requests are visible only to their submitter and administrators.

After registering the intended first account, the trusted deployment operator runs this **once**:

```powershell
.venv\Scripts\python -m flask --app app bootstrap-admin REGISTERED_USERNAME
```

This operator-only setup refuses to run when any administrator exists. There is no web bootstrap and no default account/password. Later administrators are registered users promoted from **Admin accounts** by an existing administrator. Promotions record the authorizing administrator. The final administrator cannot delete their account until another administrator exists.

## Google location setup

Enable **Places API (New)** in a billing-enabled Google Cloud project. Configure an API-restricted server key through the deployment secret manager or this process environment; never commit it. Apply appropriate server/IP restrictions and Google quotas/budget alerts. The app sends requests from the server and never exposes the key in page source.

```powershell
# Set GOOGLE_PLACES_API_KEY in your process environment, then restart the app.
.venv\Scripts\python -m flask --app app import-kenosha
```

The import discovers restaurants serving fries in Kenosha, Wisconsin and requires at least three results. It persists only Google place IDs, retrieves business details live, and shows Google Maps/provider attribution. It creates no fabricated fry menus, prices, reviews or ratings. Google Business Profile APIs manage owned businesses; Places API is the appropriate discovery API for other businesses.

With a configured key, search/profile/business address fields suggest addresses after three characters. The unified search accepts an address or an explicitly requested device location; an optional saved profile address is used only when selected. Addresses/coordinates are submitted in POST bodies, never inserted into search URLs or saved as search history. User-entered profile/business addresses are stored for their stated purpose. Google lookup results are not persisted. Review the linked location/privacy terms before public deployment.

Without a key, ordinary browsing, accounts, admin workflows, manual business/address entry and reviews work. Suggestions and address distance searches display a useful unavailable message. Actual Google-sourced Kenosha import and live Google acceptance checks remain blocked until configuration exists. Device radius search can use listings with existing coordinates; manually entered listings without coordinates require live address lookup.

## Validation

```powershell
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest -q
node --check static/app.js
```

Tests use isolated temporary databases. They cover role escalation attempts, CSRF, owner-only profile data, request review/duplicate decisions, migrations, combined search and mocked Google success/failure responses. Live Google behavior is a separate credential-dependent acceptance check.

## Deployment

Waitress binds to loopback. For public hosting, use HTTPS, a managed `SECRET_KEY`, `COOKIE_SECURE=1`, backups, trusted proxy configuration, and deployment-specific abuse controls. Passwords use scrypt and server-side sessions support revocation. Google endpoints share a persistent per-IP quota of 60 requests/minute; business submissions allow five/hour per account. Email verification and password reset remain future work. Address-radius searches currently resolve candidate listing addresses synchronously; larger directories will need bounded/paginated discovery and a compliant geospatial storage strategy.

## Sprint evidence

- [Requirements and Jira mapping](Requirements)
- [Sprint 2 reports](docs/sprints/sprint-2/reports/) and [demo](docs/sprints/sprint-2/demos/)
- [Sprint 3 implementation and acceptance evidence](IMPLEMENTATION.md)
- [Sprint 3 reports](docs/sprints/sprint-3/)

## Team workflow

Develop on a feature branch, run tests, and open a PR into `main`. Have a teammate review and approve the PR before merging. Jira stories with implemented, tested code stay **In Review** until the PR is approved/merged and the acceptance check is complete. Do not bypass repository review requirements.
