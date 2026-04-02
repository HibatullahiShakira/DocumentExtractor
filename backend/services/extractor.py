"""
extractor.py
------------
Handles PDF extraction using the Groq vision API.

Architecture:
- PDFs are scanned images — convert each page to PNG using PyMuPDF
- PNG is sent to Groq (meta-llama/llama-4-scout-17b-16e-instruct) via REST API
- Model returns structured JSON matching the extraction schema
- Uses requests directly (no SDK) for maximum compatibility
"""

import base64
import json
import os
import re

import fitz  # PyMuPDF
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_GROQ_MODEL_DEFAULT = "meta-llama/llama-4-scout-17b-16e-instruct"

EXTRACTION_SCHEMA = """
{
  "is_rolladen_order": true,
  "company_name": "string",
  "project_ref": "string",
  "order_number": "string - the large number on the same line as the word Roll",
  "delivery_date": "string - date under Liefertermin e.g. 20.06.2026",
  "colour": "string - the Rolladen field value e.g. Aluminium Weiss",
  "construction": "string - full Konstruktion value e.g. Standard (2500er Wand)",
  "foam": "string - Aussenschurze field value e.g. 140 mm Hartschaum",
  "endleiste": "string - Endleiste field value e.g. HSA9016",
  "antrieb": "string - Antrieb field value e.g. Alle Motoren mit IO-homecontrol",
  "total_quantity": "integer - the Gesamt total",
  "positions": [
    {
      "pos": "string - position code e.g. EG1 or DG4",
      "breite": "integer - width in mm",
      "hoehe": "integer - height in mm",
      "l": "string - L column value, empty string if blank",
      "r": "string - R column value, empty string if blank",
      "antrieb": "string - Antrieb column value",
      "bemerkung": "string - Bemerkung column value, empty string if blank",
      "stueck": "integer - quantity"
    }
  ]
}
"""

EXTRACTION_PROMPT = (
    "You are a precise document data extraction engine.\n\n"
    "First, determine whether the image is a German roller blind (Rolladen) purchase order form.\n"
    "A Rolladen order contains fields like Rolladen, Liefertermin, Konstruktion, Endleiste, Antrieb,\n"
    "and a table with columns Pos, Breite, Hoehe, L, R, Antrieb, Bemerkung, Stueck.\n\n"
    "If it is NOT a Rolladen order, return ONLY this JSON and nothing else:\n"
    '{"is_rolladen_order": false}\n\n'
    "If it IS a Rolladen order, extract all fields and return the full JSON below.\n\n"
    "CRITICAL RULES:\n"
    "1. Return ONLY valid JSON. No explanation, no markdown, no code fences.\n"
    "2. Extract values exactly as they appear. Do not translate or interpret.\n"
    "3. Include EVERY data row from the table (EG and DG sections).\n"
    "   Skip floor section headers (EG, OG, DG) and summary/total rows.\n"
    '4. If a table cell is empty return an empty string "".\n'
    "5. order_number is the large number next to the word Roll at the top right.\n"
    '6. For construction capture the FULL value e.g. "Standard (2500er Wand)".\n'
    "7. Table columns are: Pos | Breite (mm) | Hoehe (mm) | L | R | Antrieb | Bemerkung | Stueck.\n"
    "   Some rows have a small number (e.g. 7) in a narrow unlabelled column BEFORE Breite - ignore it.\n"
    "   Always use the column headers to identify Breite and Hoehe correctly.\n"
    "8. For header fields extract ONLY that specific field value.\n"
    "   Do not bleed values from adjacent fields on the same line.\n\n"
    "Return this exact JSON structure:\n" + EXTRACTION_SCHEMA
)


def pdf_page_to_base64_png(pdf_bytes: bytes, page_index: int = 0) -> str:
    """
    Converts a single PDF page to a base64-encoded PNG string.
    Uses PyMuPDF which works on scanned/image-based PDFs.

    Args:
        pdf_bytes:  raw bytes of the PDF file
        page_index: which page to render (0-indexed)

    Returns:
        base64-encoded PNG string
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_index]
    matrix = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR quality
    pixmap = page.get_pixmap(matrix=matrix)
    png_bytes = pixmap.tobytes("png")
    doc.close()
    return base64.standard_b64encode(png_bytes).decode("utf-8")


def clean_json_response(text: str) -> str:
    """Strips markdown code fences if the model wraps its response."""
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    return text.strip()


def extract_from_pdf_bytes(pdf_bytes: bytes) -> dict:
    """
    Main extraction function.

    Steps:
        1. Convert first PDF page to PNG
        2. POST image + prompt to Groq vision API
        3. Parse JSON response and return as dict

    Args:
        pdf_bytes: raw bytes of the uploaded PDF

    Returns:
        Extracted data as a Python dict matching EXTRACTION_SCHEMA

    Raises:
        ValueError:   if the model returns invalid JSON
        RuntimeError: if the API call fails
    """
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is not set.")
    model = os.environ.get("GROQ_MODEL", _GROQ_MODEL_DEFAULT)

    image_b64 = pdf_page_to_base64_png(pdf_bytes)
    image_url = f"data:image/png;base64,{image_b64}"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": EXTRACTION_PROMPT},
                ],
            }
        ],
        "max_tokens": 4096,
        "temperature": 0,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=120)

    if response.status_code != 200:
        raise RuntimeError(f"Groq API error {response.status_code}: {response.text}")

    raw_response = response.json()["choices"][0]["message"]["content"]
    cleaned = clean_json_response(raw_response)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model returned invalid JSON.\nResponse: {raw_response}\nError: {e}"
        ) from e

    if not parsed.get("is_rolladen_order", True):
        raise ValueError(
            "This does not appear to be a Rolladen purchase order. "
            "Please upload a valid Rolladen order form."
        )

    return parsed
