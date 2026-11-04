# Sprint 3 static analysis - November 3 snapshot

Required tools **SonarQube and Trivy** were run locally using the official cached images. The scan covers an analysis-only source combination of the deployed runtime and pending catalogue/EC2 tooling; it is not represented as merged main. Exact source revisions, 42 file hashes, image digests, logs, task responses and inventory are in `raw/2026-11-03/`.

- [Current SonarQube PDF](Sprint-3-Final-SonarQube-Report.pdf): 0 bugs, **1 BLOCKER vulnerability**, 0 code smells, 0 security hotspots; 66.1% overall coverage. Its gate returned OK with **zero conditions evaluated**, so no clean-security claim is made.
- [Current Trivy PDF](Sprint-3-Final-Trivy-Report.pdf): 0 dependency vulnerabilities, **3 infrastructure misconfigurations** (1 CRITICAL, 1 MEDIUM, 1 LOW), 0 secrets.
- Source combination: 72 Python tests and 12 JavaScript checks passed. This does not substitute for teammate approval, merged-main acceptance, live account first sign-ins or device-location acceptance.
- Findings remain open. No source remediations, finding suppressions or live AWS configuration/permission changes were made for this reporting task.

The Sonar finding concerns wildcard metadata permissions. Trivy flags unrestricted outbound traffic, missing MFA enforcement and an undescribed rule. The PDFs include the exact findings, manual context, recommendations and coverage/scan limits. Public inbound access was separately blocked during migration acceptance; an outbound finding is not a claim that the website is publicly reachable.

## Preserved same-sprint baseline

The October 20 baseline PDFs remain [SonarQube](Sprint-3-SonarQube-Report.pdf) and [Trivy](Sprint-3-Trivy-Report.pdf), with original `raw/` and `raw/initial/` evidence untouched. That application-only baseline reported zero final findings and 82.2% coverage. The November snapshot expands into infrastructure and operational tools; trends are not a like-for-like application-only regression measurement. No Sprint 2 static scan is available for a previous-sprint comparison.

## Current PDF checksums

- `Sprint-3-Final-SonarQube-Report.pdf`: `ddfdcfcdfb2e55cb62c285166ecd8d0e1d813e6b90345c2fe994a60b98e46e00`
- `Sprint-3-Final-Trivy-Report.pdf`: `265ff431f9c72328bb59214e7974f06bb9f63079f6030a093c63a14698f3ea7f`

This static analysis was generated using automated tools during this sprint.
