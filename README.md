# FastAPI Project

A basic api project using FastAPI + SQLAlchemy + Pydantic + Alembic + PostgreSQL, run with Docker Compose.

## Run

```bash
docker compose up --build
```

API: http://localhost:8000

Interactive docs at: http://localhost:8000/docs

The `users` table is created automatically on startup. 

`docker compose down -v` wipes the database.