# Patvero Care support runbook

## Safety first

Patvero is an operational record system. It is not an emergency service. If a person is in immediate danger, staff follow the provider's emergency and reportable-event procedures before troubleshooting software. Support must never tell staff to recreate, backdate, delete or silently alter a clinical, MAR, EVV, incident, handover or billing record.

## Intake

Capture: reporter, callback channel, organization/workspace, affected home, UTC and local time, screen/route, request or correlation ID, device/browser/app version, impact, number of people affected, and whether safe paper downtime procedures are active. Do not request clinical narrative, passwords, access codes, card/bank data or identity documents in a ticket.

## Severity and response

| Severity | Examples | Initial response | Escalation |
| --- | --- | --- | --- |
| P0 safety/security | cross-home access, lost/duplicated medication record, active account compromise, corrupted audit history | 15 minutes | Incident commander, security and Care operations immediately |
| P1 critical operations | staff cannot clock in/out, MAR unavailable, incident submission blocked, widespread data conflict | 30 minutes | Engineering and Care operations; start downtime procedure |
| P2 degraded | one workflow impaired with safe workaround | 4 business hours | Product owner and owning engineer |
| P3 request | question, cosmetic issue, enhancement | 1 business day | Normal queue |

## Containment

1. Preserve logs, request IDs and timestamps; do not mutate production data to “make the screen look right.”
2. For suspected unauthorized access, revoke the affected session/token and follow the security incident process.
3. For data-integrity risk, pause the affected mutation path if possible and place the organization on its approved downtime workflow.
4. Communicate known impact, safe workaround and next update time. Do not claim regulatory reporting has occurred unless an authorized provider representative submitted it and evidence exists.
5. Reconcile downtime records through a supervised, auditable process when service is restored.

## Resolution evidence

Every P0/P1 closes with timeline, root cause, affected records, reconciliation evidence, audit review, corrective actions, customer communication, test coverage, owner and due date. A safety event cannot be closed only because the UI is working again.

## Exercise

Before pilot, simulate: API outage during MAR, offline shift clock-out, duplicate mobile submission, stale resident edit, delayed claim acknowledgement, suspected cross-home access and backup restoration. Record timestamps and whether the severity and response targets were met.
