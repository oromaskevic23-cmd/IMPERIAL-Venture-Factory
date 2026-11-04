# Commercial pilot: Skills, Plugins and MCP

This is a local operator tool for **IC-OFFER-001 Automation Failure Audit**. It links the existing offline event-trace auditor to a data-only Enterprise Skill contract, the real IMPERIAL-Plugins workflow-inspection function and an MCP stdio server. It does not connect a real NCA worker, CRM writer, commercial platform or payment account.

## Components and evidence

| Component | Local behavior | Boundary |
| --- | --- | --- |
| IMPERIAL Skill | Validates and resolves the exact `automation-audit` descriptor; its exam is bound by SHA-256. | A valid plan and two synthetic exam cases do not establish professional certification, Owner approval or an AI Passport. |
| IMPERIAL Plugins | Validates the Skill-to-plugin manifest and calls the actual pinned `inspect_n8n_workflow` implementation. | This optional check sees only sanitized node names, types and active status; it does not inspect connections, code, parameters or credentials. |
| MCP | Exposes scope, trace audit, optional workflow inspection and read-only public enquiry discovery through local stdio. | Discovery contacts only the fixed public GitHub API. No HTTP listener, arbitrary URL, file access tool, outbound message, payment or dispatch. |
| Audit and automated QA | Computes existing metrics and separately recomputes the JSON and Markdown results in memory. | The hash covers canonicalized input JSON, not the original file bytes. Automated cross-checks are not human QA or customer acceptance. |

The source lock identifies exact Skill and Plugins Git commits and SHA-256 of the Python files and plugin manifest used at startup. Imports compile verified source bytes rather than cached Python bytecode. The lock is **not a digital signature**: trust the commercial pilot checkout, protect all checkouts from modification, and treat integrity verification as a local control rather than a security certification.

## Run locally

Use Python 3.11+ and three independently reviewed checkouts. Check out the exact commits in `commercial_pilot/local_sources.lock.json`: IMPERIAL-Skill `3ae7ccc86d5e0329723ae3beb5a79ea22cdc3861` and IMPERIAL-Plugins `6c23d839b85bf7ddc80aa9f1df7b2a4ed8328c60`. These components are source-visible under their respective project licenses, not automatically licensed for resale or redistribution.

```sh
export IMPERIAL_SKILL_ROOT=/absolute/path/to/IMPERIAL-Skill
export IMPERIAL_PLUGINS_ROOT=/absolute/path/to/IMPERIAL-Plugins
python3 tools/demo_commercial_mcp.py
python3 -m unittest discover -s integration_tests -p 'test_*.py' -v
```

To also query the public issue source explicitly, run `python3 tools/demo_commercial_mcp.py --discover-public`. The command prints only aggregate counts, while the underlying MCP tool returns sanitized candidate references.

The demo starts the actual MCP process and sends only synthetic fixtures. To connect an MCP-compatible local client, set the same two environment variables and launch `python3 -m commercial_pilot.commercial_mcp` from this checkout. The implemented protocol is MCP `2025-11-25` over newline-delimited JSON-RPC stdio; client compatibility beyond the included protocol tests is not claimed. The server validates both source trees before imports and exits if they are missing, altered or unpinned. Trace analysis and workflow inspection are offline; only the explicitly invoked discovery tool makes a read-only GitHub API request. The server downloads no code and writes no customer files.

The audit accepts a `trace` object of at most 2000 events and 256 KiB after canonicalization, with only `workflow`, `events`, and event `id`, `status`, `duration_ms`. The optional workflow tool accepts only `active` and 1–100 nodes with `name` and `type`. Never send secrets or personal information to these tools. Schema checks do not guarantee that identifiers are anonymous. Confirm the data owner's rights and use an approved private client and workspace before handling any redacted customer data; stdio alone provides no multiuser isolation or secure delivery channel.

## Commercial state

An existing [public enquiry form](https://github.com/oromaskevic23-cmd/IMPERIAL-Venture-Factory/issues/new?template=commercial_audit.yml) is non-binding. Actual qualification, scope, pricing and terms, independent human QA, owner-authorized delivery, customer acceptance and verified payment remain separate. No verified payment provider or authorized CRM writer is created by this integration. No valid AI Passport, live Guardian/Approval Gateway, Audit Ledger, HANTER dispatch, NCA execution or 24/7 service is claimed. The local audit tool is not an authorization mechanism.

Discovery scans up to 300 open issue/PR records and fails explicitly on overflow or unstable duplicates. The response includes sanitized references, not issue text, names or contacts. A result is a candidate for manual review, not an authenticated client or a record in CRM; pagination can change concurrently and the original issue must be rechecked.

Preserve Architect → HANTER → federated orchestrators → scoped NCA; ASTRA is one orchestrator. Maintain Zero Trust, Public/Private Boundary and CRYPTO IMPERIAL Ecosystem Boundary. Production activation requires separately verified identities, permissions, audit, independent QA and the owner's approval.
