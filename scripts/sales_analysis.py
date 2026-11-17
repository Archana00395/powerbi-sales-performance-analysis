"""Summarize sales performance and export an Excel workbook and observations."""

from math import isclose
from pathlib import Path

import pandas as pd


def format_table(data, percent_columns=()):
    """Return a readable terminal table without changing stored values."""
    formatters = {
        column: lambda value: f"{value:,.0f}"
        for column in ("Sales", "Profit", "Records")
        if column in data.columns
    }
    for column in percent_columns:
        formatters[column] = lambda value: f"{value:.2f}%"
    return data.to_string(index=False, formatters=formatters)


def main():
    """Analyze the cleaned CSV, validate totals, and write project outputs."""
    project_dir = Path(__file__).resolve().parents[1]
    input_path = project_dir / "output" / "cleaned_sales_dataset.csv"
    workbook_path = project_dir / "output" / "sales_analysis.xlsx"
    observations_path = project_dir / "observations.txt"

    data = pd.read_csv(input_path)
    required_columns = {"Sales", "Profit", "Category", "Region"}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(
            f"Required analysis column(s) missing from {input_path}: "
            f"{', '.join(sorted(missing_columns))}"
        )
    if data.empty:
        raise ValueError(f"No records found in {input_path}")

    # Parse existing figures as numbers; invalid values raise instead of being
    # silently replaced or dropped.
    for column in ("Sales", "Profit"):
        data[column] = pd.to_numeric(data[column], errors="raise")

    total_sales = data["Sales"].sum()
    total_profit = data["Profit"].sum()
    if total_sales == 0:
        raise ValueError("Overall Profit Margin cannot be calculated when total Sales is zero.")
    profit_margin = total_profit / total_sales * 100

    category_analysis = (
        data.groupby("Category", dropna=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Records=("Sales", "size"))
        .reset_index()
    )
    category_analysis["Sales Contribution (%)"] = (
        category_analysis["Sales"] / total_sales * 100
    )
    category_analysis = category_analysis.sort_values(
        "Sales", ascending=False, kind="stable"
    ).reset_index(drop=True)

    region_analysis = (
        data.groupby("Region", dropna=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Records=("Sales", "size"))
        .reset_index()
        .sort_values("Sales", ascending=False, kind="stable")
        .reset_index(drop=True)
    )

    category_sales_total = category_analysis["Sales"].sum()
    region_sales_total = region_analysis["Sales"].sum()
    category_reconciles = category_sales_total == total_sales
    region_reconciles = region_sales_total == total_sales
    contribution_total = category_analysis["Sales Contribution (%)"].sum()
    contributions_reconcile = isclose(
        contribution_total, 100.0, rel_tol=0.0, abs_tol=1e-9
    )
    if not (category_reconciles and region_reconciles and contributions_reconcile):
        raise ValueError(
            "Sales analysis validation failed: "
            f"category={category_reconciles}, region={region_reconciles}, "
            f"category contributions={contributions_reconcile} "
            f"({contribution_total:.12f}%)."
        )

    highest_category = category_analysis.iloc[0]
    lowest_category = category_analysis.iloc[-1]
    highest_region = region_analysis.iloc[0]
    lowest_region = region_analysis.iloc[-1]

    summary = pd.DataFrame(
        [
            ("Total Sales", total_sales),
            ("Total Profit", total_profit),
            ("Overall Profit Margin (%)", profit_margin),
            ("Highest-performing Category", highest_category["Category"]),
            ("Highest Category Sales", highest_category["Sales"]),
            ("Lowest-performing Category", lowest_category["Category"]),
            ("Lowest Category Sales", lowest_category["Sales"]),
            ("Highest-performing Region", highest_region["Region"]),
            ("Highest Region Sales", highest_region["Sales"]),
            ("Lowest-performing Region", lowest_region["Region"]),
            ("Lowest Region Sales", lowest_region["Sales"]),
            ("Category Sales Reconciliation", "PASS"),
            ("Region Sales Reconciliation", "PASS"),
            ("Category Contributions Total (%)", contribution_total),
            ("Category Contributions Validation", "PASS"),
        ],
        columns=("Metric", "Value"),
    )

    # These observations are computed from the sorted results above.
    lowest_region_difference = highest_region["Sales"] - lowest_region["Sales"]
    observations = [
        f"The analysis covers {len(data):,} sales records.",
        f"Total Sales were {total_sales:,.0f}.",
        (
            f"Total Profit was {total_profit:,.0f}, with an overall Profit Margin "
            f"of {profit_margin:.2f}%."
        ),
        (
            f"{highest_category['Category']} was the highest-performing category by Sales "
            f"at {highest_category['Sales']:,.0f} "
            f"({highest_category['Sales Contribution (%)']:.2f}% of total Sales)."
        ),
        (
            f"{lowest_category['Category']} was the lowest-performing category by Sales "
            f"at {lowest_category['Sales']:,.0f}."
        ),
        (
            f"{highest_region['Region']} was the highest-performing region by Sales "
            f"at {highest_region['Sales']:,.0f}."
        ),
        (
            f"{lowest_region['Region']} was the lowest-performing region by Sales "
            f"at {lowest_region['Sales']:,.0f}."
        ),
        (
            f"Sales in {highest_region['Region']} exceeded Sales in {lowest_region['Region']} "
            f"by {lowest_region_difference:,.0f}."
        ),
    ]
    if len(category_analysis) > 1:
        runner_up_category = category_analysis.iloc[1]
        observations.insert(
            5,
            (
                f"The leading category, {highest_category['Category']}, exceeded "
                f"{runner_up_category['Category']} by "
                f"{highest_category['Sales'] - runner_up_category['Sales']:,.0f} in Sales."
            ),
        )

    workbook_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Overall Summary", index=False)
        category_analysis.to_excel(writer, sheet_name="Category Analysis", index=False)
        region_analysis.to_excel(writer, sheet_name="Region Analysis", index=False)

    observations_path.write_text(
        "\n".join(f"- {observation}" for observation in observations) + "\n",
        encoding="utf-8",
    )

    print("SALES ANALYSIS")
    print("=" * 72)
    print(f"Input dataset: {input_path}")
    print(f"Records analyzed: {len(data):,}")
    print(f"Total Sales: {total_sales:,.0f}")
    print(f"Total Profit: {total_profit:,.0f}")
    print(f"Overall Profit Margin: {profit_margin:.2f}%")

    print("\nSales by Category:")
    print(format_table(category_analysis, ("Sales Contribution (%)",)))
    print("\nSales by Region:")
    print(format_table(region_analysis))

    print("\nPerformance:")
    print(
        f"Highest-performing category: {highest_category['Category']} "
        f"({highest_category['Sales']:,.0f})"
    )
    print(
        f"Lowest-performing category: {lowest_category['Category']} "
        f"({lowest_category['Sales']:,.0f})"
    )
    print(
        f"Highest-performing region: {highest_region['Region']} "
        f"({highest_region['Sales']:,.0f})"
    )
    print(
        f"Lowest-performing region: {lowest_region['Region']} "
        f"({lowest_region['Sales']:,.0f})"
    )

    print("\nValidation:")
    print(
        f"Category Sales reconcile: PASS "
        f"({category_sales_total:,.0f} = {total_sales:,.0f})"
    )
    print(
        f"Regional Sales reconcile: PASS "
        f"({region_sales_total:,.0f} = {total_sales:,.0f})"
    )
    print(f"Category contributions total: {contribution_total:.12f}% (PASS)")
    print(f"\nWorkbook saved to: {workbook_path}")
    print(f"Observations saved to: {observations_path}")
    print("\nBusiness observations:")
    for observation in observations:
        print(f"- {observation}")


if __name__ == "__main__":
    main()