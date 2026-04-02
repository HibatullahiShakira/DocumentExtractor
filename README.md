# Rolladen PDF Extraction API

Extracts structured data from German roller blind (Rolladen) purchase order PDFs and maps it to a pipe-delimited text format for downstream processing.

---

## Overview

| Component | Technology |
|---|---|
| Backend API | FastAPI (Python 3.11) |
| PDF rendering | PyMuPDF (fitz) |
| Vision extraction | Groq API — `meta-llama/llama-4-scout-17b-16e-instruct` |
| Mapping logic | Deterministic Python rules (no AI) |
| Output format | Pipe-delimited `.txt` |
| Frontend | React + Vite + Tailwind CSS v4, served by nginx |
| Containerisation | Docker + Docker Compose |
| Deployment | Railway (backend + frontend as separate services) |
| CI/CD | GitHub Actions (lint → test → docker build) |

---

## Prerequisites

- Docker and Docker Compose
- A [Groq API key](https://console.groq.com) (free tier)

---

## Quick Start

**1. Clone the repo**

```bash
git clone https://github.com/HibatullahiShakira/DocumentExtractor.git
cd DocumentExtractor
```

**2. Set your API key**

```bash
# Create a .env file in the project root
echo "GROQ_API_KEY=gsk_your_key_here" > .env
```

**3. Start everything**

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

### Running without Docker

**Terminal 1 — Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

The `.env` file in the project root is loaded automatically via `python-dotenv`.

---

## Deployment (Railway)

The app is deployed as two separate Railway services from the same GitHub repo.

**Backend service**
- Root directory: `/backend`
- Environment variable: `GROQ_API_KEY`

**Frontend service**
- Root directory: `/frontend`
- Environment variables:
  - `BACKEND_URL` — public URL of the backend service (e.g. `https://your-backend.up.railway.app`)
  - `PORT` — set to `80` (nginx listen port)

Railway auto-deploys on every push to `main`.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | — | Groq API key for vision inference |
| `GROQ_MODEL` | No | `meta-llama/llama-4-scout-17b-16e-instruct` | Override the Groq model |
| `ALLOWED_ORIGINS` | No | `*` | Comma-separated CORS origins |
| `PORT` | No | `8000` (backend) / `80` (frontend) | Port the service listens on |
| `BACKEND_URL` | Frontend only | — | Backend URL for nginx proxy (Railway deployment) |

`.env` example:

```env
GROQ_API_KEY=gsk_your_key_here
# GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
# ALLOWED_ORIGINS=http://localhost:5173
```

---

## API Endpoints

### `GET /health`
Liveness check.

```json
{ "status": "ok", "service": "rolladen-extraction-api" }
```

### `POST /extract`
Upload a PDF, receive structured JSON.

```bash
curl -X POST http://localhost:8000/extract \
  -F "file=@order.pdf"
```

**Response:**
```json
{
  "filename": "order.pdf",
  "mapped": {
    "header": ["Company Name", "Ref", "OrderNo", "..."],
    "positions": [["1", "2", "880", "1390", "0", "1", "1", "EG1", "0", "0"]]
  },
  "txt_content": "Company Name|Ref|OrderNo|...\n1|2|880|..."
}
```

Returns `422` if the uploaded PDF is not a Rolladen purchase order.

### `POST /download`
Upload a PDF, download the mapped `.txt` file directly.

```bash
curl -X POST http://localhost:8000/download \
  -F "file=@order.pdf" \
  -o order_mapped.txt
```

**Limits:** Maximum upload size is 10 MB. Only `.pdf` files accepted.

---

## Document Validation

The app automatically rejects non-Rolladen documents. If you upload a PDF that is not a German roller blind purchase order, the API returns a `422` error with a clear message instead of silently producing empty results.

---

## Output Format

### Header row (11 columns)
```
Company|ProjectRef|OrderNumber|DeliveryDate|Colour|ConstructionType|WallThickness|Foam|Endleiste|MotorSystem|TotalQty
```

### Position rows (10 columns)
```
LineNo|Qty|Width|Height|LeftMotor|RightMotor|MotorCode|PosCode|Notes|NotesMeasurement
```

**Motor codes:** `1` = Elektro + IO, `2` = Elektro + SMI, `0` = other
**Notes:** `8` = Notkurbel, `Rolladenkasten` = roller blind box, `0` = none

---

## Running Tests Locally

```bash
cd backend
pip install -r requirements.txt
pytest
```

47 unit tests covering header mapping, position mapping, OCR typo handling, and output generation.

---

## Project Structure

```
.
├── backend/
│   ├── main.py                  # FastAPI app + endpoints
│   ├── requirements.txt
│   ├── Dockerfile
│   └── services/
│       ├── extractor.py         # PDF -> Groq vision API -> raw dict
│       ├── mapper.py            # raw dict -> mapped dict (deterministic)
│       └── generator.py         # mapped dict -> pipe-delimited txt
│   └── tests/
│       └── test_mapper.py       # 47 unit tests
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # React upload + results UI
│   │   └── App.css              # Tailwind CSS v4 entry point
│   ├── nginx.conf               # nginx reverse proxy config (env-templated)
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── Dockerfile               # nginx multi-stage build
│   └── vite.config.js
├── docker-compose.yml
├── pyproject.toml               # ruff + pytest config
└── .github/workflows/ci.yml     # GitHub Actions CI
```

---

## CI/CD

Every push triggers:

1. **Lint** — `ruff check` (E, W, F, N, UP rules)
2. **Format check** — `ruff format --check`
3. **Tests** — `pytest` (all 47 tests must pass)
4. **Docker build** — backend and frontend images built to verify no broken dependencies
