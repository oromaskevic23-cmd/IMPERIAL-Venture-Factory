# Private CRM Draft Writer — Deployment and Acceptance Evidence

**Project:** IMPERIAL Core / CRM-SOFFT / IC-OFFER-001
**Checkpoint:** 2026-10-28
**Mission:** allow a strictly limited, authenticated server-side draft of a verified real public enquiry. Do not claim completed client execution or payment.
**Owner authority:** Alexander Romaskevich (RomaskevicH).

## What has actually been deployed

- Existing Supabase project ref `flqxwhibxnyujynmopmr` (eu-central-1); existing business tables preserved.
- Supabase migration `commercial_private_writer_gate_20261028` recorded by the database and reproduced in [the source-controlled SQL](../supabase/sql/commercial_private_writer_gate_20261028.sql).
- Edge Function `imperial-commercial-private-writer`, version 1, status ACTIVE; platform `verify_jwt=true`. Edge bundle SHA-256: `1fc2e7a1015e84a796fd2905ff36bb872f5779a4cba3bf549b695ccb12e987a5`.
- Source file: [edge function](../supabase/functions/imperial-commercial-private-writer/index.ts) and [fixed-host source verifier](../supabase/functions/imperial-commercial-private-writer/core.mjs).
- No service_role secret is used by the Edge Function; it uses a publishable/anon key with the *caller's* JWT. The only database mutation path available is `public.imperial_commercial_draft_intake(bigint,text)`, bound to one offer and source. The function only inserts a **DRAFT LEAD** with a derived receipt hash. It cannot authorize work, create delivery, modify payouts or assert payment.
- No Supabase Auth identity exists in this project as of this checkpoint. The strict writer ACL has **zero** rows. Production writes are therefore **disabled**, despite Edge deployment.

## Security gates (tested and enforced)

1. Edge platform requires valid JWT. The function independently validates the user with the Auth server. No public unauthenticated writes.
2. Auth user must carry admin-controlled `app_metadata.imperial_commercial_writer = "enabled"` and the same `auth.uid()` must match an `ENABLED` entry in the private `crm_sofft.commercial_writer_identities` ACL with recorded Owner approval reference/time. The ACL is empty until separately authorized onboarding.
3. For every call, Edge fetches the specific **open** GitHub issue from the fixed repository API endpoint, never from a client-supplied URL or issue body. It verifies the exact source URLs, issue ID, public form markers, both completed consent checkboxes, non-owner human account and absence of indicated test, privacy-hold, or secret patterns.
4. The database derives and verifies the SHA-256 source receipt independently before inserting non-sensitive fixed fields. Existing unique constraint `(workspace_id,demand_source,source_receipt_hash)` makes duplicates no-op.
5. Public SQL role `anon` has no EXECUTE on the RPC; `authenticated` has EXECUTE only on this one capability but **no direct INSERT or SELECT** on `crm_sofft.lead_registry`. The ACL has RLS enabled with no public policies.
6. No browser automation, private customer credentials, unsolicited client contact, payment authorization, spending, Val Town or crypto/token payout routing.

**Important security-review note:** The Supabase security advisor emits an intentional WARN that `authenticated` may execute the narrow `SECURITY DEFINER` RPC in the `public` schema. This is necessary for the existing public Data API RPC endpoint, while the function enforces both trusted Auth metadata and the empty-by-default private ACL. This is an explicit review exception, **not** a claim that the overall security review has passed. The only authorized writer should be a dedicated, non-customer service identity. Direct RPC calls by an approved service identity are technically possible; approve only trustworthy server-side callers and re-review before enabling.

## Verification evidence

- [GitHub CI run 40653753348](https://github.com/oromaskevic23-cmd/IMPERIAL-Venture-Factory/actions/runs/40653753348): completed SUCCESS with Node source/digest guard tests, 37 Python commercial regression tests and no-secret/no-fake-payment assertions.
- Supabase migration listed by name and Edge Function reported ACTIVE with `verify_jwt=true`.
- DB read-only privilege check: `anon_can_execute=false`, `auth_can_execute=true`, `auth_can_insert_table=false`, `service_role_can_insert_table=false`, `enrolled_writers=0`, `commercial_github_leads=0`.
- [Previously verified source discovery run](https://github.com/oromaskevic23-cmd/IMPERIAL-Venture-Factory/actions/runs/40652562824) screened 13 repository records: `eligible_count=0` and `payments_verified=0`.
- No live authorized Edge request, production INSERT, customer acceptance or payout is claimed.

## Owner-controlled activation — NOT performed

Only after an explicit trusted Owner decision:

1. Establish a **separate Supabase Auth service identity** using supported Supabase Auth Admin tools. Never create a fake client account or put its password/token into GitHub, a public site, a chat or repository.
2. Set **admin-controlled** `app_metadata.imperial_commercial_writer` to `"enabled"`, not user-editable metadata. Limit its use to the private Edge path.
3. Record the actual, existing Auth UUID in `crm_sofft.commercial_writer_identities` with `status='ENABLED'`, an auditable Owner-approved reference (at least 12 characters) and approval timestamp. No placeholder identities are seeded.
4. Obtain a fresh short-lived user JWT after the approved metadata update. Confirm `dry_run=true` on a real eligible issue first; then authorize at most one idempotent draft write and verify the stored hash, unique source, and audit.
5. Only after a genuine buyer approves scope/price/terms: separately authorize HANTER → ASTRA (one federated orchestrator) → LEGION/NCA via AI Passport, Enterprise Skills, Guardian Core, CYBER HAK, Approval Gateway, Audit Ledger, Zero Trust, approved Runtime Domain, independent QA, and client acceptance evidence.

The present system stops **before** the Auth onboarding and before client work. A real customer inquiry is a necessary external dependency; no synthetic issue can count as the first sale.

## Safe rollback / revocation

- Immediate logical stop: change the dedicated ACL row to `DISABLED` and revoke its trusted app metadata, then revoke active user sessions as needed. This never deletes customer records.
- Edge rollback: disable or replace the `imperial-commercial-private-writer` function after reviewing callers.
- Do not drop the CRM schema or broad permissions as a rollback shortcut.

**No Val Town. FREE_ONLY. No changes to SHPAIZMAN-RU or CRYPTO IMPERIAL Ecosystem Boundary.**
