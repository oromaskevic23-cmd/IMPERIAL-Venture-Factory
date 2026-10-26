# IMPERIAL Venture Factory
### Build verified software businesses. Keep the core. Sell transferable assets.

> **Lifecycle: FOUNDATION / Architecture & portfolio specifications.**
> This public repository does **not** mean any of the ten applications has been built, deployed, earned revenue, or been sold.

**IMPERIAL Venture Factory** is a proposed enterprise-grade venture portfolio program within **IMPERIAL Core**. It will develop ten independently deployable B2B software businesses; validate customer demand and repeatable revenue; and prepare saleable, transferable assets. Net proceeds may be reinvested in the strategic core subject to Founder approval and financial review.

**Founder · Owner · Final Architectural Decision Authority:** Alexander Romaskevich — `RomaskevicH`.

## The 10 ventures

| ID | Product | Target workflow | Status |
|:--|:--|:--|:--|
| [VF-01](products/approvedesk/SPEC.md) | **ApproveDesk** | Agency client approvals | `IDEA` |
| [VF-02](products/invoicerelay/SPEC.md) | **InvoiceRelay** | Invoice follow-up workflow | `IDEA` |
| [VF-03](products/csvreconcile/SPEC.md) | **CSVReconcile** | Reconcile data exports | `IDEA` |
| [VF-04](products/quoteflow/SPEC.md) | **QuoteFlow** | Quote-to-acceptance operations | `IDEA` |
| [VF-05](products/renewalradar/SPEC.md) | **RenewalRadar** | Contract and license renewals | `IDEA` |
| [VF-06](products/catalogfix/SPEC.md) | **CatalogFix** | Product feed quality repair | `IDEA` |
| [VF-07](products/marginlens/SPEC.md) | **MarginLens** | Contribution margin analytics | `IDEA` |
| [VF-08](products/tickettriage/SPEC.md) | **TicketTriage** | Human-reviewed support assistance | `IDEA` |
| [VF-09](products/webhookledger/SPEC.md) | **WebhookLedger** | Webhook reliability diagnostics | `IDEA` |
| [VF-10](products/sitesignal/SPEC.md) | **SiteSignal** | Consent-based site monitoring | `IDEA` |

## Venture AutoPilot — governed, not unchecked autonomy

```text
OPPORTUNITY -> DISCOVERY -> VALIDATED -> BUILD -> QA -> PILOT -> RELEASE
                                                   |                |
                                              ProofGraph       EXIT_READY -> SOLD
                  Guardian Core / CYBER HAK -> Approval Gateway -> Audit Ledger
```

**Important:** AutoPilot is a **planned orchestration protocol**, not an operational autonomous production agent. The included Python library validates portfolio structure and provides a **local, fail-closed gate evaluator**; it does not contact external systems, deploy apps, send messages, spend money, or execute sales.

## Enterprise architecture and governance

- **Federated Multi-Orchestrator Architecture**, no unrestricted global executor. ASTRA may coordinate mission planning; ventures retain independent execution boundaries.
- `VELEON ⚡` is the LLM product identity; **MAX is a mode**, not a separate product. AI features are optional and only claimed after live verification.
- `CONSTRUCTOR AI` is the strategic engineering system; `LEGION` and `Nano Core Agents` are scoped professional workers.
- `Guardian Core`, `CYBER HAK`, `Approval Gateway`, `Audit Ledger`, `AI Passport`, `Enterprise Skills`, Zero Trust, Deny by Default, Fail Closed, and ProofGraph form mandatory governance boundaries.
- Public and private artifacts have different access policies. The `CRYPTO IMPERIAL Ecosystem Boundary` prevents operational or financial conflation with venture sales.
- Intellectual property stays partitioned: a product sale must not inadvertently transfer IMPERIAL Core platform rights.
- **FREE_ONLY** until the Founder explicitly approves otherwise. No implicit paid cloud service or model usage.

## Repository map

```text
.github/workflows/                Repeatable free CI
docs/                             Program charter, governance, AutoPilot, release and exit rules
products/<venture>/SPEC.md        Ten independently scoped product contracts
portfolio/ventures.json           Machine-readable portfolio state (all proposed)
venture_fabric/                   Offline policy gate implementation
scripts/                           Offline portfolio validation
tests/                             Permission and policy checks
```

## First execution sequence

1. Confirm repos/IP boundaries, budgets, and customer interview protocols.
2. Interview target buyers before large engineering investment.
3. Build the first independent slice: **ApproveDesk**; reserve CSVReconcile and InvoiceRelay as candidates.
4. Produce real build/test/browser and independent QA evidence.
5. Run privacy/security, support, licensing, and asset transfer checks.
6. Acquire real pilots/payments; only then model valuation or exit.

## How to verify this foundation locally

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_portfolio.py
```

No third-party dependency or external API is needed to run these foundation checks.

## Controls and documents

- [Program charter](docs/PROGRAM_CHARTER.md)
- [Architecture and boundaries](docs/ARCHITECTURE.md)
- [Venture AutoPilot](docs/VENTURE_AUTOPILOT.md)
- [Assurance and release gates](docs/SECURITY_AND_ASSURANCE.md)
- [Commercial validation](docs/COMMERCIAL_PLAYBOOK.md)
- [Asset transfer and exits](docs/EXIT_DILIGENCE.md)
- [Roadmap](docs/ROADMAP.md)
- [Decision 0001](docs/adr/ADR-0001-federated-venture-factory.md)
- [Security policy](SECURITY.md)

**No claims of proven revenue, valuation, live inference, customer contracts, or completed applications are made.**

**License and transfers:** no public open-source license is granted by this repository. Commercial licensing, assignments, and permitted re-use are subject to documented Owner approval and applicable law.
