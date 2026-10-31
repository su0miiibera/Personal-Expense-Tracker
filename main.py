"""
Personal Expense Tracker & Analysis System
Interactive Menu-Driven Application

Concepts Highlighted:
- Loops (while loops for menu control, for loops for listing)
- Conditions (menu choices, input checks, validations)
- Exception Handling (try-except blocks for input validation)
- Classes and Objects (Expense, ExpenseTracker, ExpenseAnalytics, ExpenseVisualizer)
- Collections (Lists, Dicts, Tuples, Sets)
- NumPy, Pandas & Matplotlib Integration
"""

import os
import sys
import shutil
import csv
from datetime import datetime

# Configure UTF-8 encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from src.models import (
    DEFAULT_CATEGORIES_TUPLE,
    ExpenseValidationError,
    InvalidAmountError,
    InvalidDateError,
)
from src.tracker import ExpenseTracker
from src.analytics import ExpenseAnalytics
from src.visualizer import ExpenseVisualizer


CSV_FILEPATH = "data/expenses.csv"
SAMPLE_FILEPATH = "data/sample_expenses.csv"


def clear_console():
    """Clears console if desired; kept portable."""
    pass


def print_banner():
    print("\n" + "=" * 75)
    print("      🪙  PERSONAL EXPENSE TRACKER & ANALYSIS SYSTEM  🪙")
    print("   Demonstrating Core Python, OOP, NumPy, Pandas & Matplotlib")
    print("=" * 75)


def display_menu():
    print("""
[1] ➕ Add Expense
[2] 📋 View All Expenses
[3] 🔍 Filter / Search Expenses
[4] 🔄 Sort Expenses (Built-in Sort)
[5] ✏️  Delete / Remove Expense
[6] 📁 Load / Reset Dataset
[7] 📈 Generate Graphical Charts (Matplotlib)
[0] 🚪 Exit Application
""")


def prompt_expense_input() -> tuple:
    """Prompts and collects expense fields from user."""
    print("\n--- Enter New Expense Details ---")
    
    # 1. Date prompt with default to today
    today_str = datetime.now().strftime("%Y-%m-%d")
    date_input = input(f"Date (YYYY-MM-DD) [Press Enter for Today: {today_str}]: ").strip()
    if not date_input:
        date_input = today_str

    # 2. Category prompt with options
    print("Available Standard Categories:")
    for idx, cat in enumerate(DEFAULT_CATEGORIES_TUPLE, 1):
        print(f"  {idx}. {cat}", end="  " if idx % 4 != 0 else "\n")
    print()

    cat_choice = input("Select Category (Type name or number): ").strip()
    if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(DEFAULT_CATEGORIES_TUPLE):
        category = DEFAULT_CATEGORIES_TUPLE[int(cat_choice) - 1]
    else:
        category = cat_choice

    # 3. Amount prompt
    amount_str = input("Amount (₹ / Rs.): ").strip()

    # 4. Description prompt
    desc = input("Description / Note (optional): ").strip()

    return date_input, category, amount_str, desc


