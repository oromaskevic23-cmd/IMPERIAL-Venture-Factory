# IMPERIAL Core — commercial runtime checkpoint (2026-10-28)

**Evidence-based status:** PARTIAL — public enquiry intake and source-level CRM bridge available; credentialed private CRM writer, authorized NCA execution, independent production QA, customer acceptance and payment integration are NOT deployed.

## Verified deliverables

1. [PR #16](https://github.com/oromaskevic23-cmd/IMPERIAL-Venture-Factory/pull/16) merged into `main`, merge `b0f7862700aea55429db50e6cc0211301bcd7331`. It adds `commercial_pilot/federated_bridge.py` — draft-only, idempotent, non-executable bridge.
2. [PR #18](https://github.com/oromaskevic23-cmd/IMPERIAL-Venture-Factory/pull/18) merged into `main`, merge `eda758c8b54312a263085c37aff87c6f65f477b2`. It adds read-only GitHub API issue discovery, stricter consent/privacy validation, sanitized draft manifests, and an hourly scheduled workflow.
3. [GitHub Actions verification](https://github.com/oromaskevic23-cmd/IMPERIAL-Venture-Factory/actions/runs/40652309923) completed SUCCESS on PR #18. All configured commercial pilot tests, deterministic synthetic trace audit, cross-check and no-fake-revenue gates passed. This does not verify customer acceptance or live runtime.
4. Supabase `crm_sofft.lead_registry`: the existing unique constraint `(workspace_id, demand_source, source_receipt_hash)` was verified read-only. `EXPLAIN` confirmed that the bridge's `ON CONFLICT ... DO NOTHING` uses the existing unique arbiter. No lead row was inserted for this check.
5. Supabase `crm_sofft.lead_registry` has RLS enabled; no policy was found in the security advisor. It must stay denied for public users until tested grants and isolated server-side identity are established.
6. No real buyer, collected payment or authorized autonomous client execution was established by the above evidence. Owner/system-test issues must never be counted as customers.

## Concrete flow now available

Public GitHub enquiry form → GitHub safe issue triage and acknowledgement → scheduled read-only source discovery → sanitized draft manifest → **separate private CRM writer gate** → owner-approved scope and terms → HANTER federated routing / ASTRA orchestrator → LEGION / Nano Core Agents → Guardian Core, AI Passport, Enterprise Skills, Approval Gateway, Zero Trust, CYBER HAK, Audit Ledger → Independent QA → consented delivery → verified customer acceptance → externally evidenced payment.

The flow stops at the bold gate. Later transitions are architecture / planned integrations, not running production actions.

## Next engineering gates

- Deploy an isolated server-side CRM writer with least privilege and strict source/consent checks. Never embed a database secret or service-role key in a public GitHub repo, workflow or frontend.
- Enforce owner approval bound to a specific scope and audit evidence, Guardian/Core policy, owner kill switch, AI Passport and permitted execution runtime before any NCA dispatch.
- Bind proof hashes to independent QA and delivery; keep distinct reviewer and executor.
- Require external provider evidence for PAYMENT_CONFIRMED; do not invent transactions.
- Run a supervised end-to-end pilot with a real, consenting buyer; keep all test items marked test-only and revenue zero.

**Policy:** FREE_ONLY; no Val Town; no automatic spending or unsolicited outreach; separate SHPAIZMAN-RU beneficiary; no CRYPTO IMPERIAL payout or token mixing; GitHub materials in English only. HANTER is the command center and ASTRA is one orchestrator of a federated Multi-Orchestrator Architecture.

## Evidence limits

The first actual GitHub Actions source-discovery job was triggered by a controlled main-branch push and independently checked: [run 40652562824](https://github.com/oromaskevic23-cmd/IMPERIAL-Venture-Factory/actions/runs/40652562824). It completed with SUCCESS, 37/37 unit tests PASS, source discovery completed without credentials, and the sanitized output reported `eligible_count=0`, `rejected_or_ignored_count=13`, `payments_verified=0`, `dispatch_allowed=false`. This is one observed run, not proof of uninterrupted 24/7 reliability. Scheduled hourly execution still needs future observations.
