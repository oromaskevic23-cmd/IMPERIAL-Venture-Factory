# IMPERIAL Core — First Commercial Pilot (IC-OFFER-001)

**Status:** source-level, FREE_ONLY and owner-gated. NOT a claim of live commercial autonomy, customer acceptance, certified Independent QA, or collected revenue.

## First service

IMPERIAL Core's existing internal offer **IC-OFFER-001** is **Automation Failure Audit**; non-binding indicative price USD 49–149. This pilot makes a reproducible offline diagnostic deliverable with a public non-binding enquiry path. No buyer or sale is invented.

## Bounded commercial flow

1. Prospect submits the **Automation Failure Audit — request an estimate** form under GitHub Issues (GitHub sign-in required). The issue is PUBLIC: absolutely no credentials, personal data, confidential files, payment information, private URLs or trade secrets.
2. Authorized operator triages the request and records a DRAFT scope in CRM-SOFFT. No automatic integration with live CRM is claimed.
3. Architect approves scope, price, contract, beneficiary and use of synthetic/redacted test fixtures.
4. ASTRA routes an authorized work packet through HANTER/federated orchestrators to LEGION / Nano Core Agents; execution requires AI Passport, Enterprise Skills, Guardian Core, CYBER HAK, Approval Gateway, permitted Runtime Domain, ProofGraph and Audit Ledger. These live federation gates are NOT implemented by this pilot.
5. Independent reviewer verifies outputs and limitations and owner approves customer delivery. Automated checksum review is NOT equivalent to independent human QA.
6. Client acceptance and payment are evidenced separately; PAYMENT_CONFIRMED requires verified external provider receipt.

**No spam, unsolicited messages, live customer changes, payments, automatic billing, scraping authenticated systems, or paid APIs.** SHPAIZMAN Brother Edition is a separate operation and beneficiary; never blend its SHP-SVC offers or payout routes into IMPERIAL Core.

## Run first verified work package locally

Requires Python 3.11+, no third-party modules or network connection:

    python -m unittest discover -s commercial_pilot -p 'test_*.py' -v
    python commercial_pilot/audit.py commercial_pilot/examples/synthetic_trace.json --out /tmp/imperial-commercial-audit
    python commercial_pilot/verify.py commercial_pilot/examples/synthetic_trace.json /tmp/imperial-commercial-audit/report.json --receipt /tmp/imperial-commercial-audit/qa_receipt.json

Artifacts:
- report.json — input SHA-256, counts, recommendations, independent QA NOT_YET_VERIFIED, revenue 0
- report.md — readable review and suggested checks
- qa_receipt.json — separately computed automated QA hashes; NOT a human signoff

Input: JSON workflow ID and event records with only ID, status, duration_ms. Unknown fields (including possible secrets) are rejected; reports copy no raw input data. Maximum 2000 events and 256 KiB. No network access.

These traces can reveal duplicate IDs, HTTP 429, 5xx, timeouts and latency anomalies, but cannot independently establish downstream success or remediate a live customer integration.

## Release and security gates

- Public issue template becomes available only after merge to repository default branch; issues must remain enabled.
- No guaranteed price/delivery/contract by filing an issue.
- The GitHub issue → CRM-SOFFT bridge is merged as source code. GitHub Actions can discover public enquiries read-only. A narrow Edge Function is deployed, but the read-only 30 October 2026 check found zero enabled writer identities; live authenticated writing and end-to-end commercial execution remain unverified.
- Source changes in a pull request do not update the deployed Edge Function. Its independently deployed version must be verified and reviewed before any writer is enabled.
- GitHub Actions run offline tests and sample lab audit, not live 24/7 NCA execution.
- Approval Gateway, Owner Kill Switch, Zero Trust and Public/Private Boundary stay intact.
- Crypto IMPERIAL ecosystem remains separate; no payouts or tokens involved.
- No production release until independent QA, owner-approved terms, lawful payment route and evidence review.
- KPI: one authentic client inquiry → agreed scope → verified deliverable → acceptance → independently confirmed nonzero payment. No fictitious payment or client data.
