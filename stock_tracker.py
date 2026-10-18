
import pandas as pd
from pathlib import Path

# Project folder and dataset path
folder = Path(__file__).parent
file_path = folder / "constituents.csv"

print("\n===== STOCK PORTFOLIO TRACKER =====")

try:
    # Load S&P 500 company dataset
    companies = pd.read_csv(file_path)
    companies.columns = companies.columns.str.strip()

    print("\nDataset loaded successfully!")
    print("Total companies:", len(companies))

    # Display first 5 companies
    print("\n===== COMPANY DATA =====")
    print(companies.head().to_string(index=False))

    # Sector analysis
    sector_col = next(
        (c for c in companies.columns if c.lower() == "sector"),
        None
    )

    if sector_col:
        sector_report = (
            companies[sector_col]
            .fillna("Unknown")
            .value_counts()
            .rename_axis("Sector")
            .reset_index(name="Company Count")
        )

        print("\n===== SECTOR ANALYSIS =====")
        print(sector_report.to_string(index=False))
        sector_report.to_csv(
            folder / "sector_summary.csv", index=False
        )

    # Find company name and ticker columns
    name_col = next(
        (c for c in companies.columns if c.lower() == "name"),
        None
    )
    symbol_col = next(
        (c for c in companies.columns
         if c.lower() in ("symbol", "ticker")),
        None
    )

    portfolio = []

    print("\n===== ADD STOCKS TO PORTFOLIO =====")
    print("Enter DONE as ticker when finished.")

    while True:
        ticker = input("\nEnter stock ticker: ").strip()

        if ticker.upper() == "DONE":
            break

        if not ticker:
            print("Please enter a ticker.")
            continue

        # Check whether ticker exists in the dataset
        if symbol_col:
            matches = companies[
                companies[symbol_col].astype(str).str.upper()
                == ticker.upper()
            ]
        elif name_col:
            matches = companies[
                companies[name_col].astype(str).str.contains(
                    ticker, case=False, na=False, regex=False
                )
            ]
        else:
            print("Ticker/name column not found in dataset.")
            break

        if matches.empty:
            print("Company not found. Check the ticker and try again.")
            continue

        company = matches.iloc[0]
        company_name = (
            company[name_col] if name_col else ticker.upper()
        )

        print("Company:", company_name)

        try:
            quantity = int(input("Enter quantity: "))
            buy_price = float(input("Enter buy price per share: "))
            current_price = float(
                input("Enter current price per share: ")
            )

            if quantity <= 0 or buy_price < 0 or current_price < 0:
                print("Quantity must be positive and prices non-negative.")
                continue

        except ValueError:
            print("Please enter valid numeric values.")
            continue

        investment = quantity * buy_price
        current_value = quantity * current_price
        profit_loss = current_value - investment
        profit_percent = (
            profit_loss / investment * 100 if investment else 0
        )

        portfolio.append({
            "Ticker": ticker.upper(),
            "Company": company_name,
            "Quantity": quantity,
            "Buy Price": buy_price,
            "Current Price": current_price,
            "Investment": investment,
            "Current Value": current_value,
            "Profit/Loss": profit_loss,
            "Profit/Loss %": round(profit_percent, 2)
        })

    # Generate portfolio report
    if portfolio:
        report = pd.DataFrame(portfolio)
        report.to_csv(folder / "portfolio_report.csv", index=False)

        print("\n===== PORTFOLIO REPORT =====")
        print(report.to_string(index=False))

        print("\nTotal Investment:", round(report["Investment"].sum(), 2))
        print("Current Portfolio Value:",
              round(report["Current Value"].sum(), 2))
        print("Total Profit/Loss:", round(report["Profit/Loss"].sum(), 2))

        print("\nPortfolio report saved to portfolio_report.csv")
    else:
        print("\nNo stocks added. Portfolio report was not created.")

except FileNotFoundError:
    print("\nERROR: constituents.csv was not found.")
    print("Save it in the same folder as stock_tracker.py.")

except Exception as error:
    print("\nAn error occurred:", error)
