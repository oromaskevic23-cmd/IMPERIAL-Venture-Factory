# Architecture — Federated Venture Factory

## Operating topology
```text
Architect / Owner (final decisions)
  |
  +-- Policy plane: Guardian Core | CYBER HAK | Approval Gateway | Audit Ledger
  |
  +-- ASTRA coordination plane (federated planning, no unlimited root powers)
          |
          +-- Research orchestration / scoped NCA (discovery)
          +-- Engineering orchestration / CONSTRUCTOR AI (build + testing)
          +-- Assurance orchestration / independent QA (proof)
          +-- Commercial orchestration / human-reviewed pilots
          +-- Exit orchestration / human-approved buyer data room
                        |
                 independently owned venture boundaries (VF-01 ... VF-10)
```

The mission coordinator **ASTRA** never automatically acquires authority to spend money, transfer source code, read all customer data, sign agreements, run uncontrolled web requests, or publish externally.

## Contract: Venture Unit
Every unit has: `venture_id`, target buyer, owner, stage, approved capability list, separate identity & secrets, product code, export API, deterministic core path, risk profile, proof bundle, and sale boundary.

## Technical design baseline
- Separate multi-tenant domains or dedicated isolated deployments by product; no production DB shared across a future acquirer.
- Portable persistence with migration and backup/export/restore proofs.
- Infrastructure as code only when within owner budget and permissions; free-tier quotas must be documented.
- Structured audit events: actor, scope, task ID, capability, approval reference, timestamp, action, result, evidence hash. Do not store secrets or full raw customer files in logs.
- Synchronous operations have explicit retry/timeout budgets; asynchronous jobs need idempotency keys, leases and dead-letter behavior.
- Minimum release checks: type checks, dependency & secret scan, unit/integration tests, browser E2E, independent QA, threat review, rollback rehearsal, accessibility and incident runbook.
- AI only through a cost-bounded model gateway with redaction and privacy rules; never claim ownership of third-party model weights.

## Control plane invariants
**Identity ≠ Authority. Capability ≠ Approval.** Agent AI Passport proves identity metadata; a Signed Agent Permit / authorization policy scopes individual missions. Enterprise Skills describe permissible functions and required evidence but do not grant privileges. Approval Gateway approves sensitive actions; Guardian Core and CYBER HAK apply deny-by-default security; Audit Ledger records authorized state changes. ProofGraph links test, review, build and release evidence.

## Public / Private Boundary
Only redacted portfolio and verifiable product status are public. Keep buyers, revenues, credentials, contracts, audit originals, private models and diligence material in access-controlled systems.

## Transfer boundary
Use contractually valid licenses for reusable tooling. Do not bake private IMPERIAL Core agent code into an asset that will be sold without explicit transfer rights. Complete technical and legal separation before listing.
