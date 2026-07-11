# Logging Schema Reference
**Module:** Student 5 — Deployment, Logging & Rollback
**File:** `db/living_logic.db` (SQLite)
**Table:** `adaptation_events`

---

## Overview

Every anomaly detected by the system creates one row in `adaptation_events`. That same row is then updated as the event moves through the pipeline: an adaptation is proposed, an operator approves or rejects it, and a rollback is triggered if needed. This means one row = one full lifecycle of an event.

---

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-incremented primary key. Used internally to reference a row across updates. |
| `timestamp` | TEXT | UTC timestamp of when the anomaly was first logged. ISO 8601 format (e.g. `2026-06-17T10:32:00+00:00`). |
| `anomaly_id` | TEXT | Short unique identifier for the anomaly (8-character UUID slice, e.g. `a3f9c12b`). Used for human-readable references. |
| `anomaly_type` | TEXT | String describing what kind of anomaly was detected (e.g. `pressure_spike`, `sensor_spoofing`, `unusual_network_traffic`). |
| `anomaly_severity` | TEXT | Severity level of the anomaly. |
| `source_module` | TEXT | Which module detected the anomaly (e.g. `student1_detector`, `student4_threat`). Defaults to `unknown` if not provided. |
| `adaptation_proposed` | TEXT | Description of the adaptation action suggested in response to the anomaly (e.g. `reduce_valve_flow_by_20pct`). Null until `log_adaptation()` is called. |
| `operator_approved` | INTEGER | Whether an operator approved the adaptation. `1` = approved, `0` = not approved / pending. |
| `operator_id` | TEXT | ID of the operator who approved or rejected the adaptation (e.g. `operator_A`). Null if no decision has been made. |
| `adaptation_deployed` | INTEGER | Whether the adaptation was deployed. `1` = deployed, `0` = not deployed. Set to `1` automatically when `operator_approved=True`. |
| `rollback_triggered` | INTEGER | Whether a rollback was triggered for this event. `1` = yes, `0` = no. |
| `rollback_reason` | TEXT | Human-readable explanation of why the rollback was triggered (e.g. `adaptation caused pressure imbalance`). Null if no rollback. |
| `rollback_status` | TEXT | Outcome of the rollback attempt. Valid values: `SUCCESS`, `FAILED`. Null if no rollback. |

---

## Valid Values

**`anomaly_severity`**
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

**`operator_approved` / `adaptation_deployed` / `rollback_triggered`**
- `0` = false / no
- `1` = true / yes

**`rollback_status`**
- `SUCCESS` — rollback completed without issues
- `FAILED` — rollback was attempted but did not complete successfully
- `null` — no rollback was triggered

---

## Row Lifecycle

A row starts when an anomaly is detected and is updated in place as the event progresses:

```
log_anomaly()         → row created, anomaly fields populated, adaptation fields null
log_adaptation()      → adaptation_proposed, operator_approved, operator_id, adaptation_deployed updated
log_rollback()        → rollback_triggered, rollback_reason, rollback_status updated
```

---

## Example Row (fully resolved)

```json
{
  "id": 1,
  "timestamp": "2026-06-17T10:32:00+00:00",
  "anomaly_id": "a3f9c12b",
  "anomaly_type": "pressure_spike",
  "anomaly_severity": "HIGH",
  "source_module": "student1_detector",
  "adaptation_proposed": "reduce_valve_flow_by_20pct",
  "operator_approved": 1,
  "operator_id": "operator_A",
  "adaptation_deployed": 1,
  "rollback_triggered": 0,
  "rollback_reason": null,
  "rollback_status": null
}
```

---

## Notes

- `anomaly_id` is for human readability; `id` (row ID) is used internally for all update operations.
- A row where `operator_approved=0` and `adaptation_deployed=0` represents a pending or rejected adaptation.
- A row where `rollback_triggered=1` does not automatically set `adaptation_deployed` back to `0` — the rollback is recorded as a separate event on the same row.
