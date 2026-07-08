# step2_prepare_analysis_data.py — Build simple, chart-ready summary tables from the cleaned data
import os
import sqlite3
import pandas as pd
from config import DB_PATH, TARGET_COL

OUTPUT_DIR = "data/processed"
PATIENTS_CSV_PATH = f"{OUTPUT_DIR}/patients_clean.csv"

DASHBOARD_DIMENSIONS = [
    "race",
    "gender",
    "age",
    "admission_type_id",
    "discharge_disposition_id",
    "admission_source_id",
    "time_in_hospital",
    "num_lab_procedures",
    "num_procedures",
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
    "number_diagnoses",
    "max_glu_serum",
    "A1Cresult",
    "insulin",
    "change",
    "diabetesMed",
]


def load_clean_data(db_path: str = DB_PATH, table: str = "patients") -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return df


def summarize_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    summary = (
        df.groupby(group_col)[TARGET_COL]
        .agg(readmission_rate="mean", patient_count="count")
        .reset_index()
        .sort_values("readmission_rate", ascending=False)
    )
    summary["readmission_rate"] = (summary["readmission_rate"] * 100).round(2)
    return summary


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_clean_data()
    print(f"Loaded {len(df)} rows from the database")

    df.to_csv(PATIENTS_CSV_PATH, index=False)
    print(f"Saved full clean dataset to {PATIENTS_CSV_PATH}\n")

    for col in DASHBOARD_DIMENSIONS:
        if col not in df.columns:
            print(f"Skipped '{col}' — not found in dataset")
            continue
        summary = summarize_by(df, col)
        out_path = f"{OUTPUT_DIR}/summary_by_{col}.csv"
        summary.to_csv(out_path, index=False)
        print(f"Saved {out_path}  ({summary[col].nunique()} groups)")

    print(f"\nDone. {len(DASHBOARD_DIMENSIONS)} summary tables generated in {OUTPUT_DIR}/")


if __name__ == "__main__":
    run()