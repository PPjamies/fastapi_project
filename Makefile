.PHONY: up down reset logs seed test

up:            ## Build and start Postgres and the API
	docker compose up --build -d

down:          ## Stop everything (keeps data)
	docker compose down

reset:         ## Stop everything and delete the database volume
	docker compose down -v

logs:
	docker compose logs -f profile-api

seed:          ## Load sample profiles
	docker compose exec profile-api python -m app.seed

test:          ## Run the API tests (needs Python + requirements-dev.txt installed)
	cd services/profile-api && python -m pytest -q
