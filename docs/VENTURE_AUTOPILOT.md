# Venture AutoPilot v0.1 — Policy & Gate Specification

**Status:** conceptual operational model + offline validator implementation. Not a running external-agent service.

## Seven operating phases
1. **DISCOVER**: capture 10 candidate interviews, specific pain evidence, competitor alternatives and buyer/decision maker roles. Do not invent demand.
2. **DESIGN**: define acceptance contract, security/data classification, pricing hypothesis, cost ceiling, license audit, exit boundary and architecture ADR.
3. **BUILD**: CONSTRUCTOR AI engineering workers under scoped permissions; isolated development, tests and incremental proof.
4. **VERIFY**: independent QA against user workflow; CYBER HAK threat review; Guardian Core policy evidence; ProofGraph acceptance.
5. **PILOT**: permissioned real customer use; signed terms, privacy notices and legitimate billing or clearly free pilot.
6. **GROW**: monitor retention, support cost, gross margin, incidents, uptime and renewals, with evidence-driven iteration.
7. **EXIT**: prepare buyer-ready diligence; clean data-room materials; Founder reviews valuation and assigns rights under a written contract.

## Machine states and allowed movement
```text
IDEA -> DISCOVERY -> VALIDATED -> BUILD -> QA -> PILOT -> RELEASED -> EXIT_READY -> SOLD
```
No skip-ahead. A failed gate leaves the stage unchanged. Reopening a previously passed stage requires an approved corrective-action record, not silent rollback.

## Guarded gates
| Next stage | Required evidence (examples) | Human decision |
| --- | --- | --- |
| DISCOVERY | Research brief + budget cap | Scope authorization |
| VALIDATED | Interview notes, validation summary | Product owner |
| BUILD | Product spec, architecture + threat plan | Engineering approval |
| QA | Build, unit/integration proof, artifact hash | Independent QA |
| PILOT | Privacy, legal terms, customer approval, E2E | Approval Gateway |
| RELEASED | Security + independent release verdict, rollback | Production approval |
| EXIT_READY | Verified revenue/cost ledger or explicitly pre-revenue disclosure; licenses; clean IP | Founder |
| SOLD | Written transfer instrument and verified settlement | Founder only |

## Scoped NCA team
Researcher, Product Planner, Engineer, Tester, Independent QA, Security Reviewer, Growth Analyst, Commercial Analyst, Exit Coordinator. Role counts are dynamic and capability-scoped, not fixed global superusers.

## What AutoPilot cannot do by default
- No autonomous payments, token transactions, domain purchases, hidden deployments, unsolicited marketing, buyer impersonation, transfer of IP or customer data.
- No self-approved review, secret extraction, unlimited crawling, unapproved model provider usage or bypass of billing limits.
- No pretence that a saved state is a verified production deployment.

## Evidence contract
Every gate record binds: venture ID, proposed stage, task ID, independent reviewer, approved capability, dated evidence pointer or cryptographic digest, decision, UTC timestamp, and policy version. Store private raw evidence outside this public repo. The included code implements only validation and offline gate planning, not cryptographic permit verification.

## Failure handling
Deny by default; explain missing evidence; store failed attempt in a protected Audit Ledger when deployed; preserve old release; manual incident escalation and rollback.
