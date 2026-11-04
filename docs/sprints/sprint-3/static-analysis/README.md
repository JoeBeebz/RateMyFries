# Sprint 3 static analysis

- Scanned GitHub revision: `b93baae14b9fefb54077c02bad7f740cb358902b`.
- Tools ran locally on Docker Desktop; image digests and execution details are in `raw/scan-metadata.json`.
- [SonarQube PDF](Sprint-3-SonarQube-Report.pdf): tool dashboard/API export. Bugs **0**, vulnerabilities **0**, code smells **0**, security hotspots **0**, Quality Gate **PASS**.
- [Trivy PDF](Sprint-3-Trivy-Report.pdf): converted filesystem-scan summary. CRITICAL **0**, HIGH **0**, MEDIUM **0**, LOW **0**.
- Current source passed **48** integration/regression tests. SonarQube imported overall coverage is **82.2%**.
- Initial same-sprint findings and unmodified tool exports are retained under `raw/initial/` and `raw/`. Initial Sonar issues were fixed and rescanned; no findings were suppressed or manually marked safe.
- No Sprint 2 scan artifacts were available, so previous-sprint comparisons are explicitly unavailable. These reports establish the first recorded automated baseline.

The PDFs read metrics directly from the successfully completed tools' JSON output. SonarQube Community Build data was exported via its dashboard APIs; Trivy JSON was converted to a PDF summary. Both PDFs include scope/exclusions, versions, trend limits, reflection and the required automated-tools statement. PDF pages were rendered and visually inspected before submission.

Application source and tests were exported from the stated GitHub revision without Git history, local database/signing key, virtual environments, reports, IDE files or demo media. Trivy also scanned the resolved installed Python dependency inventory; it did not scan a deployment container image. License detection was skipped because site-packages was not mounted; dependency vulnerability detection completed.

## PDF checksums (SHA-256)

- `Sprint-3-SonarQube-Report.pdf`: `2e6f3abf423976b7e7acd278f75975bbe2a7674c8e95f1c6b4ef6515a560b4fc`
- `Sprint-3-Trivy-Report.pdf`: `75a08cf414686bb328ba20cbb7d793930a829ac1ecb85fd8830fa964c1d67243`

This static analysis was generated using automated tools during this sprint.
