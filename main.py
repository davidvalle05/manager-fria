from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Manager Fria Cloud API", version="3.0")

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.get("/")
def read_root():
    return {"status": "online", "persona": "manager_fria", "mode": "cloud_24_7"}

@app.get("/api/tasks/add")
def create_single_task_get(title: str, category: str = "trabajo"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, category, scheduled_for, duration_minutes, status, impact_score) VALUES (%s, %s, %s, %s, %s, %s)",
            (title, category, "2026-09-12T12:00:00", 60, "pendiente", 3)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "message": f"Tarea '{title}' añadida a la agenda en la nube."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))