# Operations Runbook — Factory Control Plane

## Normal workflow
1. Record venture intent and authorized scope.
2. Link an approved issue, ADR, cost ceiling and permission set.
3. Request approval references; never put secrets in issues.
4. Build in isolated venture workspace via delegated engineering orchestrator.
5. Attach sanitized evidence digests with originals in private storage.
6. Independent QA and CYBER HAK review before Pilot or Release.
7. Approval Gateway validates authority; only authorized operator deploys.
8. Audit Ledger records event hashes; rotate exposed credentials.

## Incident triggers
- Unexpected outbound destination, anomalous spend, cross-tenant access, key leak, unauthorized agent or conflicting financial evidence.
- **Fail closed**: stop the affected scoped job. Do not destroy evidence or production data.
- Revoke relevant credentials, preserve immutable logs, inform Founder, open private incident record, run rollback only under accepted procedure.
- Record impact, containment, verification and postmortem.

## Budget envelope
FREE_ONLY: no accidental paid accounts, background polling costs, paid model tokens or billable add-ons. Validate each platform quota and billing state before any cloud deployment.

## Release/handover
Use a dedicated venture release pipeline. Customer data export, backup and disaster recovery test must be independently reviewed. Buyer access cannot include private IMPERIAL Core infrastructure by default.

## Status semantics
A successful manifest validator is **repository structural QA**, not real-app runtime QA. CI cannot assert first revenue, valuation or executed sale.
