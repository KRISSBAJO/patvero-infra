# Supervised Care pilot acceptance

## Scope

Use a limited home, named staff, test/synthetic people where possible, approved downtime packets and daily supervision. Production clinical data must not be imported merely to make a demonstration realistic.

## Required scenarios

- Role and home assignment: every negative cross-home/read/write case is denied and audited.
- Full shift: assignment, claim, clock-in, bedside documentation, MAR/PRN/controlled count, handover, clock-out, supervisor review and amendment.
- Safety event: capture, attachments, investigation, corrective actions, independent closure and required external submission by authorized staff.
- Connectivity: offline capture, reconnect, exactly-once synchronization and supervisor reconciliation.
- Billing: accepted EVV, authorization, claim transmission receipt, 999/277CA, 835, denial/appeal and reconciliation.
- Accessibility: keyboard-only, screen reader, zoom/reflow, visible focus, error recovery and reduced motion on representative desktop and mobile devices.
- Operations: support simulation, monitoring alert, backup restore drill and downtime reconciliation.

## Daily evidence

Record scenario, actor role, device, result, request IDs, defects, severity, workaround and reviewer. Clinical supervisors—not engineers alone—decide whether workflow behavior is safe and usable.

## Exit decision

Pilot passes only when there are no unresolved Critical findings, no unaccepted High safety/security findings, reconciliation is complete, WCAG review is signed, support and restore exercises pass, and legal/operations owners approve launch in `phase-4-launch-readiness.md`.
