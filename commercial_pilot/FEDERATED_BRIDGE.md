# Federated commercial bridge — deployment gates

GitHub Issues -> sanitized CRM-SOFFT draft -> HANTER -> ASTRA -> LEGION/NCA.

This is an **integration component**, not an active cloud worker. It intentionally does not receive database credentials, create external webhooks, or write to production. The intake function defaults to dry_run=True and accepts a DB-API connection only from an authorized server-side runtime. Never use a service_role key in GitHub Actions, issues, browser or public repository.

**Verified schema target:** crm_sofft.lead_registry (workspace_id, demand_source, source_ref, source_receipt_hash, need, state). Current code uses an existence check but production concurrency requires a unique index on (workspace_id, source_ref) plus an INSERT ON CONFLICT strategy before deployment. No index or live mutation is applied in this PR.

The bridge must receive a **trusted, verified GitHub API issue record** and an independent privacy-triage decision. The envelope from astra_handoff_candidate is non-executable. An actual agent task is forbidden until a signed scope approval, authenticated owner authority, Guardian Core decision, validated AI Passport, Enterprise Skills, permitted Runtime Domain, explicit Approval Gateway permit, Audit Ledger write, and independent QA plan exist.

HANTER is the command center; ASTRA is one orchestrator among federated orchestrators, not a global orchestrator. Preserve Zero Trust, Public/Private Boundary and CRYPTO IMPERIAL Ecosystem Boundary. No automatic payments, spending, payout edits, live customer execution or Val Town.

**Next verified deployment gates:**
1. Check Supabase schema constraints, permissions, source uniqueness and isolated writer role.
2. Add a private runtime that fetches GitHub Issues through authorized API, verifies sender and source, runs triage, writes only non-sensitive drafts and records immutable audit evidence.
3. Bind owner approvals and Guardian checks to exact request hash; reject expiry, replay, missing passport or kill-switch.
4. Independently test one real, authorized request end-to-end. No synthetic requests counted as revenue.
