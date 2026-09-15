# DeepGuard AI

Professional AI-powered deepfake detection platform built with **Streamlit + FastAPI + PyTorch**.

DeepGuard analyzes image, video, and supported audio inputs and exposes forensic results through a Streamlit user interface backed by a FastAPI inference API.

## Architecture

```
Browser
   │
   ▼
Streamlit Frontend :8501
   │
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
   ├── Xception
   └── ViT
   │
   ▼
Real / Fake + confidence + risk + forensic signals
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
| Database | PostgreSQL / SQLite |
| Reports | ReportLab |
| Testing | PyTest |
| Deployment | Docker Compose |

## Requirements

- macOS, Linux, or Windows
- Python 3.11+
- Git
- ~5 GB free disk space for ML dependencies
- Optional: Docker Desktop for containerized deployment

## Local development

### 1. Clone the repository

```bash
git clone https://github.com/Aradhy25/Arise-2.0.git
cd Arise-2.0
```

### 2. Create and activate the virtual environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

If PyTorch installation needs a separate platform-specific command, install the appropriate PyTorch build first, then install the remaining requirements.

### 4. Add model weights

Place the EfficientNet checkpoint at:

```text
backend/weights/efficientnet.pth
```

Verify:

```bash
ls -lh backend/weights/efficientnet.pth
```

Do not commit private credentials, API keys, uploaded media, generated reports, or other sensitive runtime data.

### 5. Start the FastAPI backend

Use the virtual-environment interpreter explicitly:

```bash
./.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

Keep this terminal running.

Backend:

- http://localhost:8000
- http://localhost:8000/docs
- http://localhost:8000/api/health

### 6. Start the Streamlit frontend

Open a second terminal:

```bash
cd ~/Arise-2.0
source .venv/bin/activate
./.venv/bin/python -m streamlit run frontend/app.py
```

Open:

**http://localhost:8501**

The Streamlit sidebar contains the FastAPI URL. For local development the default is:

```text
http://localhost:8000
```

### 7. Test the application

In Streamlit:

1. Open **Scan**.
2. Upload a supported image, video, or audio file.
3. Select a detection model.
4. Optionally enable ensemble analysis.
5. Run the analysis.
6. Review the verdict, confidence, fake probability, risk level, explanation, and technical details.

The **Batch** tab supports multiple files and the **Live** tab supports webcam frame capture.

## Makefile shortcuts

With the virtual environment active:

```bash
make backend
make frontend
make test
```

The backend and frontend commands use the project's virtual environment directly.

## Docker Compose

The project can also be run as a multi-service stack:

```bash
docker compose up --build
```

Services:

| Service | Local port | Purpose |
|---|---:|---|
| Streamlit | 8501 | Web interface |
| FastAPI | 8000 | API and inference service |
| PostgreSQL | 5432 | Application database |

Open **http://localhost:8501** after the services start.

Stop the stack:

```bash
docker compose down
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

Use **http://localhost:8000/docs** for the interactive API documentation.

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
│   │   └── efficientnet.pth
│   ├── uploads/
│   ├── reports/
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── scripts/
├── docs/
├── docker-compose.yml
├── Makefile
└── README.md
```

## Model and forensic pipeline

A typical visual detection request follows:

1. Media upload.
2. OpenCV decoding and preprocessing.
3. Face detection and cropping where applicable.
4. PyTorch model inference.
5. Confidence and fake-probability calculation.
6. Optional ensemble and forensic signals.
7. Explainability/heatmap generation where supported.
8. Structured result returned by FastAPI.
9. Result rendered by Streamlit.

Detection is probabilistic. No deepfake detector should be treated as infallible, especially for high-stakes decisions.

## Research datasets

For research and model development, commonly used datasets include:

- FaceForensics++
- Celeb-DF
- DFDC
- ForgeryNet
- ASVspoof for relevant audio research

Use datasets according to their licenses and research terms.

## Testing

```bash
pytest -q backend/tests
```

## Security notes

For production deployment:

- Replace development secrets with strong environment-managed secrets.
- Restrict CORS to trusted origins.
- Do not expose database credentials in source control.
- Apply upload size/type limits.
- Store uploaded media securely.
- Add authentication to endpoints that require user access.
- Use HTTPS/TLS.
- Keep model files and generated reports outside public static directories.
- Review model outputs before using them for consequential decisions.

## Deployment

The recommended production architecture is:

```
Internet
   │
   ▼
Streamlit application
   │
   ▼
FastAPI service
   │
   ├── ML inference
   ├── PostgreSQL
   └── secure storage
```

For container deployment, use:

```bash
docker compose up --build
```

For a cloud deployment, deploy the Streamlit frontend and FastAPI backend as separate services and configure:

```text
DEEPGUARD_API_URL=https://your-api-domain
```

## Project status

DeepGuard AI is an active development project. Model accuracy depends on the checkpoint, preprocessing, input quality, and training data. Benchmark and validate models on representative datasets before making production claims.

## License

Add the project's applicable license here before public distribution.
