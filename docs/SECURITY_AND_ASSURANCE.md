# Security, Assurance & Quality Gates

## Zero Trust
Treat end users, browsers, API calls, plugins, prompts, code artifacts, uploads and agents as untrusted until proven otherwise. No cross-venture shared secrets. Encrypt private tenant data in transit and at rest with provider-supported mechanisms.

## Controls
- Identity: validated sessions, least-privilege RBAC/ABAC, expiry and revocation.
- Tenant separation: tenant ID derived from authenticated principal, not untrusted request headers. Validate row-level policy with adversarial tests.
- Data: classify before ingest, minimize, retain by policy, make delete/export practical and auditable.
- Supply chain: lock dependencies, review permissions, run static/secret scans, produce provenance and SBOM prior to launch.
- Artifacts: deny symlink/path traversal and secret files. Treat uploaded CSV, PDFs, images and source instructions as untrusted.
- Model usage: redaction, prompt-injection defense, allowlisted external destinations, approval before sending regulated/private content to outside services.
- Webhooks and network: verify signatures, URL allowlists, prohibit private-network SSRF targets, replay defense, idempotency, bounded retries.
- No use of another party's data, account, branding or intellectual property without lawful permissions.

## Release acceptance
A release is not `READY` unless:
1. Tests pass for exact commit SHA in CI.
2. Browser + API + DB end-to-end flow passed.
3. Independent QA signed acceptance; QA identity distinct from code author.
4. CYBER HAK threat checks and Guardian Core policy checks are attached.
5. Production access, cost, quota and data processing reviewed.
6. Backups and rollback tested, recovery targets documented.
7. Signed approval recorded; Audit Ledger references immutable evidence digest.

## Do not confuse
`GitHub Actions green` ≠ security certification.
`Function ACTIVE` ≠ live customer usage.
`500 simulated agents` ≠ 500 autonomous workers.
`Ready to exit` ≠ sold or payment received.

## Reporting
See [SECURITY.md](../SECURITY.md). Private security details must never be filed in public Issues.
