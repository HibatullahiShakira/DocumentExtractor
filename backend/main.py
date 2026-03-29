"""
main.py
-------
FastAPI backend for the Rolladen PDF extraction and mapping application.

Endpoints:
    GET  /health   - liveness check
    POST /extract  - upload PDF, get JSON (raw + mapped + txt_content)
    POST /download - upload PDF, get .txt file for download
"""

import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from services.extractor import extract_from_pdf_bytes
from services.generator import generate_txt
from services.mapper import map_document

app = FastAPI(
    title="Rolladen PDF Extraction API",
    description="Extracts and maps German roller blind purchase orders to structured output",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Liveness check — confirms the service is running."""
    return {"status": "ok", "service": "rolladen-extraction-api"}


@app.post("/extract")
async def extract_and_map(file: UploadFile = File(...)):
    """
    Accepts a PDF upload.
    Returns extracted raw data, mapped output, and the final txt content.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        raw = extract_from_pdf_bytes(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Extraction failed: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected extraction error: {e}") from e

    try:
        mapped = map_document(raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mapping failed: {e}") from e

    txt_content = generate_txt(mapped)

    return {
        "filename": file.filename,
        "raw": raw,
        "mapped": mapped,
        "txt_content": txt_content,
    }


@app.post("/download")
async def download_txt(file: UploadFile = File(...)):
    """
    Accepts a PDF upload.
    Returns the mapped .txt file directly as a downloadable response.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        raw = extract_from_pdf_bytes(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Extraction failed: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected extraction error: {e}") from e

    mapped = map_document(raw)
    txt_content = generate_txt(mapped)

    output_filename = file.filename.replace(".pdf", "_mapped.txt").replace(".PDF", "_mapped.txt")

    return Response(
        content=txt_content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{output_filename}"'},
    )
