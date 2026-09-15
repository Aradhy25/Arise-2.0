.PHONY: setup dev backend frontend test build docker-up docker-down

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r backend/requirements.txt
	cd frontend && npm ci

backend:
	. .venv/bin/activate && uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "Start backend and frontend in separate terminals: make backend / make frontend"

test:
	. .venv/bin/activate && pytest -q backend/tests

build:
	cd frontend && npm run build

docker-up:
	docker compose up --build

docker-down:
	docker compose down
