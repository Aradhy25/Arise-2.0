.PHONY: setup backend frontend test build docker-up docker-down
setup:
	python3 -m venv .venv
	./.venv/bin/python -m pip install -r backend/requirements.txt
	./.venv/bin/python -m pip install -r frontend/requirements.txt
backend:
	./.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
frontend:
	./.venv/bin/python -m streamlit run frontend/app.py --server.address=0.0.0.0 --server.port=8501
test:
	./.venv/bin/python -m pytest -q backend/tests
build:
	docker compose build
docker-up:
	docker compose up --build
docker-down:
	docker compose down
