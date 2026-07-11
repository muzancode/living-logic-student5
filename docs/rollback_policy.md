# Rollback Policy
**Module:** Student 5 — Deployment, Logging & Rollback
**Version:** 1.0 (prototype)

---

## Purpose

This document defines when a rollback is triggered, who can authorize it, what gets logged, and what a successful rollback looks like. It exists to ensure that any adaptation deployment can be safely undone and that all rollback activity is fully traceable.

---

## When Is a Rollback Triggered?

A rollback should be triggered when any of the following conditions are met after an adaptation has been deployed:

1. **Unsafe post-deployment behavior** — the deployed adaptation causes a secondary anomaly or makes system behavior worse (e.g. a valve adjustment causes a pressure imbalance elsewhere).
2. **Operator-initiated rollback** — an operator manually decides to reverse a deployed adaptation, regardless of system state.
3. **CRITICAL severity escalation** — a new CRITICAL anomaly is detected that is directly related to the deployed adaptation.
4. **Failed adaptation** — the adaptation did not achieve its intended effect within the expected observation window.

> In the current prototype, rollbacks are triggered manually via `log_rollback()`. Automated trigger logic based on the above conditions is planned for a future iteration.

---

## Who Can Authorize a Rollback?

In the current prototype, rollbacks are initiated programmatically and the `operator_id` field records which operator is responsible. In a production system:

- Any operator with deployment authority can trigger a rollback.
- The triggering operator's ID must be recorded.
- Rollbacks do not require a second approval — speed of recovery takes priority.

---

## What Gets Logged During a Rollback?

When `log_rollback()` is called, the following fields are updated on the existing event row:

| Field | Value |
|---|---|
| `rollback_triggered` | `1` |
| `rollback_reason` | Human-readable string explaining why |
| `rollback_status` | `SUCCESS` or `FAILED` |

The original deployment record (anomaly type, severity, operator approval, adaptation proposed) is preserved. Rollback data is added to the same row — nothing is deleted.

---

## What Counts as a Successful Rollback?

- `SUCCESS` — the system was returned to its pre-adaptation state without further issues.
- `FAILED` — the rollback was attempted but could not fully restore the previous state, or caused additional problems.

Both outcomes are logged. A `FAILED` rollback should be flagged for immediate operator review.

---

## Rollback Scenarios (tested)

| Scenario | Anomaly Type | Trigger Reason | Outcome |
|---|---|---|---|
| 1 | `sensor_spoofing` (CRITICAL) | Adaptation caused pressure imbalance | `SUCCESS` |

Additional scenarios to be added (partial rollback, failed rollback, cascading failure).

---

## Limitations (prototype stage)

- Rollback does not currently reverse physical system state — it only logs that a rollback occurred.
- There is no automatic trigger mechanism yet; rollbacks must be called manually.
- No timeout or escalation policy is implemented (e.g. no alert if rollback fails and no operator responds).

These are known gaps to be addressed before integration testing in Week 3.
