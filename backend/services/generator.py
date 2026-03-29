"""
generator.py
------------
Takes the mapped output dictionary and produces the final .txt file content.

Delimiter: pipe "|"
Reason: commas appear inside values (e.g. "140 mm Hartschaum"),
        pipe avoids ambiguity and is standard for industrial data exchange.
"""

DELIMITER = "|"


def row_to_line(row: list) -> str:
    """Joins a list of values into a single pipe-delimited line."""
    return DELIMITER.join(str(v) for v in row)


def generate_txt(mapped: dict) -> str:
    """
    Converts the fully mapped document dictionary into a .txt string.

    Args:
        mapped: output from mapper.map_document()
                {"header": [...11 values...], "positions": [[...10 values...], ...]}

    Returns:
        A newline-separated string ready to be written to a .txt file.
    """
    lines = [row_to_line(mapped["header"])]
    for position in mapped["positions"]:
        lines.append(row_to_line(position))
    return "\n".join(lines)
