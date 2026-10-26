# VF-01 — ApproveDesk

**Product thesis:** Agency client approvals  
**State:** IDEA / NOT BUILT / NOT RELEASED / REVENUE UNVERIFIED / NOT LISTED  
**Evidence posture:** Proposal; market demand and pricing are hypotheses.  
**Asset boundary:** Standalone buyer-transferable application, no strategic IMPERIAL Core IP conveyed by default.

## Buyer and job
**Ideal customer:** Design and marketing agencies (2–30 staff).  
**Observed problem to validate:** Client approval cycles fragmented across chats and email.  
**Buying trigger to test:** repeated workload, loss, delay or operational risk tied to this job; confirm in interviews and paid pilot.

## MVP acceptance contract
- Customer can register/access a scoped workspace and input real but authorized data.
- Core vertical slice: Assets and revisions; per-client share links; annotated feedback; approve/reject with named actor; exportable evidence.
- User can see and export results; durable state and delete policy documented.
- Core entities: `Tenant}`, `{Project}`, `{Client}`, `{AssetVersion}`, `{Comment}`, `{ApprovalEvent` (logical domain names; final schema TBD).
- Least privilege, tenant isolation, accessibility and restore/rollback evidence.
- Browser → API → database → response workflow independently tested.

## Excluded from v1
No video editing; no unapproved external publishing.

## Risk register
Primary risk: **Unauthorized approval and unsafe file uploads**.  
Required mitigations: threat-model review, deny by default, scoped credentials, data minimization, validated exports, CI, independent QA, incident and recovery procedures.

## Commercial hypothesis and proof
- Buyer interview plan: 3 representative agency workflows, 1 signed or paid pilot, evidence of approval-cycle improvement.
- Metrics to baseline and verify: Time-to-approval; revision rounds; trial-to-paid; retained teams.
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
