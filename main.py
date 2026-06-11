from contextlib import contextmanager
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = "kiln_records.db"

app = FastAPI(title="Pottery Kiln Records", version="0.1.0")


@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS firing_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_code TEXT NOT NULL,
                clay TEXT NOT NULL,
                glaze TEXT NOT NULL,
                target_temp INTEGER NOT NULL,
                actual_curve_note TEXT DEFAULT '',
                kiln_result TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


class BatchCreate(BaseModel):
    work_code: str
    clay: str
    glaze: str
    target_temp: int
    actual_curve_note: str = ""


class ResultUpdate(BaseModel):
    kiln_result: str
    actual_curve_note: Optional[str] = None


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "port": 61201}


@app.post("/batches", status_code=201)
def create_batch(payload: BatchCreate) -> dict:
    with db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO firing_batches
            (work_code, clay, glaze, target_temp, actual_curve_note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.work_code,
                payload.clay,
                payload.glaze,
                payload.target_temp,
                payload.actual_curve_note,
            ),
        )
        row = conn.execute(
            "SELECT * FROM firing_batches WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return row_to_dict(row)


@app.get("/batches")
def list_batches() -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM firing_batches ORDER BY created_at DESC, id DESC"
        ).fetchall()
        return [row_to_dict(row) for row in rows]


@app.get("/batches/{batch_id}")
def get_batch(batch_id: int) -> dict:
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM firing_batches WHERE id = ?", (batch_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Batch not found")
        return row_to_dict(row)


@app.patch("/batches/{batch_id}/result")
def update_result(batch_id: int, payload: ResultUpdate) -> dict:
    with db() as conn:
        current = conn.execute(
            "SELECT * FROM firing_batches WHERE id = ?", (batch_id,)
        ).fetchone()
        if current is None:
            raise HTTPException(status_code=404, detail="Batch not found")
        note = (
            current["actual_curve_note"]
            if payload.actual_curve_note is None
            else payload.actual_curve_note
        )
        conn.execute(
            """
            UPDATE firing_batches
            SET kiln_result = ?, actual_curve_note = ?
            WHERE id = ?
            """,
            (payload.kiln_result, note, batch_id),
        )
        row = conn.execute(
            "SELECT * FROM firing_batches WHERE id = ?", (batch_id,)
        ).fetchone()
        return row_to_dict(row)


@app.delete("/batches/{batch_id}")
def delete_batch(batch_id: int) -> dict:
    with db() as conn:
        cursor = conn.execute("DELETE FROM firing_batches WHERE id = ?", (batch_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Batch not found")
        return {"deleted": batch_id}


@app.get("/works/{work_code}/history")
def work_history(work_code: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM firing_batches
            WHERE work_code = ?
            ORDER BY created_at DESC, id DESC
            """,
            (work_code,),
        ).fetchall()
        return [row_to_dict(row) for row in rows]
