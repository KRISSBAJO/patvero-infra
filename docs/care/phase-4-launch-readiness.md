# Care Phase 4 launch readiness

This is the release gate for Patvero Care. A deployed feature is not evidence that the service is safe to launch. Every row needs an owner, dated evidence, reviewer, and an explicit pass/fail decision.

## Product and accessibility gate

| Control | Required evidence | Status |
| --- | --- | --- |
| Shift-first dashboard | Staff pilot demonstrates unassigned, active, overdue, handover and safety-exception work | Implemented locally; pilot pending |
| Readable baseline | Care content is 14–16px at 100% zoom and remains usable at 200% zoom | Implemented locally; manual review pending |
| Responsive tables | 320px, 768px and desktop screenshots for dashboard, MAR, incidents, training and finance | Implemented locally; visual baseline pending |
| Keyboard operation | Skip-through test for navigation, tabs, dialogs, tables and all form actions | Shared controls implemented; full audit pending |
| WCAG 2.2 AA | Automated scan plus a manual screen-reader, reflow, contrast, focus and error-identification review | Not passed |
| Safe edits | destructive confirmations, retained undo where safe, non-clinical autosave and stale-write rejection | Implemented in the initial high-risk paths; scenario review pending |

WCAG conformance is assessed against the current [W3C WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/). Automated scans are evidence, not a conformance decision.

## Operational gate

The following remain release blockers until the linked runbooks have signed evidence:

- Backup restoration drill: [backup-and-dr.md](./backup-and-dr.md)
- Support simulation and escalation: [support-runbook.md](./support-runbook.md)
- Supervised pilot acceptance: [pilot-acceptance.md](./pilot-acceptance.md)
- Legal and regulatory review: [legal-review.md](./legal-review.md)
- No open Critical or High safety/security issue without a written, time-bound risk acceptance by the accountable executive.

## Decision record

| Field | Value |
| --- | --- |
| Candidate version/commit |  |
| Environment |  |
| Pilot organization |  |
| Accessibility reviewer/date |  |
| Restore drill reviewer/date |  |
| Support lead/date |  |
| Legal reviewer/date |  |
| Clinical/operations owner/date |  |
| Security owner/date |  |
| Final decision | **NOT APPROVED** until every gate above has passed |
