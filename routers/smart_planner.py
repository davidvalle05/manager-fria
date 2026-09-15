from datetime import date
from database import get_db_connection
from fastapi import APIRouter

router = APIRouter(prefix="/api/planner", tags=["Smart Planner"])


@router.get("/morning-brief")
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