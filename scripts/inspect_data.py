"""Inspect the source sales CSV and report its schema and data quality."""

from pathlib import Path

import pandas as pd


def main():
    """Load the original dataset and print a descriptive inspection report."""
    csv_path = Path(__file__).resolve().parents[1] / "data" / "sales_dataset.csv"
    data = pd.read_csv(csv_path)

    numeric_columns = list(data.select_dtypes(include="number").columns)
    categorical_columns = [
        column
        for column in data.columns
        if (
            pd.api.types.is_string_dtype(data[column].dtype)
            or pd.api.types.is_object_dtype(data[column].dtype)
            or isinstance(data[column].dtype, pd.CategoricalDtype)
            or pd.api.types.is_bool_dtype(data[column].dtype)
        )
    ]
    role_columns = {
        role: [
            column
            for column in data.columns
            if column.strip().casefold() == role.casefold()
        ]
        for role in ("Sales", "Category", "Region")
    }

    print("DATA QUALITY REPORT")
    print("=" * 80)
    print(f"CSV file: {csv_path}")
    print(f"Rows: {data.shape[0]}")
    print(f"Columns: {data.shape[1]}")
    print("\nColumn names:")
    for column in data.columns:
        print(f"  - {column}")

    print("\nData types:")
    print(data.dtypes.to_string())

    missing_values = data.isna().sum()
    print("\nMissing values by column:")
    print(missing_values.to_string())
    print(f"Total missing values: {int(missing_values.sum())}")
    print(f"Duplicate rows: {int(data.duplicated().sum())}")

    print("\nNumerical columns:")
    print(f"  {numeric_columns}")
    print("Categorical columns:")
    print(f"  {categorical_columns}")

    print("\nSales, Category, and Region columns:")
    for role, columns in role_columns.items():
        print(f"  {role}: {columns if columns else 'Not found'}")

    print("\nSummary statistics:")
    print(data.describe(include="all").to_string())

    print("\nOverall data-quality checks:")
    print(f"  Missing values: {'PASS' if missing_values.sum() == 0 else 'CHECK'}")
    print(f"  Duplicate rows: {'PASS' if data.duplicated().sum() == 0 else 'CHECK'}")
    print(f"  Rows with any missing value: {int(data.isna().any(axis=1).sum())}")
    print("=" * 80)


if __name__ == "__main__":
    main()
