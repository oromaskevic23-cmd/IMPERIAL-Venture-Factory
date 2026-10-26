# VF-05 — RenewalRadar

**Product thesis:** Contract and license renewals  
**State:** IDEA / NOT BUILT / NOT RELEASED / REVENUE UNVERIFIED / NOT LISTED  
**Evidence posture:** Proposal; market demand and pricing are hypotheses.  
**Asset boundary:** Standalone buyer-transferable application, no strategic IMPERIAL Core IP conveyed by default.

## Buyer and job
**Ideal customer:** MSPs, agencies and procurement operators.  
**Observed problem to validate:** Critical renewal dates go unnoticed.  
**Buying trigger to test:** repeated workload, loss, delay or operational risk tied to this job; confirm in interviews and paid pilot.

## MVP acceptance contract
- Customer can register/access a scoped workspace and input real but authorized data.
- Core vertical slice: Renewal register; owner; reminders; escalation; snooze; CSV export.
- User can see and export results; durable state and delete policy documented.
- Core entities: `Organization}`, `{Contract}`, `{Renewal}`, `{Owner}`, `{Notification}`, `{Acknowledgment` (logical domain names; final schema TBD).
- Least privilege, tenant isolation, accessibility and restore/rollback evidence.
- Browser → API → database → response workflow independently tested.

## Excluded from v1
No automated purchasing or cancellation.

## Risk register
Primary risk: **Notification failure and inappropriate disclosure of contracts**.  
Required mitigations: threat-model review, deny by default, scoped credentials, data minimization, validated exports, CI, independent QA, incident and recovery procedures.

## Commercial hypothesis and proof
- Buyer interview plan: Dry-run renewal scenarios, approval-controlled notifications, 1 pilot.
- Metrics to baseline and verify: Missed renewal count; lead time; active accounts.
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
