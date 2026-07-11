import sqlite3
import logging
import uuid
import csv
import os
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

    def filter_events(self, severity=None, operator_id=None, date_from=None, date_to=None):
        """
        Filter events by one or more criteria.

        Parameters:
            severity     (str)  : e.g. "HIGH", "CRITICAL", "MEDIUM", "LOW"
            operator_id  (str)  : e.g. "operator_A"
            date_from    (str)  : start date in format "YYYY-MM-DD"
            date_to      (str)  : end date in format "YYYY-MM-DD"

        Returns:
            list of matching event dicts
        """
        query = "SELECT * FROM adaptation_events WHERE 1=1"
        params = []

        if severity:
            query += " AND anomaly_severity = ?"
            params.append(severity.upper())

        if operator_id:
            query += " AND operator_id = ?"
            params.append(operator_id)

        if date_from:
            query += " AND timestamp >= ?"
            params.append(date_from)

        if date_to:
            # add end of day so the date_to is inclusive
            query += " AND timestamp <= ?"
            params.append(date_to + "T23:59:59")

        query += " ORDER BY timestamp DESC"

        conn = self._connect()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        return [dict(r) for r in rows]

    def export_to_csv(self, filename=None, severity=None, operator_id=None, date_from=None, date_to=None):
        """
        Export events to a CSV file inside the exports/ folder.
        Optionally filter by severity, operator_id, or date range before exporting.

        Parameters:
            filename     (str)  : custom filename, e.g. "my_report.csv"
                                  defaults to exports/events_YYYY-MM-DD_HHMMSS.csv
            severity     (str)  : filter by severity level
            operator_id  (str)  : filter by operator ID
            date_from    (str)  : filter from date "YYYY-MM-DD"
            date_to      (str)  : filter to date "YYYY-MM-DD"

        Returns:
            path to the exported CSV file
        """
        # get events, filtered if any filters were passed
        events = self.filter_events(
            severity=severity,
            operator_id=operator_id,
            date_from=date_from,
            date_to=date_to
        )

        if not events:
            logging.warning("EXPORT | No events matched the filter. CSV not created.")
            return None

        # make sure the exports folder exists
        os.makedirs("exports", exist_ok=True)

        # build the filename
        if not filename:
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"events_{timestamp_str}.csv"

        filepath = os.path.join("exports", filename)

        # write the CSV
        fieldnames = events[0].keys()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(events)

        logging.info(f"EXPORT | {len(events)} events written to {filepath}")
        return filepath
