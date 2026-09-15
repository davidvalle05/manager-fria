import os
import psycopg2
from fastapi import HTTPException


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