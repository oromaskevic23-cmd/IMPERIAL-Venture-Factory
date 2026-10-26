# VF-10 — SiteSignal

**Product thesis:** Consent-based site monitoring  
**State:** IDEA / NOT BUILT / NOT RELEASED / REVENUE UNVERIFIED / NOT LISTED  
**Evidence posture:** Proposal; market demand and pricing are hypotheses.  
**Asset boundary:** Standalone buyer-transferable application, no strategic IMPERIAL Core IP conveyed by default.

## Buyer and job
**Ideal customer:** Web agencies and managed site operators.  
**Observed problem to validate:** Agencies find outages and TLS expiry after clients do.  
**Buying trigger to test:** repeated workload, loss, delay or operational risk tied to this job; confirm in interviews and paid pilot.

## MVP acceptance contract
- Customer can register/access a scoped workspace and input real but authorized data.
- Core vertical slice: Verified domain ownership; rate-limited probes; TLS expiry; incident log; alerts; export.
- User can see and export results; durable state and delete policy documented.
- Core entities: `Account}`, `{MonitoredSite}`, `{OwnershipProof}`, `{Probe}`, `{Incident}`, `{Notification` (logical domain names; final schema TBD).
- Least privilege, tenant isolation, accessibility and restore/rollback evidence.
- Browser → API → database → response workflow independently tested.

## Excluded from v1
No open Internet scanning or stealth probes.

## Risk register
Primary risk: **Unauthorized scanning, excessive probing, false outage alerts**.  
Required mitigations: threat-model review, deny by default, scoped credentials, data minimization, validated exports, CI, independent QA, incident and recovery procedures.

## Commercial hypothesis and proof
- Buyer interview plan: Verified ownership, bounded frequency, fault injection, 1 agency pilot.
- Metrics to baseline and verify: Detection-to-notify; false alert rate; churn.
- Pricing **TBD** after willingness-to-pay interviews. Never claim booked revenue without reconciled receipts.
- The transfer package must include exact source SHA, portable export/migration, runbook, dependency licenses, redacted demos and buyer acceptance.

## Exit/no-go boundaries
- No sale, licensing, domain transfer, customer-data release, paid infrastructure, or public production deployment without designated Founder authorization.
- Keep `Guardian Core`, `CYBER HAK`, `Approval Gateway`, `Audit Ledger`, `ProofGraph`, `AI Passport`, `Enterprise Skills` and public/private boundaries intact.
- No unapproved dependency on core IMPERIAL Core agents or protected algorithms.

## Evidence checklist
- [ ] 10 qualified discovery conversations (target)
- [ ] At least one representative real-user workflow supplied with consent
- [ ] MVP architecture ADR and threat model
- [ ] Deterministic test suite and CI on exact release commit
- [ ] Independent end-to-end QA pass and human-reviewed deployment
- [ ] Legitimate pilot and observed value
- [ ] Financial evidence or explicit pre-revenue disclosure
- [ ] Clean buyer data room and Founder sign-off
