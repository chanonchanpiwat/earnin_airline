.PHONY: init dev migrate test docker-up

init:
	uv sync

dev:
	uv run fastapi run earnin_airline/app.py

migrate:
	docker compose exec -it postgres bash -c "/home/scripts/exec_sql.sh schema.sql"

docker-up:
	docker compose -f docker-compose-ci.yml up -d

test:
	uv run pytest -sv
