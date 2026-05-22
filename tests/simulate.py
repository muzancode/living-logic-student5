from logger import EventLogger

logger = EventLogger()

anomaly_id, row_id = logger.log_anomaly(
    anomaly_type="Pressure Spike",
    severity="HIGH",
    source_module="student2_rule_engine"
)

logger.log_adaptation(
    row_id=row_id,
    adaptation_proposed="Reduce pump speed by 30%",
    operator_approved=True,
    operator_id="OP-001"
)

logger.log_rollback(
    row_id=row_id,
    reason="Pressure continued rising",
    success=True
)

events = logger.get_all_events()

for event in events:
    print(event)