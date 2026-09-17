#!/usr/bin/env bash
set -euo pipefail

echo "DeepGuard AI - macOS/Linux setup"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3.11+ is required. Set PYTHON_BIN to your Python executable."
  exit 1
fi

"$PYTHON_BIN" -m venv .venv
./.venv/bin/python -m pip install --upgrade pip setuptools wheel
./.venv/bin/python -m pip install -r backend/requirements.txt
./.venv/bin/python -m pip install -r frontend/requirements.txt

if [ ! -f backend/.env ]; then
  cat > backend/.env <<'EOF'
DATABASE_URL=mysql+pymysql://deepguard_app:YOUR_URL_ENCODED_PASSWORD@localhost:3306/deepguard
EOF
  echo "Created backend/.env. Set DATABASE_URL before starting the application."
fi

echo "Setup complete."
echo "Start backend: ./.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000"
echo "Start frontend: ./.venv/bin/python -m streamlit run frontend/app.py"
