import sqlite3
import logging
import uuid

from datetime import datetime, timezone
from db.init_db import DB_PATH, init_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/system.log"),
        logging.StreamHandler()
    ]
)


class EventLogger:

    def __init__(self):
        init_db()
        self.db_path = DB_PATH

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def log_anomaly(self, anomaly_type, severity, source_module="unknown"):

        anomaly_id = str(uuid.uuid4())[:8]

        timestamp = datetime.now(timezone.utc).isoformat()

        conn = self._connect()
        c = conn.cursor()

        c.execute("""
            INSERT INTO adaptation_events
            (
                timestamp,
                anomaly_id,
                anomaly_type,
                anomaly_severity,
                source_module
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            timestamp,
            anomaly_id,
            anomaly_type,
            severity,
            source_module
        ))

        conn.commit()

        row_id = c.lastrowid

        conn.close()

        logging.info(
            f"ANOMALY LOGGED | "
            f"id={anomaly_id} "
            f"type={anomaly_type} "
            f"severity={severity}"
        )

        return anomaly_id, row_id

    def log_adaptation(
        self,
        row_id,
        adaptation_proposed,
        operator_approved=False,
        operator_id=None
    ):

        deployed = 1 if operator_approved else 0

        conn = self._connect()
        c = conn.cursor()

        c.execute("""
            UPDATE adaptation_events

            SET adaptation_proposed=?,
                operator_approved=?,
                operator_id=?,
                adaptation_deployed=?

            WHERE id=?
        """, (
            adaptation_proposed,
            int(operator_approved),
            operator_id,
            deployed,
            row_id
        ))

        conn.commit()
        conn.close()

        status = "APPROVED" if operator_approved else "PENDING"

        logging.info(
            f"ADAPTATION | "
            f"row={row_id} "
            f"proposal='{adaptation_proposed}' "
            f"status={status}"
        )

    def log_rollback(self, row_id, reason, success=True):

        status = "SUCCESS" if success else "FAILED"

        conn = self._connect()
        c = conn.cursor()

        c.execute("""
            UPDATE adaptation_events

            SET rollback_triggered=1,
                rollback_reason=?,
                rollback_status=?

            WHERE id=?
        """, (
            reason,
            status,
            row_id
        ))

        conn.commit()
        conn.close()

        logging.warning(
            f"ROLLBACK | "
            f"row={row_id} "
            f"reason='{reason}' "
            f"status={status}"
        )

    def get_all_events(self):

        conn = self._connect()

        conn.row_factory = sqlite3.Row

        c = conn.cursor()

        c.execute("""
            SELECT *
            FROM adaptation_events
            ORDER BY timestamp DESC
        """)

        rows = c.fetchall()

        conn.close()

        return [dict(r) for r in rows]