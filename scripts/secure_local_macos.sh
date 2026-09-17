#!/usr/bin/env bash
set -euo pipefail

# DeepGuard AI — secure local HTTPS launcher for macOS.
# Uses mkcert to create a locally trusted certificate for localhost.
# Certificates and the private key are stored outside Git tracking.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CERT_DIR="$ROOT_DIR/.cert"
CERT_FILE="$CERT_DIR/localhost.pem"
KEY_FILE="$CERT_DIR/localhost-key.pem"
CONFIG_DIR="$ROOT_DIR/.streamlit"
CONFIG_FILE="$CONFIG_DIR/config.toml"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required. Install it from https://brew.sh/ and run this script again."
  exit 1
fi

if ! command -v mkcert >/dev/null 2>&1; then
  echo "Installing mkcert..."
  brew install mkcert
fi

mkdir -p "$CERT_DIR" "$CONFIG_DIR"

mkcert -install

if [[ ! -f "$CERT_FILE" || ! -f "$KEY_FILE" ]]; then
  echo "Generating locally trusted localhost certificate..."
  mkcert \
    -cert-file "$CERT_FILE" \
    -key-file "$KEY_FILE" \
    localhost 127.0.0.1 ::1
  chmod 600 "$KEY_FILE"
fi

cat > "$CONFIG_FILE" <<EOF
[server]
address = "127.0.0.1"
port = 8501
sslCertFile = "$CERT_FILE"
sslKeyFile = "$KEY_FILE"
enableCORS = true
enableXsrfProtection = true

[browser]
serverAddress = "localhost"
serverPort = 8501
EOF

echo
echo "DeepGuard AI secure local frontend"
echo "----------------------------------"
echo "HTTPS: https://localhost:8501"
echo "Certificate: $CERT_FILE"
echo ""
echo "Start FastAPI separately on port 8000, then keep this terminal running."
echo ""

cd "$ROOT_DIR"
exec "$ROOT_DIR/.venv/bin/python" -m streamlit run frontend/app.py
