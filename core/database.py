import sqlite3
import hashlib
import os
from datetime import datetime
from contextlib import contextmanager
from typing import Optional

# DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "medicare.db")
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, "medicate.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                blood_group TEXT,
                contact TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                disease TEXT NOT NULL,
                inputs_json TEXT NOT NULL,
                probability REAL NOT NULL,
                risk_score REAL NOT NULL,
                result TEXT NOT NULL,
                advice TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        c.execute("CREATE INDEX IF NOT EXISTS idx_pred_user_disease ON predictions(user_id, disease, created_at)")


def hash_password(password: str) -> str:
    salt = "medicare_ai_salt_v1"
    return hashlib.sha256((salt + password).encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def create_user(full_name: str, username: str, email: str, password: str,
                age: Optional[int], gender: Optional[str],
                blood_group: Optional[str], contact: Optional[str]) -> Optional[int]:
    try:
        with get_conn() as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO users (full_name, username, email, password_hash, age, gender, blood_group, contact, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    full_name.strip(),
                    username.strip().lower(),
                    email.strip().lower(),
                    hash_password(password),
                    age,
                    gender,
                    blood_group,
                    contact,
                    datetime.utcnow().isoformat(),
                ),
            )
            return c.lastrowid
    except sqlite3.IntegrityError:
        return None


def authenticate_user(identifier: str, password: str):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (identifier.strip().lower(), identifier.strip().lower()),
        )
        row = c.fetchone()
        if not row:
            return None
        if verify_password(password, row["password_hash"]):
            return dict(row)
        return None


def get_user_by_id(user_id: int):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        return dict(row) if row else None


def update_user_profile(user_id: int, full_name: str, age: int, gender: str,
                        blood_group: str, contact: str) -> None:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            UPDATE users SET full_name = ?, age = ?, gender = ?, blood_group = ?, contact = ?
            WHERE id = ?
            """,
            (full_name, age, gender, blood_group, contact, user_id),
        )


def save_prediction(user_id: int, disease: str, inputs_json: str,
                    probability: float, risk_score: float, result: str,
                    advice: str) -> int:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO predictions (user_id, disease, inputs_json, probability, risk_score, result, advice, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                disease,
                inputs_json,
                float(probability),
                float(risk_score),
                result,
                advice,
                datetime.utcnow().isoformat(),
            ),
        )
        return c.lastrowid


def get_user_predictions(user_id: int, disease: Optional[str] = None, limit: Optional[int] = None):
    with get_conn() as conn:
        c = conn.cursor()
        sql = "SELECT * FROM predictions WHERE user_id = ?"
        params = [user_id]
        if disease:
            sql += " AND disease = ?"
            params.append(disease)
        sql += " ORDER BY created_at DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        c.execute(sql, params)
        return [dict(r) for r in c.fetchall()]


def get_latest_prediction(user_id: int, disease: str):
    rows = get_user_predictions(user_id, disease=disease, limit=1)
    return rows[0] if rows else None


def get_previous_prediction(user_id: int, disease: str, before_id: int):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT * FROM predictions
            WHERE user_id = ? AND disease = ? AND id < ?
            ORDER BY id DESC LIMIT 1
            """,
            (user_id, disease, before_id),
        )
        row = c.fetchone()
        return dict(row) if row else None


def delete_prediction(pred_id: int, user_id: int) -> None:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM predictions WHERE id = ? AND user_id = ?", (pred_id, user_id))


def count_predictions(user_id: int):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT disease, COUNT(*) as c FROM predictions WHERE user_id = ? GROUP BY disease",
            (user_id,),
        )
        return {r["disease"]: r["c"] for r in c.fetchall()}
