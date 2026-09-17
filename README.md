# DeepGuard AI

Professional AI-powered deepfake detection platform built with **Streamlit + FastAPI + PyTorch + MySQL**.

DeepGuard analyzes supported image, video, and audio inputs and exposes forensic results through a Streamlit interface backed by a FastAPI inference API and persistent MySQL storage.

## Cross-platform support

- **Windows 10/11** — PowerShell setup
- **macOS** — Intel and Apple Silicon (M1/M2/M3/M4), subject to PyTorch wheel support
- **Linux** — platforms supported by the selected Python/PyTorch wheels
- **Docker** — consistent service layout across Windows, macOS and Linux

## Architecture

```text
Browser
   │
   ▼
Streamlit Frontend :8501
   │ HTTP/REST (local server-to-server)
   ▼
FastAPI Backend :8000
   │
   ├── Authentication / API
   ├── Media processing
   ├── Forensic analysis
   └── Detection history / reports
   │
   ▼
PyTorch ML Pipeline → MySQL persistence
```

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| Deep learning | PyTorch + TorchVision |
| Models | EfficientNet-B0, Xception/ResNeXt, ViT-B/16 |
| Computer vision | OpenCV |
| Explainability | Grad-CAM / forensic heatmaps |
| Authentication | JWT |
| Database | MySQL 8+ / MySQL Community Server |
| ORM | SQLAlchemy |
| MySQL driver | PyMySQL |
| Reports | ReportLab |
| Testing | PyTest |
| Containerization | Docker + Docker Compose |

## Languages & configuration

| Language / format | Usage |
|---|---|
| Python | Backend, Streamlit, ML inference, preprocessing and tests |
| SQL / MySQL | Database persistence and queries |
| JavaScript / JSX | Existing frontend source retained in the repository |
| Shell (Bash) | macOS/Linux automation |
| PowerShell | Windows automation |
| YAML | CI/CD and configuration where present |
| Dockerfile | Container images |
| TOML | Python/deployment configuration |
| Makefile | Unix development shortcuts |
| Markdown | Documentation |

## Requirements

### Native installation

- Python **3.11+**
- Git
- MySQL **8+**
- Internet access for Python packages and model dependencies
- At least ~5 GB free disk space for ML dependencies

### Docker

- Docker Desktop on Windows/macOS, or Docker Engine + Docker Compose on Linux
- ~6–10 GB RAM recommended for the ML stack

> **PyTorch note:** PyTorch wheels vary by operating system, CPU architecture and accelerator. If a pinned wheel is unavailable for your platform, install a compatible official PyTorch build for that platform first.

## Quick start — macOS / Linux

### 1. Clone

```bash
git clone https://github.com/Aradhy25/Arise-2.0.git
cd Arise-2.0
```

### 2. Setup

```bash
chmod +x scripts/setup_unix.sh
./scripts/setup_unix.sh
```

### 3. Configure MySQL

Create the database and application user:

```sql
CREATE DATABASE deepguard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'deepguard_app'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON deepguard.* TO 'deepguard_app'@'localhost';
FLUSH PRIVILEGES;
```

Copy `backend/.env.example` to `backend/.env` and configure:

```env
DATABASE_URL=mysql+pymysql://deepguard_app:YOUR_URL_ENCODED_PASSWORD@localhost:3306/deepguard
SECRET_KEY=replace-with-a-long-random-secret
CORS_ORIGINS=http://localhost:8501
DEVICE=cpu
DEFAULT_MODEL=efficientnet
DEEPGUARD_API_URL=http://localhost:8000
```

If the database password contains URL-reserved characters such as `@`, encode them (`@` → `%40`).

### 4. Start FastAPI

```bash
./.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

### 5. Start Streamlit

In a second terminal:

```bash
./.venv/bin/python -m streamlit run frontend/app.py --server.port 8501
```

Open `http://localhost:8501` for ordinary local HTTP development.

## 🔒 Secure local HTTPS — macOS

For local development, DeepGuard now includes `scripts/secure_local_macos.sh`. It uses **mkcert** to create a locally trusted certificate for `localhost`, then launches Streamlit with TLS. Streamlit supports TLS through `server.sslCertFile` and `server.sslKeyFile`; for production, Streamlit recommends terminating TLS at a reverse proxy or load balancer instead. citeturn0search0turn0search1

From the repository root:

```bash
chmod +x scripts/secure_local_macos.sh
./scripts/secure_local_macos.sh
```

The script will:

