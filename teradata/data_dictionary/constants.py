from pathlib import Path

BASE = Path(__file__).parent.parent
META = BASE / "metadata"
OUT = BASE / "output"

TABLEKIND_NAMES = {
    "T": "Table",
    "V": "View",
    "O": "View",
    "P": "Procedure",
    "M": "Macro",
    "A": "Procedure",
    "R": "TableFunction",
    "F": "Function",
    "U": "UDT",
    "S": "Sequence",
    "t": "TempTable",
}
VALID_TABLE_KINDS = list(TABLEKIND_NAMES.keys())

COLUMN_TYPE_MAP = {
    "CV": "VARCHAR",
    "CF": "CHAR",
    "I": "INTEGER",
    "I1": "BYTEINT",
    "I2": "SMALLINT",
    "I8": "BIGINT",
    "D": "DECIMAL",
    "F": "FLOAT",
    "DA": "DATE",
    "TS": "TIMESTAMP",
    "TZ": "TIME WITH TIME ZONE",
    "AT": "TIME",
    "BF": "BYTE",
    "BV": "VARBYTE",
    "BO": "BLOB",
    "CO": "CLOB",
    "N": "NUMBER",
    "JN": "JSON",
    "XM": "XML",
    "UT": "UDT",
    "PD": "PERIOD(DATE)",
    "PT": "PERIOD(TIME)",
    "PS": "PERIOD(TIMESTAMP)",
    "PM": "PERIOD(TIMESTAMP WITH TIME ZONE)",
    "PZ": "PERIOD(TIMESTAMP WITH TIME ZONE)",
}
INTERVAL_CODES = [
    "YR", "YM", "MO", "DY", "DH", "DM", "DS",
    "HR", "HM", "HS", "MI", "MS", "SC",
]
PERIOD_CODES = ["PD", "PT", "PS", "PM", "PZ"]
