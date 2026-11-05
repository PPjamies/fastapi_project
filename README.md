# profile-service

A small monorepo used as a test bed for the Docs Agent. It contains one service, the **Profile API**: create, read, update, delete and list (CRUDL) person profiles, stored in PostgreSQL.

Stack: FastAPI, Pydantic, SQLAlchemy, Alembic, Pytest, PostgreSQL 16, Docker Compose.

## Run it

```bash
make up      # build and start Postgres + the API on http://localhost:8000
make seed    # load 3 sample profiles
make logs    # follow API logs
make down    # stop (keeps data); `make reset` also deletes the database
```

Then open http://localhost:8000/docs for interactive API docs, or fetch the spec at http://localhost:8000/openapi.json.

## Endpoints

| Method | Path | Does |
|---|---|---|
| GET | `/health` | API and database status |
| GET | `/v1/profiles` | List profiles (`page`, `page_size`, `last_name`, `email`) |
| POST | `/v1/profiles` | Create a profile |
| GET | `/v1/profiles/{profile_id}` | Get one profile |
| PATCH | `/v1/profiles/{profile_id}` | Update some fields |
| DELETE | `/v1/profiles/{profile_id}` | Delete a profile |

Full user docs will live in `docs/` once the v1.0.0 baseline is written.

## Develop and test without Docker

```bash
cd services/profile-api
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q                     # uses in-memory SQLite by default

# against Postgres instead:
TEST_DATABASE_URL=postgresql+psycopg://profile:profile@localhost:5432/profiles_test pytest -q
```

## Layout

```
docker-compose.yml          Postgres + API
services/profile-api/
  app/main.py               FastAPI app
  app/constants.py          shared limits and defaults (page size, patterns)
  app/profiles/             model, Pydantic schemas, routes
  migrations/               Alembic migrations
  tests/                    Pytest suite
```

## Database changes

```bash
cd services/profile-api
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

The container runs `alembic upgrade head` automatically on start.
