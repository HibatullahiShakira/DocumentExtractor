# Rolladen PDF Extraction & Mapping

Extracts structured data from German roller blind purchase order PDFs and maps it to a pipe-delimited `.txt` format.

## Stack
- **Backend**: FastAPI + Claude Vision API
- **Frontend**: React (Vite)
- **Containerization**: Docker + Docker Compose

## Quick Start

```bash
export ANTHROPIC_API_KEY=your_key_here
docker-compose up --build
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Docker Pull

```bash
docker pull hibatullahi/rolladen-backend:latest
docker pull hibatullahi/rolladen-frontend:latest
```
