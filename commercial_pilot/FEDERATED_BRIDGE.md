# Federated commercial bridge — deployment gates

GitHub Issues -> sanitized CRM-SOFFT draft -> HANTER -> ASTRA -> LEGION/NCA.

This is an **integration component**, not an active cloud worker. It intentionally does not receive database credentials, create external webhooks, or write to production. The intake function defaults to dry_run=True and accepts a DB-API connection only from an authorized server-side runtime. Never use a service_role key in GitHub Actions, issues, browser or public repository.

**Verified schema target:** crm_sofft.lead_registry (workspace_id, demand_source, source_ref, source_receipt_hash, need, state). Database verified on 2026-10-28: UNIQUE (workspace_id, demand_source, source_receipt_hash) exists and EXPLAIN confirms the exact ON CONFLICT arbiter. No real lead row was inserted in this verification. Actual CRM ingestion still requires an isolated, authorized server-side writer and verification of API origin, privacy, RLS and owner policy.

The bridge must receive a **trusted, verified GitHub API issue record** and an independent privacy-triage decision. The envelope from astra_handoff_candidate is non-executable. An actual agent task is forbidden until a signed scope approval, authenticated owner authority, Guardian Core decision, validated AI Passport, Enterprise Skills, permitted Runtime Domain, explicit Approval Gateway permit, Audit Ledger write, and independent QA plan exist.

HANTER is the command center; ASTRA is one orchestrator among federated orchestrators, not a global orchestrator. Preserve Zero Trust, Public/Private Boundary and CRYPTO IMPERIAL Ecosystem Boundary. No automatic payments, spending, payout edits, live customer execution or Val Town.

**Next verified deployment gates:**
1. Check Supabase schema constraints, permissions, source uniqueness and isolated writer role.
2. Add a private runtime that fetches GitHub Issues through authorized API, verifies sender and source, runs triage, writes only non-sensitive drafts and records immutable audit evidence.
3. Bind owner approvals and Guardian checks to exact request hash; reject expiry, replay, missing passport or kill-switch.
4. Independently test one real, authorized request end-to-end. No synthetic requests counted as revenue.

## Read-only public source discovery

The scheduled GitHub workflow `commercial-source-discovery.yml` fetches public issues over HTTPS, verifies canonical API URLs, checks both consent boxes and triage, filters owner/system tests, and prints counts only. `python -m commercial_pilot.source_sync --output review.json` writes a sanitized **draft manifest**, never customer text. This is NOT production CRM ingestion; do not put Supabase secrets in GitHub Actions. There is no agent dispatch or payment capability in the discovery job.
