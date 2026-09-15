from database import get_db_connection
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("")
@router.get("/")
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


@router.get("/add")
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


@router.get("/complete")
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