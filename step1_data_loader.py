# step1_data_loader.py — Load the raw UCI Diabetes 130-US hospitals dataset, clean it, and store to SQLite
import sqlite3
import pandas as pd
from config import RAW_DATA_PATH, IDS_MAPPING_PATH, DB_PATH, DROP_COLS, TARGET_COL, RAW_TARGET_COL

# The three ID columns in diabetic_data.csv that IDS_mapping.csv translates to human-readable labels
ID_COLUMNS = ["admission_type_id", "discharge_disposition_id", "admission_source_id"]


def load_raw(path: str = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw CSV. The UCI dataset uses '?' for missing values."""
    df = pd.read_csv(path, na_values=["?", "Unknown/Invalid"], low_memory=False)
    return df


def load_id_mappings(path: str = IDS_MAPPING_PATH) -> dict:
    """
    IDS_mapping.csv stacks three separate lookup tables back to back. Detects a
    new section whenever a line's first field is exactly one of the known ID
    column names — robust regardless of blank-line formatting.
    """
    with open(path, "r", encoding="utf-8-sig") as f:
        lines = [line.rstrip("\r\n") for line in f]

    mappings = {}
    current_col = None

    for line in lines:
        if line.strip() == "":
            continue
        parts = [p.strip().strip('"') for p in line.split(",", 1)]
        if len(parts) < 2:
            continue
        key, value = parts[0], parts[1]

        if key in ID_COLUMNS:
            current_col = key
            mappings.setdefault(current_col, {})
            continue

        if current_col is not None and key != "":
            mappings[current_col][key] = value

    return mappings


def apply_id_mappings(df: pd.DataFrame, mappings: dict) -> pd.DataFrame:
    """Replace numeric ID columns with their human-readable descriptions where a mapping exists."""
    df = df.copy()
    for col in ID_COLUMNS:
        if col in df.columns and col in mappings:
            lookup = mappings[col]
            df[col] = df[col].astype(str).map(lookup).fillna(df[col].astype(str))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Drop unusable columns, collapse target to binary, handle missing values."""
    df = df.copy()

    cols_to_drop = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    if RAW_TARGET_COL in df.columns:
        df[TARGET_COL] = (df[RAW_TARGET_COL] == "<30").astype(int)
        df = df.drop(columns=[RAW_TARGET_COL])

    df = df.drop_duplicates()

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].fillna("Missing")
        else:
            df[col] = df[col].fillna(df[col].median())

    return df


def save_to_sqlite(df: pd.DataFrame, db_path: str = DB_PATH, table: str = "patients") -> None:
    conn = sqlite3.connect(db_path)
    df.to_sql(table, conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved {len(df)} rows to {db_path} (table: {table})")


def run() -> pd.DataFrame:
    df = load_raw()
    print(f"Raw dataset shape: {df.shape}")

    try:
        mappings = load_id_mappings()
        df = apply_id_mappings(df, mappings)
        mapped_cols = [c for c in ID_COLUMNS if c in mappings and len(mappings[c]) > 0]
        print(f"Applied ID mappings for columns: {mapped_cols}")
        for c in mapped_cols:
            print(f"  {c}: {len(mappings[c])} codes mapped")
    except FileNotFoundError:
        print(f"Warning: {IDS_MAPPING_PATH} not found — keeping raw numeric ID codes.")

    df = clean(df)
    save_to_sqlite(df)
    print(f"Cleaned dataset shape: {df.shape}")
    print(f"Readmission (<30 days) rate: {df[TARGET_COL].mean():.4f}")
    return df


if __name__ == "__main__":
    run()