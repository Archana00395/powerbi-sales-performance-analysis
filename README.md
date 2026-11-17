# Sales Performance Report

## Project overview

This project inspects, cleans, and analyzes the supplied sales dataset. It
produces a cleaned CSV, an Excel workbook with sales summaries, and a set of
data-based business observations.

## Objectives

- Inspect the dataset structure and data quality.
- Preserve the source data while preparing a cleaned copy.
- Summarize sales and profit by category and region.
- Validate sales totals and category contribution percentages.
- Export repeatable results for reporting.

## Dataset description

The supplied `data/sales_dataset.csv` contains 180 records and 13 columns:
`Order_ID`, `Order_Date`, `Region`, `Category`, `Product`, `Channel`,
`Customer_Type`, `Quantity`, `Unit_Price`, `Unit_Cost`, `Sales`, `Cost`, and
`Profit`.

The inspection found no missing values or exact duplicate rows. Numeric fields
are `Quantity`, `Unit_Price`, `Unit_Cost`, `Sales`, `Cost`, and `Profit`.
`Order_Date` is stored as text in the source file and is parsed as a date in the
cleaning step. The dataset does not specify a currency or unit for the monetary
figures, so results are reported in the dataset's units.

**Publication note:** The reviewed file contains order identifiers and
transaction-level sales, costs, and profits. No names, email addresses, phone
numbers, or SSN-like values were found in the dataset, and no credential or
API-key patterns were found in the reviewed project text. This does not
establish that the transaction data is non-confidential or licensed for
redistribution. Confirm the dataset's ownership and public-release permission
before publishing it.

## Technology stack

- Python 3.14.3 (tested)
- pandas 3.0.6
- openpyxl 3.1.5 (Excel workbook writer)

Install the Python dependencies with:

```powershell
python -m pip install -r requirements.txt
```

## Project structure

```text
Sales_Performance_Report/
├── data/
│   └── sales_dataset.csv
├── scripts/
│   ├── inspect_data.py
│   ├── clean_data.py
│   └── sales_analysis.py
├── output/
│   ├── cleaned_sales_dataset.csv
│   └── sales_analysis.xlsx
├── observations.txt
├── requirements.txt
├── .gitignore
└── README.md
```

## Data inspection process

Run `scripts/inspect_data.py` to load the original CSV and report its row and
column counts, column names, data types, missing values, exact duplicate rows,
numerical and categorical columns, summary statistics, and the detected Sales,
Category, and Region columns.

## Data cleaning process

Run `scripts/clean_data.py` to create `output/cleaned_sales_dataset.csv`. It
removes only fully identical rows, converts the observed numeric fields to
numeric types, parses `Order_Date`, and checks whether Sales values are numeric
or negative. Existing missing values are preserved rather than imputed, and
the original CSV is not modified.

## Sales analysis methodology

Run `scripts/sales_analysis.py` to analyze the cleaned CSV. Sales and Profit
are summed overall and grouped by Category and Region. Category contribution
is calculated as:

```text
category Sales / total Sales * 100
```

Overall Profit Margin is calculated as:

```text
total Profit / total Sales * 100
```

The script validates that category and regional Sales each reconcile to total
Sales and that the unrounded category contributions sum to approximately
100%. It writes three sheets to `output/sales_analysis.xlsx`: `Overall
Summary`, `Category Analysis`, and `Region Analysis`. It also generates
`observations.txt`. Percentage values displayed to two decimal places may not
sum to exactly 100.00% due to rounding; validation uses unrounded values.

## Key findings

Based on the supplied 180-record dataset:

- Total Sales: **942,606**
- Total Profit: **298,496**
- Overall Profit Margin: **31.67%**
- Highest-sales category: **Home**, 315,888 (33.51% contribution)
- Lowest-sales category: **Fashion**, 167,628 (17.78% contribution)
- Highest-sales region: **North**, 297,912
- Lowest-sales region: **West**, 208,148

These figures use the dataset's units; no currency is specified in the source.

## How to run the Python scripts

From the project root, install dependencies and run the scripts in order:

```powershell
python -m pip install -r requirements.txt
python scripts/inspect_data.py
python scripts/clean_data.py
python scripts/sales_analysis.py
```

The inspection and cleaning scripts read `data/sales_dataset.csv`. The
analysis script reads `output/cleaned_sales_dataset.csv`. The scripts resolve
these paths relative to their own location.

## Future improvements

- Add automated tests for cleaning, grouping, and reconciliation behavior.
- Parse and validate dates with an explicit input format.
- Add charts or a Power BI report built from the cleaned dataset.
- Document the source dataset's license and confirm its publication rights.
- Add currency or unit metadata if it becomes available from the source.