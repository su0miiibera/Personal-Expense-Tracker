"""
Expense Analytics Module
Demonstrating:
- NumPy (Vectorized numerical computations, statistical metrics, percentiles)
- Pandas (DataFrames, GroupBy, Aggregations, Datetime indexing, Pivot tables)
- Object-Oriented Design (ExpenseAnalytics class)
"""

from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from src.models import Expense


class ExpenseAnalytics:
    """
    Performs data science and statistical analysis on expense data
    using NumPy and Pandas.
    """

    def __init__(self, expenses: Optional[List[Expense]] = None):
        self.df: pd.DataFrame = pd.DataFrame()
        if expenses:
            self.load_expenses(expenses)

    def load_expenses(self, expenses: List[Expense]) -> None:
        """
        Converts a list of Expense objects into a Pandas DataFrame.
        Demonstrates: Pandas DataFrame construction and Datetime conversion.
        """
        if not expenses:
            self.df = pd.DataFrame(columns=["ID", "Date", "Category", "Amount", "Description"])
            return

        records = [exp.to_dict() for exp in expenses]
        self.df = pd.DataFrame(records)
        # Rename columns to standardized titles
        self.df.rename(
            columns={
                "id": "ID",
                "date": "Date",
                "category": "Category",
                "amount": "Amount",
                "description": "Description",
            },
            inplace=True,
        )
        # Convert Date string to Pandas Datetime
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df["Amount"] = pd.to_numeric(self.df["Amount"], errors="coerce")
        self.df["YearMonth"] = self.df["Date"].dt.to_period("M").astype(str)

    def is_empty(self) -> bool:
        """Checks if dataset has no records."""
        return self.df.empty

    # ==========================================
    # NumPy Numerical & Statistical Analysis
    # ==========================================

    def get_numpy_statistics(self) -> Dict[str, float]:
        """
        Computes key descriptive statistics using NumPy array operations.
        Demonstrates: NumPy arrays, np.mean, np.median, np.std, np.percentile, np.min, np.max.
        """
        if self.df.empty:
            return {
                "count": 0,
                "total": 0.0,
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
                "p25": 0.0,
                "p75": 0.0,
                "iqr": 0.0,
            }

        # Convert Pandas Series to NumPy 1D array
        amounts_array: np.ndarray = self.df["Amount"].to_numpy()

        total = float(np.sum(amounts_array))
        mean = float(np.mean(amounts_array))
        median = float(np.median(amounts_array))
        std_dev = float(np.std(amounts_array))  # standard deviation
        minimum = float(np.min(amounts_array))
        maximum = float(np.max(amounts_array))
        p25 = float(np.percentile(amounts_array, 25))
        p75 = float(np.percentile(amounts_array, 75))
        iqr = float(p75 - p25)

        return {
            "count": len(amounts_array),
            "total": round(total, 2),
            "mean": round(mean, 2),
            "median": round(median, 2),
            "std_dev": round(std_dev, 2),
            "min": round(minimum, 2),
            "max": round(maximum, 2),
            "p25": round(p25, 2),
            "p75": round(p75, 2),
            "iqr": round(iqr, 2),
        }

    # ==========================================
    # Pandas GroupBy & Summaries
    # ==========================================

    def get_category_summary(self) -> pd.DataFrame:
        """
        Aggregates spending by Category using Pandas.
        Calculates Total, Count, Mean, Percentage Share.
        Demonstrates: Pandas groupby, agg, and vectorized column operations.
        """
        if self.df.empty:
            return pd.DataFrame()

        summary = (
            self.df.groupby("Category")["Amount"]
            .agg(
                Total="sum",
                Count="count",
                Average="mean",
                Min="min",
                Max="max",
            )
            .reset_index()
        )

        total_spent = summary["Total"].sum()
        # Vectorized percentage calculation with NumPy / Pandas
        if total_spent > 0:
            summary["Percentage"] = np.round((summary["Total"] / total_spent) * 100, 2)
        else:
            summary["Percentage"] = 0.0

        # Round monetary columns
        summary["Total"] = summary["Total"].round(2)
        summary["Average"] = summary["Average"].round(2)
        summary["Min"] = summary["Min"].round(2)
        summary["Max"] = summary["Max"].round(2)

        # Sort in descending order by total expenditure
        summary.sort_values(by="Total", ascending=False, inplace=True)
        return summary

    def get_monthly_summary(self) -> pd.DataFrame:
        """
        Aggregates spending by Month (YYYY-MM).
        Demonstrates: Grouping over temporal periods, aggregation, sorting.
        """
        if self.df.empty:
            return pd.DataFrame()

        monthly = (
            self.df.groupby("YearMonth")["Amount"]
            .agg(
                Total="sum",
                Count="count",
                Average="mean",
            )
            .reset_index()
        )

        monthly["Total"] = monthly["Total"].round(2)
        monthly["Average"] = monthly["Average"].round(2)
        monthly.sort_values(by="YearMonth", ascending=True, inplace=True)
        return monthly