1. Install `mkcert` with Homebrew if necessary.
2. Install a local development CA with `mkcert -install`.
3. Generate a certificate for `localhost`, `127.0.0.1` and `::1`.
4. Store the certificate/private key under `.cert/`.
5. Create an ignored local Streamlit TLS configuration under `.streamlit/local-config.toml`.
6. Start Streamlit on `https://localhost:8501`.

`mkcert` is specifically designed for locally trusted development certificates and supports macOS system trust stores. Its generated root CA private key must never be shared. citeturn0search2

### Secure local architecture

```text
Browser
  │
  │ HTTPS / TLS
  ▼
https://localhost:8501
  │
  │ local Python request
  ▼
http://localhost:8000
FastAPI
  │
  ▼
MySQL :3306
```

The FastAPI and MySQL ports remain local services; the browser-facing Streamlit interface is encrypted with HTTPS. For a public deployment, put TLS termination in front of the application rather than exposing these development settings directly.

### Important

The following files are intentionally local-only and ignored by Git:

```text
.cert/
.streamlit/local-config.toml
```

**Never commit a TLS private key or your mkcert root CA private key.**

## Quick start — Windows PowerShell

```powershell
git clone https://github.com/Aradhy25/Arise-2.0.git
cd Arise-2.0
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup_windows.ps1
```

Configure `backend\.env`, then start:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

In another PowerShell window:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend\app.py --server.port 8501
```

Open `http://localhost:8501`.

For Windows HTTPS development, use the same mkcert approach or a local reverse proxy. Do not copy a private development key into the repository.

## Quick start — Docker

From the repository root:

```bash
docker compose up --build
```

Services:

| Service | Port | Purpose |
|---|---:|---|
| Streamlit | 8501 | Web interface |
| FastAPI | 8000 | API and inference |
| MySQL | 3306 | Application database |

Open `http://localhost:8501`.

Stop:

```bash
docker compose down
```

Remove the development database volume:

```bash
docker compose down -v
```

## Model weights

Place model checkpoints in:

```text
backend/weights/
```

Current EfficientNet checkpoint:

```text
backend/weights/efficientnet.pth
```

Do not commit private datasets or credentials.

## Database verification

```bash
mysql -u deepguard_app -p deepguard
```

Then:

```sql
SHOW TABLES;
```

Expected application tables include:

```text
detections
users
```

## Testing

macOS/Linux:

```bash
./.venv/bin/python -m pytest -q backend/tests
```

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest -q backend\tests
```

## Makefile

```bash
make backend
make frontend
make test
make docker-up
make docker-down
```

## API overview

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create an account |
| POST | `/api/auth/login` | Authenticate |
| GET | `/api/auth/me` | Current user |
| POST | `/api/detect` | Media detection |
| GET | `/api/detect/models` | Available models |
| GET | `/api/history` | Detection history |
| GET | `/api/health` | Service health |

Interactive API documentation: `http://localhost:8000/docs`

## Local vs public deployment

```text
LOCAL
Browser → HTTPS Streamlit :8501 → FastAPI :8000 → MySQL :3306

PUBLIC
Browser → HTTPS reverse proxy / hosting → FastAPI → Hosted MySQL
```

Use environment variables/secrets for public deployments. Never publish `backend/.env`, database passwords, JWT secrets or private model/data credentials. Streamlit also recommends keeping secrets outside source control. citeturn0search10turn0search11

## Project structure

```text
Arise-2.0/
├── backend/
│   ├── app/
│   ├── weights/
│   ├── uploads/
│   ├── reports/
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── scripts/
│   ├── setup_unix.sh
│   ├── setup_windows.ps1
│   └── secure_local_macos.sh
├── docs/
├── docker-compose.yml
├── Makefile
└── README.md
```

## Security checklist

For production:

- Use strong, unique secrets.
- Keep `.env` files out of Git.
- Restrict CORS to trusted origins.
- Use HTTPS/TLS with a proper public certificate.
- Prefer TLS termination at a reverse proxy/load balancer for production.
- Store uploads and reports securely.
- Apply upload size/type limits.
- Do not expose MySQL directly to public users.
- Keep database credentials server-side.
- Validate model outputs before using them for consequential decisions.
- Never commit private TLS keys or local CA private keys.

## Project status

DeepGuard AI is an active development project. Detection quality depends on model weights, preprocessing, input quality and training data; benchmark models on representative datasets before making production accuracy claims.

## License

Add the project's applicable license before public distribution.
