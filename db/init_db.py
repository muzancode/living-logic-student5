import sqlite3
import os
import json

DB_PATH = "db/events.db"

SCHEMA_PATH = "schemas/event_log_schema.json"


def init_db():
    os.makedirs("db", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    with open(SCHEMA_PATH, "r") as f:
        schema = json.load(f)

    fields = schema["fields"]

    column_defs = []

    for field_name, field_type in fields.items():
        column_defs.append(f"{field_name} {field_type}")

    sql = f"""
    CREATE TABLE IF NOT EXISTS adaptation_events (
        {", ".join(column_defs)}
    )
    """

    c.execute(sql)

    conn.commit()
    conn.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
    print(f"Database ready at {DB_PATH}")