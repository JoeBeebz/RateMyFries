# Sprint 4 static analysis - November 3, 2026

Required tools **SonarQube and Trivy** were run locally using official images. This review covers an analysis-only combination of the deployed runtime and pending catalogue/EC2 tooling, not merged main. Exact revisions, 42 source-file hashes, tool versions, image digests, logs and raw results are in `raw/2026-11-03/`.

- [SonarQube report](Sprint-4-SonarQube-Report.pdf): 0 bugs, **1 BLOCKER vulnerability**, 0 code smells, 0 hotspots; 66.1% coverage. The gate returned OK with **zero conditions evaluated**; the vulnerability remains open.
- [Trivy report](Sprint-4-Trivy-Report.pdf): 0 dependency vulnerabilities, **3 infrastructure misconfigurations** (1 CRITICAL, 1 MEDIUM, 1 LOW), 0 secrets.
- The analysis-only snapshot passed 72 Python tests and 12 JavaScript checks. This does not replace teammate approval, merged-main acceptance, device-location acceptance or initial account sign-ins.
- No finding was suppressed or remediated for this reporting request. No deployed AWS permissions/network changes were made.

The findings concern wildcard metadata permissions, unrestricted outbound traffic, missing MFA enforcement and an undescribed security-group rule. The PDFs include manual context and recommended follow-up. The egress finding does not indicate public inbound website access.

## Preserved Sprint 3 baseline

The October 20 baseline remains in the original Sprint 3 folder: [SonarQube](../../sprint-3/static-analysis/Sprint-3-SonarQube-Report.pdf) and [Trivy](../../sprint-3/static-analysis/Sprint-3-Trivy-Report.pdf). Its raw evidence remains untouched. That application-only baseline reported zero final findings and 82.2% coverage. This Sprint 4 review adds infrastructure and operational tooling, so the trend is not a like-for-like application-only regression measurement.

Sprint 4 is the owner-confirmed submission label. Original Jira/tool identifiers retain their recorded Sprint 3 names in raw evidence; they have not been rewritten. See the Jira and GitHub reports for the recorded scope and prior merged baseline.

## PDF checksums

- `Sprint-4-SonarQube-Report.pdf`: `40c87427c788e0b69e20ac6e9b014cc6442fdb39b4001a29a3fac10ae0973280`
- `Sprint-4-Trivy-Report.pdf`: `821b1427fbe1a402d8f560d287cd23d202ce180395ee8e3e855e83a2a8652df9`

This static analysis was generated using automated tools during this sprint.
