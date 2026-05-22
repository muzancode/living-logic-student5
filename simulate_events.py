from logger import EventLogger
import time

el = EventLogger()

print("\n--- Scenario 1: Normal adaptation, operator approved ---")

aid, rid = el.log_anomaly(
    "pressure_spike",
    "HIGH",
    "student1_detector"
)

time.sleep(0.5)

el.log_adaptation(
    rid,
    "reduce_valve_flow_by_20pct",
    operator_approved=True,
    operator_id="operator_A"
)

print(f"Event {rid} complete.\n")

print("--- Scenario 2: Adaptation deployed, then rolled back ---")

aid2, rid2 = el.log_anomaly(
    "sensor_spoofing",
    "CRITICAL",
    "student1_detector"
)

time.sleep(0.5)

el.log_adaptation(
    rid2,
    "isolate_sensor_node_7",
    operator_approved=True,
    operator_id="operator_B"
)

time.sleep(0.5)

el.log_rollback(
    rid2,
    "adaptation caused pressure imbalance",
    success=True
)

print(f"Event {rid2} rolled back.\n")

print("--- Scenario 3: Adaptation proposed but not approved ---")

aid3, rid3 = el.log_anomaly(
    "unusual_network_traffic",
    "MEDIUM",
    "student4_threat"
)

el.log_adaptation(
    rid3,
    "block_external_comms",
    operator_approved=False
)

print(f"Event {rid3} pending approval.\n")

print("--- All events in database ---")

for e in el.get_all_events():

    print(
        f"[{e['timestamp']}] "
        f"{e['anomaly_type']} | "
        f"deployed={e['adaptation_deployed']} | "
        f"rollback={e['rollback_triggered']} | "
        f"approved={e['operator_approved']}"
    )