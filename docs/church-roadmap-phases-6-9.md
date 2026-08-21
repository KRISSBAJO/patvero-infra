# Patvero Church roadmap — Phases 6–9

The Phase 1–5 product foundation is implemented. Production pilot acceptance is not complete: Winners Chapel Nashville still needs a verified Stripe Giving account and an active pilot state before real-money testing.

## Phase 6 — Giving Operations Center

**Goal:** Give church finance staff one coherent workspace for every giving workflow, informed by the useful parts of Tithe.ly without adding a second application sidebar.

- One horizontal Giving navigation: overview, transactions, recurring gifts, deposits, statements, batches, funds and campaigns, giving form, text-to-give, and settings.
- Searchable and filterable transaction ledger with a detailed transaction panel and auditable refunds.
- Recurring schedule status, last charge, next charge, designation, and cancellation state.
- Deposit reconciliation showing gross receipts, processor fees, refunds, adjustments, net payout, and reconciliation status.
- Annual statements, cash/check batches, fund management, pledge campaigns, giving-form branding, and text-to-give in the same workspace.
- Public form supporting multiple designations, recurring frequency, optional donor-covered fees, and donor contact details before redirecting to Stripe-hosted Checkout.
- Responsive and accessible keyboard, focus, empty, loading, error, and offline states.

**Exit criteria:** Staff can find a gift, inspect its immutable history, refund it, reconcile its payout, manage its fund or recurring schedule, issue a statement, and configure the public giving experience without leaving the Giving workspace.

## Phase 7 — Winners Chapel pilot acceptance

**Goal:** Prove the complete financial and operational workflow with real low-value transactions.

- Complete Stripe Connect onboarding and activate the controlled pilot.
- Verify one-time and recurring gifts, receipts, webhook retries, duplicate delivery handling, refunds, disputes, payouts, and ledger reconciliation.
- Import and reconcile member and historical-contribution data.
- Generate and validate year-end statements.
- Complete accessibility testing with keyboard, screen reader, zoom, contrast, and mobile devices.
- Exercise support escalation, isolated backup restoration, measured RPO/RTO, and rollback.
- Retain evidence in the launch console and keep open critical findings at zero.

**Exit criteria:** A real gift reaches the church account, appears exactly once, produces a receipt, survives refund and payout reconciliation, matches the annual statement, and all launch evidence is approved.

## Phase 8 — Multi-church scale and integrations

**Goal:** Expand safely from one church to three and then ten.

- Multi-campus organizations, separate payout routing, and delegated finance permissions.
- Pushpay, Tithe.ly, and Planning Center importers with resumable validation and duplicate review.
- QuickBooks and accounting synchronization with export parity and reconciliation diagnostics.
- Versioned public API, scoped keys, signed outbound webhooks, retry tooling, and delivery logs.
- Support SLAs, tenant-aware operational dashboards, usage billing, and onboarding playbooks.
- Performance, rate-limit, queue, storage, and restore testing at projected ten-church volume.

**Exit criteria:** Three and then ten churches complete onboarding, import, giving, payout, accounting, and support workflows without cross-tenant exposure or unresolved reconciliation differences.

## Phase 9 — Premium platform and formal readiness

**Goal:** Add premium differentiation and prepare the platform for larger commercial commitments.

- Optional white-label church applications after the multi-tenant Patvero app is proven.
- Advanced giving, attendance, engagement, retention, and campaign analytics.
- Governed automations for donor follow-up, member journeys, volunteer operations, and communications.
- Multi-region recovery architecture, tested failover, regional data controls, and capacity planning.
- Formal security and privacy readiness program, evidence collection, vendor review, penetration testing, and external legal/compliance guidance.

**Exit criteria:** Premium capabilities have measured adoption, white-label releases are maintainable, regional recovery targets are demonstrated, and external readiness reviews have no unresolved critical findings.

