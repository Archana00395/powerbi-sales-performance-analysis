"""Clean the sales dataset and save a quality-checked CSV copy."""

from pathlib import Path

import pandas as pd


def sales_checks(data):
    """Return counts of non-numeric and negative values in Sales."""
    sales = pd.to_numeric(data["Sales"], errors="coerce")
    invalid = data["Sales"].notna() & sales.isna()
    return int(invalid.sum()), int((sales < 0).sum())


def print_quality_summary(label, data):
    """Print comparable quality checks for a dataset."""
    invalid_sales, negative_sales = sales_checks(data)
    print(f"\n{label}")
    print("-" * 80)
    print(f"Rows: {len(data)}")
    print(f"Columns: {len(data.columns)}")
    print(f"Total missing values: {int(data.isna().sum().sum())}")
    print(f"Exact duplicate rows: {int(data.duplicated().sum())}")
    print(f"Invalid (non-numeric) Sales values: {invalid_sales}")
    print(f"Negative Sales values: {negative_sales}")
    print("Data types:")
    print(data.dtypes.to_string())


def main():
    """Clean the source CSV without changing it or inventing replacement data."""
    project_dir = Path(__file__).resolve().parents[1]
    input_path = project_dir / "data" / "sales_dataset.csv"
    output_path = project_dir / "output" / "cleaned_sales_dataset.csv"

    data = pd.read_csv(input_path)
    if "Sales" not in data.columns:
        raise ValueError(f"Required 'Sales' column was not found in {input_path}")

    print_quality_summary("BEFORE CLEANING", data)

    # Drop only fully identical records; rows sharing an ID but differing in
    # other fields are retained because they may represent meaningful records.
    duplicate_count = int(data.duplicated().sum())
    data = data.drop_duplicates()
    print(f"\nExact duplicate rows removed: {duplicate_count}")

    # Convert known numeric fields without coercing invalid text into missing
    # values. This preserves existing numeric values and surfaces bad input.
    numeric_columns = (
        "Quantity",
        "Unit_Price",
        "Unit_Cost",
        "Sales",
        "Cost",
        "Profit",
    )
    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="raise")

    # The inspected dataset stores ISO-formatted order dates as strings.
    if "Order_Date" in data.columns:
        data["Order_Date"] = pd.to_datetime(data["Order_Date"], errors="raise")

    invalid_sales, negative_sales = sales_checks(data)
    if invalid_sales:
        raise ValueError(
            f"Found {invalid_sales} non-numeric Sales value(s); "
            "cleaning stopped without writing an output file."
        )

    # Keep missing values as missing rather than inventing replacement values.
    # The inspected dataset has none, so no imputation or row removal is needed.
    print("\nMissing values are preserved as missing; no values were imputed.")
    if negative_sales:
        print(
            f"WARNING: Found {negative_sales} negative Sales value(s); "
            "they are reported, not changed."
        )
    else:
        print("Negative Sales check: none found.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)

    print_quality_summary("AFTER CLEANING", data)
    print(f"\nCleaned dataset saved to: {output_path}")


if __name__ == "__main__":
    main()
