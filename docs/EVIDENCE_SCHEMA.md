# Evidence Contract v0.1 — Public Digest / Private Originals

## Public evidence
The public repository may contain stage, artifact type, source commit SHA, timestamp and a hash of redacted evidence. Do not commit personal data, actual customer records, revenue account statements, private prompts or signed agreements.

## Private proof record
```json
{
  "venture_id": "VF-01",
  "mission_id": "private-random-uuid",
  "current_stage": "QA",
  "requested_stage": "PILOT",
  "evidence": [{"kind": "independent_qa", "sha256": "<64-hex>", "storage": "PRIVATE"}],
  "reviewer_identity": "<independent authorized reviewer>",
  "approval_gateway_reference": "<signed and verified off-repo>",
  "audit_ledger_reference": "<immutable protected log record>",
  "policy_version": "0.1"
}
```

## Important assurance levels
1. **Manifest valid** — JSON and spec structures are consistent (current CI can verify).
2. **Metadata gate ready** — hash-looking strings and reference fields are present (offline policy only).
3. **Evidence independently verified** — inspect original artifact, chain of custody, signed permit, reviewer independence (NOT implemented here).
4. **Operationally accepted** — end-to-end tests and secure approval in target environment (NOT implemented here).
5. **Commercially accepted** — paid/customer/deal evidence independently reconciled (NOT implemented here).

Never label level 1 or 2 as level 3–5. An arbitrary SHA-looking digest is not proof of authentic content. The offline evaluator does not have power to launch, spend or sell.
