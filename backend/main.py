"""
main.py
-------
FastAPI backend for the Rolladen PDF extraction and mapping application.

Endpoints:
    GET  /health   - liveness check
    POST /extract  - upload PDF, get JSON (raw + mapped + txt_content)
    POST /download - upload PDF, get .txt file for download
"""

import logging
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from services.extractor import extract_from_pdf_bytes
from services.generator import generate_txt
from services.mapper import map_document

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

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


def _run_pipeline(pdf_bytes: bytes) -> tuple[dict, str]:
    """
    Shared extraction pipeline: PDF bytes -> (mapped dict, txt string).

    Raises:
        HTTPException 422 if extraction produces invalid output.
        HTTPException 500 for unexpected errors.
    """
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
    return mapped, txt_content


def _validate_upload(file: UploadFile, pdf_bytes: bytes) -> None:
    """Validates filename and size. Raises HTTPException on failure."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(pdf_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
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
    pdf_bytes = await file.read()
    _validate_upload(file, pdf_bytes)

    mapped, txt_content = _run_pipeline(pdf_bytes)

    return {
        "filename": file.filename,
        "mapped": mapped,
        "txt_content": txt_content,
    }


@app.post("/download")
async def download_txt(file: UploadFile = File(...)):
    """
    Accepts a PDF upload.
    Returns the mapped .txt file directly as a downloadable response.
    """
    pdf_bytes = await file.read()
    _validate_upload(file, pdf_bytes)

    _, txt_content = _run_pipeline(pdf_bytes)

    output_filename = file.filename.replace(".pdf", "_mapped.txt").replace(".PDF", "_mapped.txt")

    return Response(
        content=txt_content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{output_filename}"'},
    )
