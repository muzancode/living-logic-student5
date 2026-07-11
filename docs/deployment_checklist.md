# Adaptation Deployment Checklist
**Module:** Student 5 — Deployment, Logging & Rollback
**Version:** 1.0 (prototype)

---

## Purpose

This checklist defines the conditions that must be satisfied before, during, and after an adaptation is deployed. It is the human-facing governance layer on top of the logging system.

---

## Pre-Deployment

Before any adaptation is deployed, confirm all of the following:

- [ ] Anomaly has been reviewed — type, severity, and source module are recorded in the event log
- [ ] Adaptation proposal is clearly described and logged (`adaptation_proposed` field is not null)
- [ ] Severity level is appropriate — CRITICAL and HIGH anomalies require immediate operator attention before deployment
- [ ] Operator has reviewed the proposed adaptation
- [ ] Operator approval is recorded — `operator_id` and `operator_approved=1` are set in the event log
- [ ] Rollback plan is understood — the operator knows what action reverses this adaptation if needed

---

## Deployment

At the moment of deployment:

- [ ] `adaptation_deployed` is set to `1` in the event log
- [ ] Deployment timestamp is confirmed (captured automatically via `timestamp` field at anomaly creation)
- [ ] Source module is correctly identified in the log (`source_module` field)

---

## Post-Deployment

After the adaptation has been deployed, monitor and confirm:

- [ ] System behavior is stable — no secondary anomalies have been detected
- [ ] No new CRITICAL or HIGH anomalies have emerged in the observation window
- [ ] If behavior is unsafe → trigger rollback immediately via `log_rollback()` with a clear reason string
- [ ] Final status is confirmed in the event log:
  - Successful deployment: `rollback_triggered=0`
  - Rolled back: `rollback_triggered=1`, `rollback_status=SUCCESS` or `FAILED`

---

## Rollback Checklist (if triggered)

If a rollback is needed:

- [ ] Rollback reason is clearly documented (e.g. `"adaptation caused pressure imbalance"`)
- [ ] `log_rollback()` is called with `row_id`, `reason`, and `success` status
- [ ] `rollback_status` is confirmed as `SUCCESS` or `FAILED`
- [ ] If `FAILED` — flag for immediate operator review, do not close the event

---

## Notes

- All checklist steps correspond to fields in the `adaptation_events` table — see `logging_schema.md` for field definitions.
- In the current prototype, operator approval is simulated. In production, this would be gated by a real approval interface.
- An adaptation should never be marked as deployed (`adaptation_deployed=1`) without a corresponding `operator_approved=1`.
