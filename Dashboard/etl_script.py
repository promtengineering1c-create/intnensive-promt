import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent
OUTPUT_DIR = DATA_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_sales_data(filepath: str | Path) -> pd.DataFrame:
    """Load Sales_Data_MVP with error handling."""
    try:
        df = pd.read_excel(filepath)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        raise
    except Exception as exc:
        print(f"[ERROR] Failed to read {filepath}: {exc}")
        raise
    return df


def load_rls_data(filepath: str | Path) -> pd.DataFrame:
    """Load RLS_Access_MVP with error handling."""
    try:
        df = pd.read_excel(filepath)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        raise
    except Exception as exc:
        print(f"[ERROR] Failed to read {filepath}: {exc}")
        raise
    return df


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate types, drop duplicates, handle missing values."""

    # --- Type enforcement ---
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")

    # --- Remove exact duplicates by Transaction_ID ---
    before = len(df)
    df = df.drop_duplicates(subset=["Transaction_ID"])
    after = len(df)
    if after < before:
        print(f"[INFO] Removed {before - after} duplicate transaction(s)")

    # --- Handle missing values ---
    # Revenue: fill with 0 — safest for aggregation; if NaN after coerce,
    # we assume it's a missing record rather than a corrupt one.
    df["Revenue"] = df["Revenue"].fillna(0)

    # Date: drop rows where Date is NaT — can't reliably impute a sale date.
    nat_count = df["Date"].isna().sum()
    if nat_count:
        print(f"[INFO] Dropping {nat_count} row(s) with missing Date")
        df = df.dropna(subset=["Date"])

    # Region, Store, Category: drop rows entirely missing critical dimensions.
    for col in ["Region", "Store", "Category"]:
        missing = df[col].isna().sum()
        if missing:
            print(f"[WARN] Dropping {missing} row(s) with missing '{col}'")
            df = df.dropna(subset=[col])

    return df.reset_index(drop=True)


def main() -> None:
    # Source paths
    sales_path = DATA_DIR / "Sales_Data_MVP.xlsx"
    rls_path = DATA_DIR / "RLS_Access_MVP.xlsx"

    # --- Step 1: Load ---
    sales_df = load_sales_data(sales_path)
    rls_df = load_rls_data(rls_path)

    print(f"[INFO] Loaded {len(sales_df)} sales rows, {len(rls_df)} RLS rows")

    # --- Step 2: Clean ---
    sales_clean = clean_sales_data(sales_df)

    print(f"[INFO] Cleaned data: {len(sales_clean)} rows ready")

    # --- Step 3: Export ---
    sales_out = OUTPUT_DIR / "Sales_Data_Cleaned.csv"
    rls_out = OUTPUT_DIR / "RLS_Access_Cleaned.csv"

    sales_clean.to_csv(sales_out, index=False, encoding="utf-8-sig")
    rls_df.to_csv(rls_out, index=False, encoding="utf-8-sig")

    print(f"[INFO] Exported: {sales_out}")
    print(f"[INFO] Exported: {rls_out}")


if __name__ == "__main__":
    main()
