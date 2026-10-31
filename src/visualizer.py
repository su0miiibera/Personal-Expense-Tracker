"""
Expense Visualizer Module
Demonstrating:
- Matplotlib visualizations:
  1. Bar Chart (Category-wise expenditure)
  2. Pie Chart (Percentage distribution of categories)
  3. Line Plot (Expenditure timeline / monthly trend)
  4. Histogram (Distribution of expense amounts)
  5. Comprehensive 2x2 Dashboard Figure
- Figure styling, palettes, legends, labels, annotations
- File exporting of charts to PNG
"""

import os
from typing import Optional, List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from src.analytics import ExpenseAnalytics


class ExpenseVisualizer:
    """
    Generates rich graphical reports and charts using Matplotlib.
    """

    # Modern color palette for categories
    COLOR_PALETTE = [
        "#4361EE",  # Royal Blue
        "#3A0CA3",  # Indigo
        "#7209B7",  # Purple
        "#F72585",  # Pink/Magenta
        "#4CC9F0",  # Sky Blue
        "#2EC4B6",  # Teal
        "#FF9F1C",  # Orange
        "#E71D36",  # Crimson
        "#06D6A0",  # Emerald
        "#118AB2",  # Ocean
    ]

    def __init__(self, analytics: ExpenseAnalytics, output_dir: str = "reports"):
        self.analytics = analytics
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Configure global aesthetic defaults
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    def _prepare_data(self) -> bool:
        """Helper to ensure data exists before attempting to plot."""
        if self.analytics.is_empty():
            print("Cannot generate visual charts: Dataset is empty.")
            return False
        return True

    # ==========================================
    # 1. Bar Chart: Category-wise Expenditure
    # ==========================================

    def plot_category_bar_chart(
        self, save_path: Optional[str] = None, show: bool = True
    ) -> Optional[str]:
        """
        Creates a bar chart displaying total spending per category.
        """
        if not self._prepare_data():
            return None

        cat_summary = self.analytics.get_category_summary()
        categories = cat_summary["Category"].tolist()
        totals = cat_summary["Total"].tolist()

        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar(
            categories,
            totals,
            color=self.COLOR_PALETTE[: len(categories)],
            edgecolor="#222222",
            alpha=0.88,
            width=0.55,
        )

        # Annotate bar values on top
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"₹{height:,.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

        ax.set_title("Category-Wise Total Expenditure", fontsize=14, fontweight="bold", pad=12)
        ax.set_xlabel("Expense Category", fontsize=11, fontweight="bold")
        ax.set_ylabel("Total Amount (₹)", fontsize=11, fontweight="bold")
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
        plt.xticks(rotation=25, ha="right", fontsize=10)
        plt.tight_layout()

        target_file = save_path or os.path.join(self.output_dir, "category_bar_chart.png")
        fig.savefig(target_file, dpi=200)

        if show:
            plt.show()
        plt.close(fig)
        return target_file

    # ==========================================
    # 2. Pie Chart: Proportional Category Breakdown
    # ==========================================

    def plot_category_pie_chart(
        self, save_path: Optional[str] = None, show: bool = True
    ) -> Optional[str]:
        """
        Creates a pie chart with percentage shares of each category.
        """
        if not self._prepare_data():
            return None

        cat_summary = self.analytics.get_category_summary()
        categories = cat_summary["Category"].tolist()
        totals = cat_summary["Total"].tolist()

        fig, ax = plt.subplots(figsize=(8, 8))
        explode = [0.05 if i == 0 else 0 for i in range(len(categories))]  # Explode highest category

        wedges, texts, autotexts = ax.pie(
            totals,
            labels=categories,
            autopct="%1.1f%%",
            startangle=140,
            explode=explode,
            colors=self.COLOR_PALETTE[: len(categories)],
            wedgeprops={"edgecolor": "white", "linewidth": 1.5, "antialiased": True},
            textprops={"fontsize": 10},
        )

        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        ax.set_title("Expense Distribution by Category", fontsize=14, fontweight="bold", pad=15)
        plt.tight_layout()

        target_file = save_path or os.path.join(self.output_dir, "category_pie_chart.png")
        fig.savefig(target_file, dpi=200)

        if show:
            plt.show()
        plt.close(fig)
        return target_file

    # ==========================================
    # 3. Line Plot: Expenditure Trend Over Time
    # ==========================================

    def plot_monthly_line_trend(
        self, save_path: Optional[str] = None, show: bool = True
    ) -> Optional[str]:
        """
        Creates a line plot displaying temporal spending trend across months/dates.
        """
        if not self._prepare_data():
            return None

        monthly = self.analytics.get_monthly_summary()
        months = monthly["YearMonth"].tolist()
        totals = monthly["Total"].tolist()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(
            months,
            totals,
            marker="o",
            markersize=7,
            linewidth=2.5,
            color="#4361EE",
            label="Monthly Expenditure",
        )

        # Fill underneath for aesthetics
        ax.fill_between(months, totals, color="#4361EE", alpha=0.15)

        # Annotate points
        for i, (m, val) in enumerate(zip(months, totals)):
            ax.annotate(
                f"₹{val:,.0f}",
                xy=(m, val),
                xytext=(0, 7),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                fontweight="bold",
                color="#3A0CA3",
            )

        ax.set_title("Monthly Expenditure Trend", fontsize=14, fontweight="bold", pad=12)
        ax.set_xlabel("Billing Period (Year-Month)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Total Spent (₹)", fontsize=11, fontweight="bold")
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
        plt.xticks(rotation=30, ha="right", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="upper left")
        plt.tight_layout()

        target_file = save_path or os.path.join(self.output_dir, "monthly_line_plot.png")
        fig.savefig(target_file, dpi=200)

        if show:
            plt.show()
        plt.close(fig)
        return target_file

    # ==========================================
    # 4. Histogram: Amount Frequency Distribution
    # ==========================================

    def plot_amount_histogram(
        self, save_path: Optional[str] = None, show: bool = True
    ) -> Optional[str]:
        """
        Creates a histogram showing the frequency distribution of expense amounts.
        """
        if not self._prepare_data():
            return None

        amounts = self.analytics.df["Amount"].to_numpy()
        stats = self.analytics.get_numpy_statistics()

        fig, ax = plt.subplots(figsize=(9, 5))
        n_bins = max(5, min(20, len(amounts) // 2))

        n, bins, patches = ax.hist(
            amounts,
            bins=n_bins,
            color="#7209B7",
            edgecolor="white",
            alpha=0.8,
        )

        # Plot Mean and Median vertical reference lines
        ax.axvline(
            stats["mean"],
            color="#E71D36",
            linestyle="--",
            linewidth=2,
            label=f"Mean: ₹{stats['mean']:,.2f}",
        )
        ax.axvline(
            stats["median"],
            color="#06D6A0",
            linestyle="-.",
            linewidth=2,
            label=f"Median: ₹{stats['median']:,.2f}",
        )

        ax.set_title("Expense Amount Distribution (Histogram)", fontsize=14, fontweight="bold", pad=12)
        ax.set_xlabel("Expense Amount (₹)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Frequency (Count)", fontsize=11, fontweight="bold")

        ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
        ax.legend(loc="upper right")
        plt.tight_layout()

        target_file = save_path or os.path.join(self.output_dir, "amount_histogram.png")
        fig.savefig(target_file, dpi=200)

        if show:
            plt.show()
        plt.close(fig)
        return target_file

    # ==========================================
    # 5. Combined Dashboard: All 4 Visualizations
    # ==========================================

    def generate_comprehensive_dashboard(
        self, save_path: Optional[str] = None, show: bool = True
    ) -> Optional[str]:
        """
        Generates a 2x2 multi-panel graphical dashboard combining:
        1. Bar chart (Category total)
        2. Pie chart (Category share)
        3. Line plot (Monthly trend)
        4. Histogram (Amount distribution)
        """
        if not self._prepare_data():
            return None

        cat_summary = self.analytics.get_category_summary()
        monthly = self.analytics.get_monthly_summary()
        amounts = self.analytics.df["Amount"].to_numpy()
        stats = self.analytics.get_numpy_statistics()

        fig, axs = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(
            "Personal Expense Tracker — Executive Analytics Dashboard",
            fontsize=18,
            fontweight="bold",
            y=0.98,
        )

        # Subplot 1: Category Bar Chart (Top Left)
        ax1 = axs[0, 0]
        categories = cat_summary["Category"].tolist()
        totals = cat_summary["Total"].tolist()
        bars1 = ax1.bar(
            categories,
            totals,
            color=self.COLOR_PALETTE[: len(categories)],
            edgecolor="#333",
            alpha=0.85,
        )
        for b in bars1:
            ax1.annotate(
                f"₹{b.get_height():,.0f}",
                xy=(b.get_x() + b.get_width() / 2, b.get_height()),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                fontsize=8,
                fontweight="bold",
            )
        ax1.set_title("Total Expenditure by Category", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Total (₹)")
        ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
        ax1.tick_params(axis="x", rotation=25)

        # Subplot 2: Pie Chart (Top Right)
        ax2 = axs[0, 1]
        ax2.pie(
            totals,
            labels=categories,
            autopct="%1.1f%%",
            startangle=140,
            colors=self.COLOR_PALETTE[: len(categories)],
            wedgeprops={"edgecolor": "white", "linewidth": 1.2},
            textprops={"fontsize": 9},
        )
        ax2.set_title("Spending Breakdown by Percentage", fontsize=12, fontweight="bold")

        # Subplot 3: Monthly Line Trend (Bottom Left)
        ax3 = axs[1, 0]
        months = monthly["YearMonth"].tolist()
        month_totals = monthly["Total"].tolist()
        ax3.plot(months, month_totals, marker="o", color="#4361EE", linewidth=2.2, label="Monthly Trend")
        ax3.fill_between(months, month_totals, color="#4361EE", alpha=0.15)
        for m, val in zip(months, month_totals):
            ax3.annotate(
                f"₹{val:,.0f}",
                xy=(m, val),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                fontsize=8,
            )
        ax3.set_title("Monthly Spending Trend", fontsize=12, fontweight="bold")
        ax3.set_ylabel("Total (₹)")
        ax3.yaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
        ax3.tick_params(axis="x", rotation=25)
        ax3.grid(True, linestyle="--", alpha=0.5)

        # Subplot 4: Histogram (Bottom Right)
        ax4 = axs[1, 1]
        n_bins = max(5, min(15, len(amounts) // 2))
        ax4.hist(amounts, bins=n_bins, color="#7209B7", edgecolor="white", alpha=0.8)
        ax4.axvline(stats["mean"], color="#E71D36", linestyle="--", linewidth=1.8, label=f"Mean (₹{stats['mean']:,.0f})")
        ax4.axvline(stats["median"], color="#06D6A0", linestyle="-.", linewidth=1.8, label=f"Median (₹{stats['median']:,.0f})")
        ax4.set_title("Expense Frequency Distribution", fontsize=12, fontweight="bold")
        ax4.set_xlabel("Amount (₹)")
        ax4.set_ylabel("Count")
        ax4.xaxis.set_major_formatter(ticker.StrMethodFormatter("₹{x:,.0f}"))
        ax4.legend(loc="upper right", fontsize=9)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        target_file = save_path or os.path.join(self.output_dir, "spending_dashboard.png")
        fig.savefig(target_file, dpi=200)

        if show:
            plt.show()
        plt.close(fig)
        return target_file
