from datetime import date
import os
from fastapi import FastAPI, HTTPException
import psycopg2

app = FastAPI(title="Manager Fria AI API", version="2.0")


def get_db_connection():
  db_url = os.environ.get("DATABASE_URL")
  if not db_url:
    raise HTTPException(
        status_code=500, detail="DATABASE_URL no configurada en el entorno."
    )
  try:
    conn = psycopg2.connect(db_url)
    return conn
  except Exception as e:
    raise HTTPException(
        status_code=500, detail=f"Error conectando a la base de datos: {str(e)}"
    )


@app.get("/")
def home():
  return {
      "status": "online",
      "manager": "fria-ai-backend",
      "modules": ["tasks", "smart_planner"],
  }


# --- MÓDULO 1: TAREAS ---
@app.get("/api/tasks")
def get_tasks():
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute(
      "SELECT id, title, category, status FROM tasks WHERE status = 'pendiente'"
  )
  rows = cur.fetchall()
  cur.close()
  conn.close()

  tasks_list = [
      {"id": row[0], "title": row[1], "category": row[2], "status": row[3]}
      for row in rows
  ]
  return {
      "total_pending": len(tasks_list),
      "tasks": tasks_list,
      "response_persona": (
          f"Tienes {len(tasks_list)} bloques pendientes en la nube."
      ),
  }


@app.get("/api/tasks/add")
def add_task(title: str, category: str = "general"):
  if not title:
    raise HTTPException(
        status_code=400, detail="El título de la tarea es obligatorio."
    )

  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute(
      "INSERT INTO tasks (title, category, status) VALUES (%s, %s, 'pendiente')"
      " RETURNING id;",
      (title, category),
  )
  new_id = cur.fetchone()[0]
  conn.commit()
  cur.close()
  conn.close()

  return {
      "status": "success",
      "message": f"Tarea '{title}' añadida correctamente a la nube.",
      "task_id": new_id,
  }


@app.get("/api/tasks/complete")
def complete_task(title: str):
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute(
      "SELECT id, title FROM tasks WHERE status = 'pendiente' AND LOWER(title)"
      " LIKE LOWER(%s);",
      (f"%{title}%",),
  )
  task = cur.fetchone()

  if not task:
    cur.close()
    conn.close()
    return {
        "status": "not_found",
        "message": f"No se ha encontrado ninguna tarea pendiente con el título '{title}'.",
    }

  task_id, exact_title = task
  cur.execute(
      "UPDATE tasks SET status = 'completada' WHERE id = %s;", (task_id,)
  )
  conn.commit()
  cur.close()
  conn.close()

  return {
      "status": "success",
      "message": f"¡Buen trabajo! Tarea '{exact_title}' marcada como completada.",
  }


# --- MÓDULO 2: PLANIFICADOR INTELIGENTE (SMART PLANNER) ---
@app.get("/api/planner/morning-brief")
def morning_brief():
  conn = get_db_connection()
  cur = conn.cursor()

  # 1. Tareas pendientes
  cur.execute("SELECT title FROM tasks WHERE status = 'pendiente';")
  tasks = cur.fetchall()
  pending_tasks_count = len(tasks)

  # 2. Exámenes próximos
  today = date.today()
  cur.execute(
      "SELECT title, exam_date FROM exams WHERE exam_date >= %s ORDER BY"
      " exam_date ASC LIMIT 2;",
      (today,),
  )
  exams = cur.fetchall()

  # 3. Rutinas fijas
  cur.execute("SELECT title, duration_minutes FROM routines;")
  routines = cur.fetchall()

  cur.close()
  conn.close()

  # Construir locución de voz para el asistente matutino
  greeting = f"Buenos días David. Hoy es {today.strftime('%A %d de %B')}. "
  greeting += f"Tienes {pending_tasks_count} tareas pendientes. "

  if exams:
    next_exam, exam_date = exams[0]
    days_left = (exam_date - today).days
    greeting += f"Aviso importante: Tienes examen de {next_exam} en {days_left} días. "

  if routines:
    routine_names = ", ".join([r[0] for r in routines])
    greeting += f"Tus bloques fijos programados son: {routine_names}."

  return {
      "date": str(today),
      "pending_tasks_count": pending_tasks_count,
      "upcoming_exams": [
          {"title": e[0], "date": str(e[1])} for e in exams
      ],
      "routines_count": len(routines),
      "response_persona": greeting,
  }