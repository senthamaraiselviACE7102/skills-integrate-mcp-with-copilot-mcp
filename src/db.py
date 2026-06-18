"""SQLite persistence layer for activities and participants."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data" / "school.db"
MIGRATION_PATH = BASE_DIR / "migrations" / "001_initial_schema.sql"
SEED_PATH = BASE_DIR / "data" / "activities_seed.json"


class ActivityNotFoundError(Exception):
    pass


class AlreadySignedUpError(Exception):
    pass


class NotSignedUpError(Exception):
    pass


class ActivityFullError(Exception):
    pass


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _connect() as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        migration_sql = MIGRATION_PATH.read_text(encoding="utf-8")
        conn.executescript(migration_sql)

        activity_count = conn.execute("SELECT COUNT(*) AS count FROM activities").fetchone()["count"]
        if activity_count == 0:
            _seed_database(conn)

        conn.commit()


def _seed_database(conn: sqlite3.Connection) -> None:
    seed_payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    for activity in seed_payload:
        cursor = conn.execute(
            """
            INSERT INTO activities (name, description, schedule, max_participants)
            VALUES (?, ?, ?, ?)
            """,
            (
                activity["name"],
                activity["description"],
                activity["schedule"],
                activity["max_participants"],
            ),
        )
        activity_id = cursor.lastrowid

        for email in activity.get("participants", []):
            conn.execute(
                """
                INSERT INTO participants (activity_id, email)
                VALUES (?, ?)
                """,
                (activity_id, email),
            )


def fetch_activities() -> dict[str, dict[str, Any]]:
    with _connect() as conn:
        activity_rows = conn.execute(
            """
            SELECT id, name, description, schedule, max_participants
            FROM activities
            ORDER BY name ASC
            """
        ).fetchall()

        participants_rows = conn.execute(
            """
            SELECT activity_id, email
            FROM participants
            ORDER BY email ASC
            """
        ).fetchall()

    participants_by_activity: dict[int, list[str]] = {}
    for row in participants_rows:
        participants_by_activity.setdefault(row["activity_id"], []).append(row["email"])

    result: dict[str, dict[str, Any]] = {}
    for row in activity_rows:
        result[row["name"]] = {
            "description": row["description"],
            "schedule": row["schedule"],
            "max_participants": row["max_participants"],
            "participants": participants_by_activity.get(row["id"], []),
        }

    return result


def signup_for_activity(activity_name: str, email: str) -> None:
    with _connect() as conn:
        activity = conn.execute(
            """
            SELECT id, max_participants
            FROM activities
            WHERE name = ?
            """,
            (activity_name,),
        ).fetchone()

        if activity is None:
            raise ActivityNotFoundError

        existing_signup = conn.execute(
            """
            SELECT 1
            FROM participants
            WHERE activity_id = ? AND email = ?
            """,
            (activity["id"], email),
        ).fetchone()
        if existing_signup:
            raise AlreadySignedUpError

        current_count = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM participants
            WHERE activity_id = ?
            """,
            (activity["id"],),
        ).fetchone()["count"]
        if current_count >= activity["max_participants"]:
            raise ActivityFullError

        conn.execute(
            """
            INSERT INTO participants (activity_id, email)
            VALUES (?, ?)
            """,
            (activity["id"], email),
        )
        conn.commit()


def unregister_from_activity(activity_name: str, email: str) -> None:
    with _connect() as conn:
        activity = conn.execute(
            """
            SELECT id
            FROM activities
            WHERE name = ?
            """,
            (activity_name,),
        ).fetchone()

        if activity is None:
            raise ActivityNotFoundError

        deleted = conn.execute(
            """
            DELETE FROM participants
            WHERE activity_id = ? AND email = ?
            """,
            (activity["id"], email),
        )
        if deleted.rowcount == 0:
            raise NotSignedUpError

        conn.commit()
