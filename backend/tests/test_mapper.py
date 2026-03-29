from services.generator import generate_txt
from services.mapper import (
    map_antrieb_header,
    map_antrieb_row,
    map_bemerkung,
    map_bemerkung_number,
    map_colour,
    map_construction_number,
    map_construction_type,
    map_document,
    map_endleiste,
    map_l_column,
    map_r_column,
)

FILE_2_RAW = {
    "company_name": "Musterbau & Holztechnik GmbH",
    "project_ref": "K2026-77195",
    "order_number": "0805260933",
    "delivery_date": "20.06.2026",
    "colour": "Aluminium Weiß",
    "construction": "Standard (2500er Wand)",
    "foam": "140 mm Hartschaum",
    "endleiste": "HSA9016",
    "antrieb": "Alle Motoren mit IO-homecontrol",
    "total_quantity": 13,
    "positions": [
        {"pos": "EG1", "breite": 880,  "hoehe": 1390, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 2},
        {"pos": "EG2", "breite": 880,  "hoehe": 1390, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "EG3", "breite": 1210, "hoehe": 1450, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "EG4", "breite": 2510, "hoehe": 2310, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "Notkurbel",                        "stueck": 1},
        {"pos": "EG5", "breite": 1850, "hoehe": 1120, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "EG6", "breite": 1060, "hoehe": 2350, "l": "L", "r": "",  "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "DG1", "breite": 855,  "hoehe": 600,  "l": "L", "r": "",  "antrieb": "Elektro", "bemerkung": "Deita Rolladenkasten 180 mm hoch", "stueck": 1},
        {"pos": "DG2", "breite": 820,  "hoehe": 600,  "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "Delta Rolladenkasten 180 mm hoch", "stueck": 1},
        {"pos": "DG3", "breite": 1060, "hoehe": 2350, "l": "L", "r": "",  "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "DG4", "breite": 1060, "hoehe": 2350, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "Notkurbel",                        "stueck": 1},
        {"pos": "DG5", "breite": 1210, "hoehe": 1450, "l": "L", "r": "",  "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "DG6", "breite": 1210, "hoehe": 1450, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
    ],
}

FILE_1_RAW = {
    "company_name": "Musterbau & Holztechnik GmbH",
    "project_ref": "P2026-71881",
    "order_number": "0803260522",
    "delivery_date": "15.05.2026",
    "colour": "Aluminium Anthrazit",
    "construction": "Erhöht (2750er Wand)",
    "foam": "140 mm Hartschaum",
    "endleiste": "HSA7016",
    "antrieb": "Alle Motoren mit IO-homecontrol",
    "total_quantity": 13,
    "positions": [
        {"pos": "EG1", "breite": 920,  "hoehe": 1450, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 2},
        {"pos": "EG2", "breite": 920,  "hoehe": 1450, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "EG3", "breite": 1210, "hoehe": 1450, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "EG4", "breite": 2510, "hoehe": 2310, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "Notkurbel",                        "stueck": 1},
        {"pos": "EG5", "breite": 1850, "hoehe": 1120, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "EG6", "breite": 1060, "hoehe": 2350, "l": "L", "r": "",  "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "DG1", "breite": 900,  "hoehe": 700,  "l": "L", "r": "",  "antrieb": "Elektro", "bemerkung": "Delta Rolladenkasten 180 mm hoch", "stueck": 1},
        {"pos": "DG2", "breite": 900,  "hoehe": 700,  "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "Delta Rolladenkasten 180 mm hoch", "stueck": 1},
        {"pos": "DG3", "breite": 1060, "hoehe": 2350, "l": "L", "r": "",  "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "DG4", "breite": 1060, "hoehe": 2350, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "Notkurbel",                        "stueck": 1},
        {"pos": "DG5", "breite": 1210, "hoehe": 1450, "l": "L", "r": "",  "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
        {"pos": "DG6", "breite": 1210, "hoehe": 1450, "l": "",  "r": "R", "antrieb": "Elektro", "bemerkung": "",                                 "stueck": 1},
    ],
}


def test_colour_weiss():
    assert map_colour("Aluminium Weiß") == "WEISS"


def test_colour_weiss_ascii_fallback():
    assert map_colour("Aluminium Weiss") == "WEISS"


def test_colour_anthrazit():
    assert map_colour("Aluminium Anthrazit") == "ANTHRAZIT"


def test_colour_silber():
    assert map_colour("Aluminium Silber") == "SILBER"


def test_construction_type_standard():
    assert map_construction_type("Standard (2500er Wand)") == "Standard"


def test_construction_type_erhoht():
    assert map_construction_type("Erhöht (2750er Wand)") == "Erhöht"


def test_construction_number_2500():
    assert map_construction_number("Standard (2500er Wand)") == "2500"


def test_construction_number_2750():
    assert map_construction_number("Erhöht (2750er Wand)") == "2750"


def test_endleiste_9016():
    assert map_endleiste("HSA9016") == "hwf9016"


def test_endleiste_7016():
    assert map_endleiste("HSA7016") == "hwf7016"


def test_endleiste_9006():
    assert map_endleiste("HSA9006") == "hwf9006"


def test_antrieb_header_io():
    assert map_antrieb_header("Alle Motoren mit IO-homecontrol") == "IO"


def test_antrieb_header_smi():
    assert map_antrieb_header("Alle Motoren mit SMI-homecontrol") == "SMI"


def test_l_column_with_l():
    assert map_l_column("L") == "1"


def test_l_column_empty():
    assert map_l_column("") == "0"


def test_r_column_with_r():
    assert map_r_column("R") == "1"


def test_r_column_empty():
    assert map_r_column("") == "0"


def test_antrieb_row_elektro_io():
    assert map_antrieb_row("Elektro", "Alle Motoren mit IO-homecontrol") == "1"


def test_antrieb_row_elektro_smi():
    assert map_antrieb_row("Elektro", "Alle Motoren mit SMI-homecontrol") == "2"


def test_antrieb_row_empty():
    assert map_antrieb_row("", "Alle Motoren mit IO-homecontrol") == "0"


def test_bemerkung_notkurbel():
    assert map_bemerkung("Notkurbel") == "8"


def test_bemerkung_rolladenkasten():
    assert map_bemerkung("Delta Rolladenkasten 180 mm hoch") == "Rolladenkasten"


def test_bemerkung_empty():
    assert map_bemerkung("") == "0"


def test_bemerkung_none():
    assert map_bemerkung(None) == "0"


def test_bemerkung_number_180():
    assert map_bemerkung_number("Delta Rolladenkasten 180 mm hoch") == "180"


def test_bemerkung_number_notkurbel():
    assert map_bemerkung_number("Notkurbel") == "0"


def test_bemerkung_number_empty():
    assert map_bemerkung_number("") == "0"


def test_file2_header_all_columns():
    result = map_document(FILE_2_RAW)
    h = result["header"]
    assert h[0] == "Musterbau & Holztechnik GmbH"
    assert h[1] == "K2026-77195"
    assert h[2] == "0805260933"
    assert h[3] == "20.06.2026"
    assert h[4] == "WEISS"
    assert h[5] == "Standard"
    assert h[6] == "2500"
    assert h[7] == "140 mm Hartschaum"
    assert h[8] == "hwf9016"
    assert h[9] == "IO"
    assert h[10] == "13"


def test_file2_position_count():
    result = map_document(FILE_2_RAW)
    assert len(result["positions"]) == 12


def test_file2_eg1_two_pieces():
    result = map_document(FILE_2_RAW)
    assert result["positions"][0] == ["1", "2", "880", "1390", "0", "1", "1", "EG1", "0", "0"]


def test_file2_eg4_notkurbel():
    result = map_document(FILE_2_RAW)
    assert result["positions"][3] == ["4", "1", "2510", "2310", "0", "1", "1", "EG4", "8", "0"]


def test_file2_eg6_left_motor():
    result = map_document(FILE_2_RAW)
    assert result["positions"][5] == ["6", "1", "1060", "2350", "1", "0", "1", "EG6", "0", "0"]


def test_file2_dg1_rolladenkasten():
    result = map_document(FILE_2_RAW)
    assert result["positions"][6] == ["7", "1", "855", "600", "1", "0", "1", "DG1", "Rolladenkasten", "180"]


def test_file2_dg2_rolladenkasten():
    result = map_document(FILE_2_RAW)
    assert result["positions"][7] == ["8", "1", "820", "600", "0", "1", "1", "DG2", "Rolladenkasten", "180"]


def test_file1_header_colour_anthrazit():
    result = map_document(FILE_1_RAW)
    assert result["header"][4] == "ANTHRAZIT"


def test_file1_header_construction_erhoht():
    result = map_document(FILE_1_RAW)
    assert result["header"][5] == "Erhöht"
    assert result["header"][6] == "2750"


def test_file1_header_endleiste_7016():
    result = map_document(FILE_1_RAW)
    assert result["header"][8] == "hwf7016"


def test_file1_position_count():
    result = map_document(FILE_1_RAW)
    assert len(result["positions"]) == 12


def test_file1_eg1_two_pieces():
    result = map_document(FILE_1_RAW)
    assert result["positions"][0] == ["1", "2", "920", "1450", "0", "1", "1", "EG1", "0", "0"]


def test_line_numbers_sequential_file2():
    result = map_document(FILE_2_RAW)
    for i, row in enumerate(result["positions"], start=1):
        assert row[0] == str(i)


def test_line_numbers_sequential_file1():
    result = map_document(FILE_1_RAW)
    for i, row in enumerate(result["positions"], start=1):
        assert row[0] == str(i)


def test_generator_produces_pipe_delimiter():
    result = map_document(FILE_2_RAW)
    txt = generate_txt(result)
    first_line = txt.split(chr(10))[0]
    assert "|" in first_line
    assert first_line.count("|") == 10


def test_generator_line_count():
    result = map_document(FILE_2_RAW)
    txt = generate_txt(result)
    lines = txt.strip().split(chr(10))
    assert len(lines) == 13


def test_generator_header_content():
    result = map_document(FILE_2_RAW)
    txt = generate_txt(result)
    assert txt.startswith("Musterbau & Holztechnik GmbH|K2026-77195|0805260933")


if __name__ == "__main__":
    import inspect

    tests = [
        v for k, v in sorted(globals().items())
        if k.startswith("test_") and inspect.isfunction(v)
    ]
    passed = failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {test.__name__}: {e}")
            failed += 1
    print(f"{passed} passed, {failed} failed out of {len(tests)} tests")
