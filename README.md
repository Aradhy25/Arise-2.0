# DeepGuard AI

Professional AI-powered deepfake detection platform built with **Streamlit + FastAPI + PyTorch + MySQL**.

DeepGuard analyzes supported image, video, and audio inputs and exposes forensic results through a Streamlit interface backed by a FastAPI inference API and persistent MySQL storage.

## Cross-platform support

DeepGuard is prepared for local development on:

- **Windows 10/11** — PowerShell setup and Windows Python virtual environment
- **macOS** — Intel and Apple Silicon (M1/M2/M3/M4) where supported by the installed PyTorch build
- **Linux** — x86_64 and other platforms supported by the selected Python/PyTorch wheels
- **Docker** — recommended when you want the most consistent environment across operating systems

The repository provides platform-specific setup scripts so users do not need to manually translate Unix commands to Windows.

## Architecture

```text
Browser
   │
   ▼
Streamlit Frontend :8501
   │ HTTP/REST
   ▼
FastAPI Backend :8000
   │
   ├── Authentication / API
   ├── Media processing
   ├── Forensic analysis
   └── Detection history / reports
   │
   ▼
PyTorch ML Pipeline
   ├── EfficientNet
   ├── Xception / ResNeXt
   └── ViT
   │
   ├── MySQL persistence
   └── Real / Fake + confidence + risk + forensic signals
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
| **Python** | Backend, Streamlit, ML inference, preprocessing, tests and utilities |
| **SQL / MySQL** | Database persistence and queries |
| **JavaScript / JSX** | Existing frontend source retained in the repository |
| **HTML / JSX markup** | Frontend markup where applicable |
| **Shell (Bash)** | macOS/Linux setup and development scripts |
| **PowerShell** | Windows setup automation |
| **YAML** | CI/CD and configuration where present |
| **Dockerfile** | Container images |
| **TOML** | Python/deployment configuration where present |
| **Makefile** | Unix development shortcuts |
| **Markdown** | Documentation |

## Requirements

### Native installation

- Python **3.11+**
- Git
- MySQL **8+** or compatible MySQL Community Server
- Internet access for Python packages and model dependencies
- At least ~5 GB free disk space for ML dependencies
- A supported CPU; GPU acceleration is optional and depends on the PyTorch build and operating system

### Docker installation

- Docker Desktop on Windows/macOS, or Docker Engine + Docker Compose on Linux
- At least ~6–10 GB RAM recommended for the ML stack
- Additional disk space for images, dependencies, model weights and MySQL data

> **PyTorch note:** PyTorch wheels vary by operating system, CPU architecture and accelerator. The pinned requirements are the project's tested baseline; if your platform does not provide a compatible wheel for a pinned version, install a compatible official PyTorch build for that platform first, then install the remaining requirements.

## Quick start — macOS / Linux

### 1. Clone

```bash
git clone https://github.com/Aradhy25/Arise-2.0.git
cd Arise-2.0
```

### 2. Run the setup script

```bash
chmod +x scripts/setup_unix.sh
./scripts/setup_unix.sh
```

The script creates `.venv`, upgrades packaging tools, installs backend/frontend dependencies and creates a safe `backend/.env` template when one does not exist.

### 3. Configure MySQL

Create the application database and user:

```sql
CREATE DATABASE deepguard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'deepguard_app'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON deepguard.* TO 'deepguard_app'@'localhost';
FLUSH PRIVILEGES;
```

Copy/configure:

```text
backend/.env.example → backend/.env
```

Set:

```env
DATABASE_URL=mysql+pymysql://deepguard_app:YOUR_URL_ENCODED_PASSWORD@localhost:3306/deepguard
SECRET_KEY=replace-with-a-long-random-secret
DEVICE=cpu
DEFAULT_MODEL=efficientnet
DEEPGUARD_API_URL=http://localhost:8000
```

If the password contains URL-reserved characters such as `@`, encode them. For example, `@` becomes `%40`.

### 4. Start backend

```bash
./.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

### 5. Start Streamlit

Open another terminal:

```bash
./.venv/bin/python -m streamlit run frontend/app.py --server.port 8501
```

Open **http://localhost:8501**.

## Quick start — Windows PowerShell

### 1. Clone

```powershell
git clone https://github.com/Aradhy25/Arise-2.0.git
cd Arise-2.0
```

### 2. Run setup

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup_windows.ps1
```

If Python is installed as `py` rather than `python`, create the environment manually:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m pip install -r frontend\requirements.txt
```

### 3. Configure MySQL

Use MySQL Workbench or the MySQL CLI to create the `deepguard` database and `deepguard_app` user, then copy:

```text
backend\.env.example → backend\.env
```

Set the `DATABASE_URL` to your Windows MySQL instance, for example:

```env
DATABASE_URL=mysql+pymysql://deepguard_app:YOUR_URL_ENCODED_PASSWORD@localhost:3306/deepguard
```

### 4. Start backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

### 5. Start Streamlit

Open another PowerShell window:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend\app.py --server.port 8501
```

Open **http://localhost:8501**.

## Quick start — Docker (all supported desktop/server OS)

Docker is the most consistent installation option when you want the same service layout on Windows, macOS or Linux.

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

Open **http://localhost:8501**.

Stop the stack:

```bash
docker compose down
```

Remove containers and the development database volume:

```bash
docker compose down -v
```

> Docker Compose uses a MySQL container and does not use your host MySQL installation. This makes the Docker setup independent of whether MySQL is installed natively on Windows, macOS or Linux.

## Model weights

Place the required model checkpoint(s) in:

```text
backend/weights/
```

For the current EfficientNet setup:

```text
backend/weights/efficientnet.pth
```

Model weights can be large and platform-independent, but inference acceleration depends on the host's PyTorch build. Do not commit private datasets or credentials.

## Database verification

Native installation:

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

Docker installation:

```bash
docker compose exec db mysql -u deepguard_app -p deepguard
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

`make` is convenient on macOS/Linux and is optional on Windows. Native Windows users can use the PowerShell commands above instead.

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

Interactive API documentation is available at:

**http://localhost:8000/docs**

## Local vs public deployment

The same codebase can support both local and public environments.

```text
LOCAL
Streamlit :8501 → FastAPI :8000 → Local MySQL :3306

PUBLIC
Streamlit hosting → Public FastAPI → Hosted MySQL
```

Use environment variables/secrets for public deployments. Never publish `backend/.env`, database passwords, JWT secrets or private model/data credentials.

## Project structure

```text
Arise-2.0/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── ml/
│   │   ├── models/
│   │   └── schemas/
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
│   └── setup_windows.ps1
├── docs/
├── docker-compose.yml
├── Makefile
└── README.md
```

## Security notes

For production:

- Use strong, unique secrets.
- Keep `.env` files out of Git.
- Restrict CORS to trusted origins.
- Use HTTPS/TLS.
- Store uploads and generated reports securely.
- Apply upload size/type limits.
- Do not expose MySQL directly to public users.
- Keep database credentials server-side.
- Validate model outputs before using them for consequential decisions.

## Project status

DeepGuard AI is an active development project. The current stack is **Streamlit + FastAPI + PyTorch + MySQL**, with persistent user and detection history. Detection quality depends on model weights, preprocessing, input quality and training data; benchmark models on representative datasets before making production accuracy claims.

## License

Add the project's applicable license before public distribution.
