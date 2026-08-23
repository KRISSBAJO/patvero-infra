# Care backup restoration and disaster recovery

## Required protections

- Encrypted PostgreSQL backups with retention agreed by legal/security.
- Object-storage versioning and lifecycle rules for resident/incident evidence.
- Backup credentials separated from production runtime credentials.
- Restore access limited to named operators with MFA and audited use.
- A documented RPO/RTO approved by the Care operational owner; defaults must not be invented by engineering.

## Quarterly isolated restore drill

1. Select a dated database backup and matching object-store recovery point.
2. Create an isolated, non-production network and a database whose name ends in `_restore_drill`.
3. Run `liveKit-be/deploy/backend/care-restore-drill.sh` with the explicit safety acknowledgement.
4. Apply the application migrations expected by that release.
5. Validate workspace/home/resident boundaries, encrypted-field readability through the application, shift/MAR/incident counts, version chains, ledger balance, claim transmission/remittance links and audit-event continuity.
6. Restore a sample of object evidence and verify checksum, authorization and malware-scan state.
7. Measure restore start, database ready, application ready and reconciliation complete times.
8. Destroy the isolated environment using the approved data-disposal procedure.

## Pass criteria

- No command targets production.
- Database and object evidence recover to the same logical point.
- Critical Care records are present once, decrypt correctly through the application and remain scoped to their workspace/home.
- Immutable/versioned histories and financial ledgers reconcile.
- Measured RPO/RTO are within the approved values.
- A second operator signs the evidence and all exceptions have owners and deadlines.

Until a drill is executed and signed, backup restoration is **not passed**.
