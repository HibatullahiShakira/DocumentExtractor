"""
mapper.py
---------

Takes a raw extracted dictionary and returns a mapped output dictionary
that exactly follows the assessment mapping rules.
"""

import re


# ---------------------------------------------------------------------------
# HEADER MAPPING
# ---------------------------------------------------------------------------


def map_colour(raw: str) -> str:
    """
    COL 5 - Rolladen colour.

    Examples:
        "Aluminium Weiß"      -> "WEISS"
        "Aluminium Anthrazit" -> "ANTHRAZIT"
        "Aluminium Silber"    -> "SILBER"
    """
    raw_lower = raw.lower()
    if "weiß" in raw_lower or "weiss" in raw_lower:
        return "WEISS"
    elif "anthrazit" in raw_lower:
        return "ANTHRAZIT"
    elif "silber" in raw_lower:
        return "SILBER"
    return raw.upper()


def map_construction_type(raw: str) -> str:
    """
    COL 6 - Construction type keyword only (word before the bracket).

    Examples:
        "Standard (2500er Wand)" -> "Standard"
        "Erhöht (2750er Wand)"  -> "Erhöht"
    """
    return raw.split("(")[0].strip()


def map_construction_number(raw: str) -> str:
    """
    COL 7 - Wall thickness number extracted from inside the bracket.

    Examples:
        "Standard (2500er Wand)" -> "2500"
        "Erhöht (2750er Wand)"  -> "2750"
    """
    match = re.search(r"\((\d+)", raw)
    if match:
        return match.group(1)
    numbers = re.findall(r"\d+", raw)
    return numbers[0] if numbers else "0"


def map_endleiste(raw: str) -> str:
    """
    COL 9 - End strip code. Extracts last 4 digits and prepends 'hwf'.

    Examples:
        "HSA9016" -> "hwf9016"
        "HSA7016" -> "hwf7016"
        "HSA9006" -> "hwf9006"
    """
    digits = re.findall(r"\d+", raw)
    if digits:
        last_code = digits[-1][-4:]
        return f"hwf{last_code}"
    return raw


def map_antrieb_header(raw: str) -> str:
    """
    COL 10 - Motor system from the document header.

    Examples:
        "Alle Motoren mit IO-homecontrol"  -> "IO"
        "Alle Motoren mit SMI-homecontrol" -> "SMI"
    """
    raw_upper = raw.upper()
    if "IO" in raw_upper:
        return "IO"
    elif "SMI" in raw_upper:
        return "SMI"
    return raw


def map_header(raw: dict) -> list:
    """
    Produces the single header row as a list of 11 values.

    Expected keys: company_name, project_ref, order_number, delivery_date,
                   colour, construction, foam, endleiste, antrieb, total_quantity
    """
    construction_raw = raw.get("construction", "")

    return [
        raw.get("company_name", ""),  # COL 1
        raw.get("project_ref", ""),  # COL 2
        raw.get("order_number", ""),  # COL 3
        raw.get("delivery_date", ""),  # COL 4
        map_colour(raw.get("colour", "")),  # COL 5
        map_construction_type(construction_raw),  # COL 6
        map_construction_number(construction_raw),  # COL 7
        raw.get("foam", ""),  # COL 8
        map_endleiste(raw.get("endleiste", "")),  # COL 9
        map_antrieb_header(raw.get("antrieb", "")),  # COL 10
        str(raw.get("total_quantity", "")),  # COL 11
    ]


# ---------------------------------------------------------------------------
# POSITION ROW MAPPING
# ---------------------------------------------------------------------------


def map_l_column(value: str) -> str:
    """COL 5 - If L cell contains 'L' -> '1', else '0'."""
    return "1" if value and "L" in value.upper() else "0"


def map_r_column(value: str) -> str:
    """COL 6 - If R cell contains 'R' -> '1', else '0'."""
    return "1" if value and "R" in value.upper() else "0"


def map_antrieb_row(antrieb_cell: str, header_antrieb: str) -> str:
    """
    COL 7 - Combines row Antrieb value with header motor system.

        Elektro + IO header  -> "1"
        Elektro + SMI header -> "2"
        Anything else        -> "0"
    """
    # Regex catches common OCR typos: "Elektro", "Eicktro", "Elktro", etc.
    cell_lower = antrieb_cell.lower()
    # Regex covers OCR typos: "Elektro", "Eicktro", "Elktro", "Elektr" (truncated)
    is_elektro = bool(re.search(r"e[il][a-z]*[kt]ro?", cell_lower))
    header_upper = header_antrieb.upper()

    if is_elektro and "IO" in header_upper:
        return "1"
    elif is_elektro and "SMI" in header_upper:
        return "2"
    return "0"


def map_bemerkung(value: str) -> str:
    """
    COL 9 - Classifies the Bemerkung (notes) field.

        Contains "Notkurbel"      -> "8"
        Contains "Rolladenkasten" -> "Rolladenkasten"
        Empty or anything else    -> "0"
    """
    if not value:
        return "0"
    value_lower = value.lower()
    if "notkurbel" in value_lower:
        return "8"
    elif "rolladenkasten" in value_lower:
        return "Rolladenkasten"
    return "0"


def map_bemerkung_number(value: str) -> str:
    """
    COL 10 - Extracts a numeric measurement from the Bemerkung field.

    Examples:
        "Delta Rolladenkasten 180 mm hoch" -> "180"
        "Notkurbel"                        -> "0"
    """
    if not value:
        return "0"
    numbers = re.findall(r"\d+", value)
    return numbers[0] if numbers else "0"


def map_position_row(line_number: int, row: dict, header_antrieb: str) -> list:
    """
    Produces one position row as a list of 10 values.

    Expected keys: pos, breite, hoehe, l, r, antrieb, bemerkung, stueck
    """
    bemerkung = row.get("bemerkung", "") or ""

    return [
        str(line_number),  # COL 1: running number
        str(row.get("stueck", "")),  # COL 2: quantity
        str(row.get("breite", "")),  # COL 3: width
        str(row.get("hoehe", "")),  # COL 4: height
        map_l_column(row.get("l", "")),  # COL 5: left motor
        map_r_column(row.get("r", "")),  # COL 6: right motor
        map_antrieb_row(row.get("antrieb", ""), header_antrieb),  # COL 7: motor code
        row.get("pos", ""),  # COL 8: position code
        map_bemerkung(bemerkung),  # COL 9: notes type
        map_bemerkung_number(bemerkung),  # COL 10: notes number
    ]


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------


def map_document(raw: dict) -> dict:
    """
    Master mapping function.
    Takes the full raw extracted dict and returns the fully mapped output.

    Returns:
        {
            "header": [...11 values...],
            "positions": [[...10 values...], ...]
        }
    """
    header = map_header(raw)
    header_antrieb_raw = raw.get("antrieb", "")

    positions = []
    for i, row in enumerate(raw.get("positions", []), start=1):
        mapped_row = map_position_row(i, row, header_antrieb_raw)
        positions.append(mapped_row)

    return {
        "header": header,
        "positions": positions,
    }