def handle_add_expense(tracker: ExpenseTracker):
    try:
        date, category, amount_str, desc = prompt_expense_input()
        new_exp = tracker.add_expense(
            date=date,
            category=category,
            amount=amount_str,
            description=desc,
        )
        print(f"\n✅ Expense added successfully:\n   {new_exp}")
    except (InvalidAmountError, InvalidDateError, ExpenseValidationError) as e:
        print(f"\n❌ Validation Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def print_expense_table(expenses, title="Recorded Expenses"):
    print(f"\n--- {title} (Total: {len(expenses)}) ---")
    if not expenses:
        print("  (No records found)")
        return

    print(f"{'ID':<5} | {'Date':<10} | {'Category':<15} | {'Amount (₹)':>10} | {'Description'}")
    print("-" * 75)
    for exp in expenses:
        exp_id = exp.expense_id if exp.expense_id is not None else "-"
        print(f"{exp_id:<5} | {exp.date:<10} | {exp.category:<15} | {exp.amount:>10.2f} | {exp.description}")
    print("-" * 75)


def handle_view_all(tracker: ExpenseTracker):
    expenses = tracker.get_all_expenses()
    print_expense_table(expenses, "All Recorded Expenses")
    if expenses:
        total = tracker.calculate_total_expenditure()
        avg = tracker.calculate_average_expenditure()
        highest, lowest = tracker.get_highest_and_lowest_expenses()
        print(f"Summary: Total = ₹{total:,.2f} | Count = {len(expenses)} | Avg = ₹{avg:,.2f}")
        if highest and lowest:
            print(f"Highest: ₹{highest.amount:,.2f} ({highest.category}) | Lowest: ₹{lowest.amount:,.2f} ({lowest.category})")


def handle_filter_expenses(tracker: ExpenseTracker):
    print("\n--- Filter Expenses ---")
    cat = input("Category (leave blank for all): ").strip() or None
    start = input("Start Date (YYYY-MM-DD or blank): ").strip() or None
    end = input("End Date (YYYY-MM-DD or blank): ").strip() or None
    min_amt_str = input("Minimum Amount (or blank): ").strip()
    max_amt_str = input("Maximum Amount (or blank): ").strip()

    min_amt = float(min_amt_str) if min_amt_str else None
    max_amt = float(max_amt_str) if max_amt_str else None

    results = tracker.filter_expenses(
        category=cat,
        start_date=start,
        end_date=end,
        min_amount=min_amt,
        max_amount=max_amt,
    )
    print_expense_table(results, "Filtered Results")


def handle_sort_expenses(tracker: ExpenseTracker):
    print("\n--- Sort Expenses ---")
    print("Sort by:")
    print("  1. Date")
    print("  2. Amount")
    print("  3. Category")
    choice = input("Select sort field [1-3, default 1]: ").strip()
    by_map = {"1": "date", "2": "amount", "3": "category"}
    sort_by = by_map.get(choice, "date")

    order = input("Order: (A)scending or (D)escending? [default A]: ").strip().lower()
    ascending = not order.startswith("d")

    sorted_list = tracker.sort_expenses(by=sort_by, ascending=ascending)
    order_str = "Ascending" if ascending else "Descending"
    print_expense_table(sorted_list, f"Sorted by {sort_by.title()} ({order_str}) via Built-in Sort")


def handle_delete_expense(tracker: ExpenseTracker):
    print("\n--- Delete Expense ---")
    id_str = input("Enter Expense ID to delete: ").strip()
    if not id_str.isdigit():
        print("❌ Invalid ID format. Must be a numeric ID.")
        return

    exp_id = int(id_str)
    target = tracker.get_expense_by_id(exp_id)
    if not target:
        print(f"❌ Expense with ID {exp_id} not found.")
        return

    confirm = input(f"Are you sure you want to delete {target}? (y/N): ").strip().lower()
    if confirm == "y":
        if tracker.delete_expense(exp_id):
            print(f"✅ Expense #{exp_id} deleted successfully.")
        else:
            print("❌ Failed to delete expense.")
    else:
        print("Cancelled.")



def handle_visualizations(tracker: ExpenseTracker):
    expenses = tracker.get_all_expenses()
    if not expenses:
        print("\n❌ No expense data available to plot.")
        return

    analytics = ExpenseAnalytics(expenses)
    visualizer = ExpenseVisualizer(analytics, output_dir="reports")

    print("\n--- Visualizations (Matplotlib) ---")
    print("  1. Category Bar Chart")
    print("  2. Category Distribution Pie Chart")
    print("  3. Monthly Spending Line Trend")
    print("  4. Expense Amount Distribution Histogram")
    print("  5. Comprehensive 2x2 Dashboard (All in One)")
    print("  6. Generate and Save All Reports")

    choice = input("Select visual option [1-6]: ").strip()

    if choice == "1":
        path = visualizer.plot_category_bar_chart(show=True)
        print(f"✅ Bar chart saved to: {path}")
    elif choice == "2":
        path = visualizer.plot_category_pie_chart(show=True)
        print(f"✅ Pie chart saved to: {path}")
    elif choice == "3":
        path = visualizer.plot_monthly_line_trend(show=True)
        print(f"✅ Line plot saved to: {path}")
    elif choice == "4":
        path = visualizer.plot_amount_histogram(show=True)
        print(f"✅ Histogram saved to: {path}")
    elif choice == "5":
        path = visualizer.generate_comprehensive_dashboard(show=True)
        print(f"✅ Executive Dashboard saved to: {path}")
    elif choice == "6":
        b = visualizer.plot_category_bar_chart(show=False)
        p = visualizer.plot_category_pie_chart(show=False)
        l = visualizer.plot_monthly_line_trend(show=False)
        h = visualizer.plot_amount_histogram(show=False)
        d = visualizer.generate_comprehensive_dashboard(show=False)
        print("\n✅ All 5 graphical reports successfully generated:")
        print(f"   • {b}\n   • {p}\n   • {l}\n   • {h}\n   • {d}")
    else:
        print("Invalid choice.")


def handle_load_dataset(tracker: ExpenseTracker):
    print("\n--- 📁 Load / Reset Dataset ---")
    print(f"Current Active Dataset File : {tracker.storage_filepath}")
    print(f"Default Sample Dataset File : {SAMPLE_FILEPATH}")
    print("\nYou can:")
    print("  • Enter a filename or path to load an existing CSV dataset")
    print("  • Enter a new filename to initialize a new dataset")
    print("  • Press [Enter] to reload / reset to the default sample dataset")

    file_input = input("\nEnter dataset file name/path [Press Enter for default sample]: ").strip()

    if not file_input:
        target_path = SAMPLE_FILEPATH
    else:
        # Check direct path
        if os.path.exists(file_input):
            target_path = file_input
        # Check inside data/ directory
        elif os.path.exists(os.path.join("data", file_input)):
            target_path = os.path.join("data", file_input)
        # Check if .csv extension was omitted
        elif not file_input.lower().endswith(".csv") and os.path.exists(file_input + ".csv"):
            target_path = file_input + ".csv"
        elif not file_input.lower().endswith(".csv") and os.path.exists(os.path.join("data", file_input + ".csv")):
            target_path = os.path.join("data", file_input + ".csv")
        else:
            # File does not exist yet; determine desired path for initialization
            filename = file_input if file_input.lower().endswith(".csv") else file_input + ".csv"
            # If no directory was provided, default to data/
            if not os.path.dirname(filename):
                target_path = os.path.join("data", filename)
            else:
                target_path = filename

    if os.path.exists(target_path):
        if os.path.abspath(target_path) == os.path.abspath(SAMPLE_FILEPATH):
            confirm = input(f"Reset active dataset with records from default sample '{target_path}'? (y/N): ").strip().lower()
        else:
            confirm = input(f"Load records from '{target_path}' into the expense tracker? (y/N): ").strip().lower()

        if confirm == "y":
            try:
                if os.path.abspath(target_path) == os.path.abspath(SAMPLE_FILEPATH):
                    # Copy sample data into primary CSV file so original sample template remains pristine
                    tracker.storage_filepath = CSV_FILEPATH
                    shutil.copy(SAMPLE_FILEPATH, tracker.storage_filepath)
                    count = tracker.load_from_csv()
                    print(f"✅ Successfully reset dataset with {count} default sample records.")
                else:
                    tracker.storage_filepath = target_path
                    count = tracker.load_from_csv()
                    print(f"✅ Successfully loaded {count} expense records from '{target_path}'.")
                print(f"   Active storage is now set to: {tracker.storage_filepath}")
            except Exception as err:
                print(f"❌ Failed to load dataset from '{target_path}': {err}")
        else:
            print("Operation cancelled.")
    else:
        print(f"\n⚠️  Dataset file '{target_path}' does not exist.")
        create_confirm = input(f"Would you like to create and initialize a new empty dataset at '{target_path}'? (y/N): ").strip().lower()
        if create_confirm == "y":
            try:
                os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
                with open(target_path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(tracker.CSV_HEADERS)
                tracker.storage_filepath = target_path
                tracker.load_from_csv()
                print(f"✅ Successfully initialized empty dataset at '{target_path}'.")
                print(f"   Active storage is now set to: {tracker.storage_filepath}")
            except Exception as err:
                print(f"❌ Failed to create dataset: {err}")
        else:
            print("Operation cancelled.")


def main():
    # Ensure sample data is initialized if primary CSV is not present
    if not os.path.exists(CSV_FILEPATH) and os.path.exists(SAMPLE_FILEPATH):
        shutil.copy(SAMPLE_FILEPATH, CSV_FILEPATH)

    tracker = ExpenseTracker(storage_filepath=CSV_FILEPATH)
    print_banner()
    print(f"System ready! Current database has {len(tracker.get_all_expenses())} expense records.")

    # Main Application Loop
    while True:
        display_menu()
        choice = input("Enter option [0-7]: ").strip()

        if choice == "1":
            handle_add_expense(tracker)
        elif choice == "2":
            handle_view_all(tracker)
        elif choice == "3":
            handle_filter_expenses(tracker)
        elif choice == "4":
            handle_sort_expenses(tracker)
        elif choice == "5":
            handle_delete_expense(tracker)
        elif choice == "6":
            handle_load_dataset(tracker)
        elif choice == "7":
            handle_visualizations(tracker)
        elif choice == "0":
            print("\n👋 Thank you for using Personal Expense Tracker & Analysis System. Goodbye!\n")
            break
        else:
            print("❌ Invalid selection. Please enter a number between 0 and 7.")


if __name__ == "__main__":
    main()
