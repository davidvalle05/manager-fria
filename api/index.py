from fastapi import FastAPI
from routers import smart_planner, tasks

app = FastAPI(title="Manager Fria AI API", version="2.0")

# Incluir los routers con sus prefijos correspondientes
app.include_router(tasks.router)
app.include_router(smart_planner.router)


@app.get("/")
def home():
  return {
      "status": "online",
      "manager": "fria-ai-backend",
      "modules": ["tasks", "smart_planner"],
  }