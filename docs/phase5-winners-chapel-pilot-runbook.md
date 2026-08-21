# Patvero Phase 5 — Winners Chapel Nashville pilot runbook

## Access boundary

- Phase 5 management APIs and the `/church/launch` console are enabled only for `krissbajo@gmail.com`.
- The backend email guard is authoritative. The web navigation check is only a convenience.
- Public widgets, text-to-give resolution, and kiosk sessions remain unavailable until the selected workspace is enrolled and its pilot status is `active`.
- Never put bank account numbers, card data, identity documents, voided checks, or provider secrets into import files, support cases, or launch evidence.

## Before enrollment

1. Confirm Winners Chapel Nashville is the active Patvero workspace.
2. Confirm Stripe Giving onboarding is complete and charges and payouts are enabled.
3. Configure the dedicated Stripe Giving webhook and the `TEXT_GIVING_WEBHOOK_SECRET` through the deployment secret manager.
4. Confirm the production web URL, email sender, SMS sender, webhook worker, database monitoring, and backup alerts are healthy.
5. Record unresolved security findings. The launch gate must remain blocked while any critical finding is open.

## Migration procedure

1. Export members and historical contributions from the source system without payment instruments or identity documents.
2. Save the source export checksum and record count outside Patvero.
3. Run a dry import with a representative sample.
4. Resolve duplicate people before importing contributions. Every contribution must match a member by source ID, verified email, or member number.
5. Run the full provider import. Patvero stores a unique mapping of workspace, provider, record type, and source ID, so rerunning the same export cannot duplicate a person or contribution.
6. Compare source totals and Patvero totals by year, currency, fund, and payment method. Investigate every failed row and retain the import job report.

## Live donation and reconciliation test

1. Create a low-value real donation using the church's public giving page.
2. Confirm Stripe Checkout completes and the donation appears exactly once in Patvero after the signed webhook is processed.
3. Confirm the donor receives the expected receipt and can view the gift in their giving history.
4. Refund the test gift and confirm a separate refund event appears without changing or deleting the original contribution.
5. Confirm the next Stripe payout appears once, matches the processor amount and fees, and can be reconciled by an authorized church finance user.
6. Generate the donor's annual statement and compare its amount to the immutable ledger and source records.
7. Mark reconciliation, receipt, and statement checks `passed` only after evidence is retained.

## Campus payout routing

- Create one campus record per ministry location.
- Store only the Stripe connected-account ID for each campus. Stripe remains responsible for bank and identity information.
- Run a real low-value donation for each routed campus before enabling normal use.
- Never advance beyond the one-church wave while any campus has restricted charges or payouts.

## Public API, webhook, widget, text, and kiosk checks

- API keys must use the minimum scopes, have an owner and expiry, and be copied only once into an approved secret manager.
- Webhook endpoints must be public HTTPS URLs. Verify HMAC signatures, delivery IDs, timestamp freshness, and duplicate handling at the receiver.
- Widget tokens are unguessable. Configure the exact production HTTPS origins and test the iframe from each approved website.
- Text-to-give providers must sign `inboundNumber + "\n" + message` with HMAC-SHA256 and send the value as `x-patvero-text-signature: sha256=<hex>`.
- Kiosk sessions must be campus-specific where possible, expire within 30 days, and use a locked-down browser profile. Revoke the kiosk when a device is lost or reassigned.

## Support and disputes

| Priority | Initial response | Escalation |
| --- | ---: | --- |
| Critical | 15 minutes | Security lead and pilot owner immediately; pause affected functionality |
| High | 1 hour | Pilot owner and payments operator |
| Normal | 1 business day | Assigned support owner |
| Low | 2 business days | Product backlog |

- Stripe dispute events automatically open or update a high-priority `payment_dispute` case and append a ledger event.
- Never close a dispute case based only on the Stripe status. Confirm the ledger, payout effect, supporting evidence, and donor communication.
- For payout, receipt, import, or statement incidents, record provider references without copying protected financial data.
- Set the support readiness check to `passed` only after an on-call owner, escalation contacts, response targets, and this runbook have been tested.

## Backup restoration and disaster recovery

1. Select a recent production backup and record its immutable backup reference.
2. Restore only into a newly created, isolated non-production environment. Never overwrite production for a drill.
3. Verify migration level, row counts, workspace isolation, contribution totals, ledger immutability, object-storage references, and sign-in revocation behavior.
4. Measure recovery point objective (RPO) and recovery time objective (RTO).
5. Destroy the isolated restoration after evidence is retained according to the data-retention policy.
6. Record the drill as `passed` only when all checks succeed; otherwise record `failed`, open a support case, and keep launch blocked.

## Legal review

External qualified counsel must review and explicitly approve:

- payment and subscription terms;
- privacy notices and processor disclosures;
- charitable acknowledgment language and tax disclaimers;
- data retention, deletion, import, export, and termination obligations.

The launch console records the reviewer, result, and notes. It is an evidence register, not legal advice and not a substitute for counsel.

## Staged launch and rollback

1. **One church:** Winners Chapel Nashville only. Daily reconciliation and support review.
2. **Three churches:** advance only after every one-church exit criterion is passed and critical findings are zero.
3. **Ten churches:** repeat campus, payout, support, restoration, and reconciliation verification before advancing.
4. **Commercial:** require approved legal reviews, tested support coverage, passed recovery evidence, verified billing, and no unresolved critical findings.

Pause the pilot when reconciliation diverges, signed webhooks repeatedly fail, payouts become restricted, a critical security issue is opened, or support cannot meet its response target. Pausing must not delete data or invalidate donor access to receipts and statements.

## Exit checklist

- [ ] Member and historical contribution import reconciles to source totals.
- [ ] Real donation, receipt, refund, payout, and annual statement are verified.
- [ ] Signed webhook retries and duplicate events are verified.
- [ ] Campus routing is verified with real low-value gifts.
- [ ] Support and dispute procedures are exercised.
- [ ] Isolated backup restoration passes with measured RPO/RTO.
- [ ] All four legal-review areas are approved by qualified counsel.
- [ ] Open critical security findings equal zero.
- [ ] Pilot operator records each result in `/church/launch` and advances the rollout gate.
