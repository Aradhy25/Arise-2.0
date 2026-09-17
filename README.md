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
   ├── Dedicated Real/Fake detector
   ├── Forensic analysis / heatmaps
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
| Deep learning | PyTorch + Hugging Face Transformers |
| Primary image detector | Fine-tuned ViT Real/Fake classifier |
| Optional local detector | EfficientNet-B0 / ResNeXt / ViT with validated fine-tuned checkpoint |
| Computer vision | OpenCV |
| Explainability | Forensic heatmaps / Grad-CAM for validated local checkpoints |
| Authentication | JWT |
| Database | MySQL 8+ / MySQL Community Server |
| ORM | SQLAlchemy |
| MySQL driver | PyMySQL |
| Reports | ReportLab |
| Testing | PyTest |
| Containerization | Docker + Docker Compose |

## Detection engine

The default visual detector is **`dima806/deepfake_vs_real_image_detection`**, a fine-tuned Vision Transformer with explicit `Real` and `Fake` labels. The model card reports strong benchmark results on its training/evaluation data, but also warns about concept drift because the model was trained on data collected years ago. Those benchmark numbers should therefore **not** be treated as DeepGuard's current real-world accuracy. urlModel card on Hugging Facehttps://huggingface.co/dima806/deepfake_vs_real_image_detection

This change is important because an ImageNet-pretrained EfficientNet with a newly created binary classification head is **not** a deepfake detector. DeepGuard now refuses mismatched local checkpoints and will not present a random/untrained binary head as a valid detector.

On first visual inference, Transformers downloads and caches the detector model (roughly 343 MB for the current safetensors checkpoint). Subsequent runs use the local Hugging Face cache.

### Configure the detector

`backend/.env` can contain:

```env
DETECTOR_BACKEND=huggingface
HF_MODEL_ID=dima806/deepfake_vs_real_image_detection
USE_LOCAL_CHECKPOINT=false
```

A local checkpoint can be enabled only after it has been trained for the repository's exact classifier architecture:

```env
DETECTOR_BACKEND=local
USE_LOCAL_CHECKPOINT=true
```

If a local checkpoint has missing or unexpected parameters, DeepGuard rejects it instead of silently using partially loaded weights.

### Important limitation

Deepfake detection is not a universal truth oracle. The default Hugging Face model is useful as a trained baseline for Real/Fake image classification, but its own model card warns about concept drift. For a production-quality research system, benchmark and fine-tune the detector on current, representative datasets containing the specific manipulation types you care about (face swaps, reenactment, diffusion/AI-generated faces, compression variants, social-media recompression, and current generators).

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
- Internet access for Python packages and the first Hugging Face model download
- At least ~6 GB free disk space for ML dependencies and the detector cache

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
CORS_ORIGINS=https://localhost:8501,http://localhost:8501,http://localhost:5173,http://localhost:3000,http://127.0.0.1:8501,http://127.0.0.1:5173
DEVICE=cpu
DEFAULT_MODEL=efficientnet
DETECTOR_BACKEND=huggingface
HF_MODEL_ID=dima806/deepfake_vs_real_image_detection
USE_LOCAL_CHECKPOINT=false
DEEPGUARD_API_URL=http://localhost:8000
```

If the database password contains URL-reserved characters such as `@`, encode them (`@` → `%40`).

### 4. Install/update dependencies

If you already have a `.venv`, update it after pulling the detector changes:

```bash
./.venv/bin/python -m pip install -r backend/requirements.txt
./.venv/bin/python -m pip install -r frontend/requirements.txt
```

### 5. Start FastAPI

```bash
./.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

### 6. Start Streamlit

In a second terminal:

```bash
./.venv/bin/python -m streamlit run frontend/app.py --server.port 8501
```

Open `http://localhost:8501` for ordinary local HTTP development.

## 🔒 Secure local HTTPS — macOS

For local development, DeepGuard includes `scripts/secure_local_macos.sh`. It uses **mkcert** to create a locally trusted certificate for `localhost`, then launches Streamlit with TLS.

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

Place optional local fine-tuned checkpoints in:

```text
backend/weights/
```

Current legacy/local checkpoint path:

```text
backend/weights/efficientnet.pth
```

Do not enable it as the detector unless it has been trained for the exact repository architecture and passes validation. The default Hugging Face detector does not require the checkpoint to be committed to GitHub.

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

Use environment variables/secrets for public deployments. Never publish `backend/.env`, database passwords, JWT secrets or private model/data credentials.

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

DeepGuard AI is an active development project. Detection quality depends on model weights, preprocessing, input quality, manipulation type, and training data. Benchmark models on representative current datasets before making production accuracy claims.

## License

Add the project's applicable license before public distribution.
