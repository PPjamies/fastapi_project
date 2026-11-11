# profile-service

A basic CRUD API for user profiles. FastAPI + SQLAlchemy + PostgreSQL, run with Docker Compose.

## Run

```bash
docker compose up --build
```

API: http://localhost:8000 — interactive docs at http://localhost:8000/docs

The `profiles` table is created automatically on startup. `docker compose down -v` wipes the database.

## Endpoints

| Method | Path | Does |
|---|---|---|
| POST | `/profiles` | Create a profile |
| GET | `/profiles` | List all profiles |
| GET | `/profiles/{id}` | Get one profile |
| PUT | `/profiles/{id}` | Replace a profile |
| DELETE | `/profiles/{id}` | Delete a profile |

Profile body:

```json
{ "first_name": "Ada", "last_name": "Lovelace", "email": "ada@example.com", "phone": "+442071234567" }
```

`phone` is optional. Emails must be unique (duplicate → 409).
