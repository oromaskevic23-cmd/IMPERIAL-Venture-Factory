# VF-02 — InvoiceRelay

**Product thesis:** Invoice follow-up workflow  
**State:** IDEA / NOT BUILT / NOT RELEASED / REVENUE UNVERIFIED / NOT LISTED  
**Evidence posture:** Proposal; market demand and pricing are hypotheses.  
**Asset boundary:** Standalone buyer-transferable application, no strategic IMPERIAL Core IP conveyed by default.

## Buyer and job
**Ideal customer:** B2B freelancers and small service companies.  
**Observed problem to validate:** Overdue invoices lack reliable follow-up and ownership.  
**Buying trigger to test:** repeated workload, loss, delay or operational risk tied to this job; confirm in interviews and paid pilot.

## MVP acceptance contract
- Customer can register/access a scoped workspace and input real but authorized data.
- Core vertical slice: CSV invoice ingest; customer ledger; aging view; reminder draft; explicit approve-send; audit export.
- User can see and export results; durable state and delete policy documented.
- Core entities: `Tenant`, `Customer`, `Invoice`, `ReminderDraft`, `DeliveryRecord`, `StatusImport` (logical domain names; final schema TBD).
- Least privilege, tenant isolation, accessibility and restore/rollback evidence.
- Browser → API → database → response workflow independently tested.

## Excluded from v1
No payment handling, debt collection law advice or autonomous sending.

## Risk register
Primary risk: **Financial personal data; spam and unauthorized collections**.  
Required mitigations: threat-model review, deny by default, scoped credentials, data minimization, validated exports, CI, independent QA, incident and recovery procedures.

## Commercial hypothesis and proof
- Buyer interview plan: 3 real receivables workflows, controlled pilot with opt-in and reconciled payment outcomes.
- Metrics to baseline and verify: Days sales outstanding; aging bands; approval rate; paid invoices verified by records.
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
