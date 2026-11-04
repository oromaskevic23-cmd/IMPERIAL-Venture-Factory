# Commercial Pilot 001 — first engagement runbook

This runbook is for a human operator conducting IC-OFFER-001, the existing Automation Failure Audit. A public issue is an enquiry, not a customer contract. The published USD 49–149 range is indicative, non-binding and not verified as a current market price. Agree the actual price, scope, delivery date and payment terms individually before work begins.

## 1. Receive and qualify

1. Review the original public GitHub issue and confirm that it represents a genuine enquiry. Recheck that it is still open and that privacy and scope confirmations are present; automated discovery is only a screening aid and is not a complete privacy assessment.
2. A public issue must never contain credentials, personal records, payment information, confidential workflows or files. If any appear, stop and route to the repository's privacy review process. Do not copy the contents into this repository or logs.
3. Identify the responsible customer and the single workflow to assess. Confirm that the customer can authorize use of the proposed data and the work. Any private communication or data transfer needs an approved private channel; this repository does not provide one.

## 2. Approve terms and prepare data

1. Obtain the owner's agreement to the scope, price, service terms, beneficiary and delivery method. Do not promise remediation, production access, a root cause, or an outcome the offline tool cannot establish.
2. Agree on one synthetic or properly redacted JSON trace: `workflow` plus 1–2000 `events`, each containing only `id`, `status`, and `duration_ms`, with a maximum size of 256 KiB. Opaque IDs should not encode names, email addresses or other sensitive information. Customer data requires a suitable authorized private channel and storage, neither of which is implemented here.
3. The live CRM writer is not enabled for this path. A source discovery draft is not a recorded customer, a signed engagement, or permission to bypass the writer's authorization gates.

## 3. Produce and review

1. Follow the offline commands in [COMMERCIAL_PILOT.md](../COMMERCIAL_PILOT.md). Preserve the source, JSON report, Markdown report and automated receipt in the approved private workspace; do not commit customer files.
2. Have a separate qualified reviewer inspect the scope, input and results. The automated cross-check detects defined inconsistencies but is not independent human QA and does not prove the report is correct for the customer's business.
3. Obtain the owner's authorization for the specific report and approved delivery channel. Share only after those gates are complete. This tool neither delivers reports nor accesses or repairs a customer's systems.

## 4. Close with separate evidence

1. Record the customer's acceptance independently from the work report. Keep any private evidence outside the public repository.
2. An invoice and an accepted report do not prove payment. Mark payment confirmed only after verifying the actual payment provider's transaction, beneficiary, amount, currency and final status. Refunds and disputes require separate review.
3. Do not enter a confirmed payment in CRM unless the authorized writer and its permissions have been independently tested. If a provider or CRM writer is unavailable, leave the respective state unverified; do not infer zero revenue across other systems.

No autonomous agents, outbound messages, charges, subscriptions, token transfers or customer production changes are performed by this runbook.
