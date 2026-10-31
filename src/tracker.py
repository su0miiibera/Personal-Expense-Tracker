"""
Expense Tracker Core Manager
Demonstrating:
- OOP (ExpenseTracker class managing collections)
- Collections (Lists, Dictionaries, Sets, Tuples)
- Loops (for loops, while loops, comprehensions)
- Conditions (filtering, existence checks, validation)
- Built-in Sorting (Python Timsort with custom key functions)
- Robust File Handling (Reading/Writing CSV & JSON with Context Managers)
- Exception Handling (try-except-finally blocks)
"""

import os
import csv
import json
from typing import List, Dict, Optional, Tuple, Set, Any
from src.models import (
    Expense,
    ExpenseTrackerError,
    ExpenseValidationError,
    DEFAULT_CATEGORIES_TUPLE,
)


class ExpenseTracker:
    """
    Manages in-memory expense records and coordinates file persistence.
    """

    CSV_HEADERS: List[str] = ["ID", "Date", "Category", "Amount", "Description"]

    def __init__(self, storage_filepath: str = "data/expenses.csv"):
        self.storage_filepath = storage_filepath
        self._expenses: List[Expense] = []  # Collection: List of Expense objects
        self._next_id: int = 1
        
        # Ensure data folder exists
        os.makedirs(os.path.dirname(self.storage_filepath) or ".", exist_ok=True)
        
        # Automatically attempt loading existing data
        if os.path.exists(self.storage_filepath):
            self.load_from_csv()

    # ==========================================
    # CRUD Operations
    # ==========================================

    def add_expense(
        self,
        date: str,
        category: str,
        amount: float,
        description: str = "",
        auto_save: bool = True,
    ) -> Expense:
        """
        Adds a new expense to the collection.
        Demonstrates: Object creation, List append, condition checks.
        """
        expense = Expense(
            date=date,
            category=category,
            amount=amount,
            description=description,
            expense_id=self._next_id,
        )
        self._expenses.append(expense)
        self._next_id += 1

        if auto_save:
            self.save_to_csv()

        return expense

    def get_all_expenses(self) -> List[Expense]:
        """Returns a shallow copy of all recorded expenses (Collection: List)."""
        return list(self._expenses)

    def get_expense_by_id(self, expense_id: int) -> Optional[Expense]:
        """
        Finds an expense by its unique ID.
        Demonstrates: Loop and Condition.
        """
        for expense in self._expenses:
            if expense.expense_id == expense_id:
                return expense
        return None

    def delete_expense(self, expense_id: int, auto_save: bool = True) -> bool:
        """
        Deletes an expense by its ID.
        Demonstrates: While loop / index lookup and condition.
        """
        index_to_remove = -1
        i = 0
        while i < len(self._expenses):
            if self._expenses[i].expense_id == expense_id:
                index_to_remove = i
                break
            i += 1

        if index_to_remove != -1:
            removed = self._expenses.pop(index_to_remove)
            if auto_save:
                self.save_to_csv()
            return True
        return False

    def clear_all(self, auto_save: bool = True) -> None:
        """Clears all expenses from memory and storage."""
        self._expenses.clear()
        self._next_id = 1
        if auto_save:
            self.save_to_csv()

    # ==========================================
    # Calculations & Aggregations
    # ==========================================

    def calculate_total_expenditure(self, expenses: Optional[List[Expense]] = None) -> float:
        """
        Calculates total money spent.
        Demonstrates: Loops, Accumulation pattern, Float rounding.
        """
        dataset = self._expenses if expenses is None else expenses
        total = 0.0
        for exp in dataset:
            total += exp.amount
        return round(total, 2)

    def calculate_average_expenditure(self, expenses: Optional[List[Expense]] = None) -> float:
        """
        Calculates the mean expenditure per transaction.
        Demonstrates: Conditions (zero check) and arithmetic.
        """
        dataset = self._expenses if expenses is None else expenses
        if not dataset:
            return 0.0
        return round(self.calculate_total_expenditure(dataset) / len(dataset), 2)

    def calculate_category_wise_expenditure(
        self, expenses: Optional[List[Expense]] = None
    ) -> Dict[str, float]:
        """
        Aggregates spending categorized by category.
        Demonstrates: Dictionary collection, for loop, dictionary membership condition.
        """
        dataset = self._expenses if expenses is None else expenses
        category_totals: Dict[str, float] = {}

        for exp in dataset:
            cat = exp.category
            if cat in category_totals:
                category_totals[cat] += exp.amount
            else:
                category_totals[cat] = exp.amount

        # Round all values to 2 decimal places
        for cat in category_totals:
            category_totals[cat] = round(category_totals[cat], 2)

        return category_totals

    def calculate_monthly_expenditure(
        self, expenses: Optional[List[Expense]] = None
    ) -> Dict[str, float]:
        """
        Aggregates spending categorized by Month (YYYY-MM).
        Demonstrates: String slicing, dictionary aggregation.
        """
        dataset = self._expenses if expenses is None else expenses
        monthly_totals: Dict[str, float] = {}

        for exp in dataset:
            month_key = exp.date[:7]  # Extracts 'YYYY-MM'
            monthly_totals[month_key] = monthly_totals.get(month_key, 0.0) + exp.amount

        # Sort months chronologically
        sorted_months = dict(sorted(monthly_totals.items()))
        return {m: round(amt, 2) for m, amt in sorted_months.items()}

    def get_highest_and_lowest_expenses(
        self, expenses: Optional[List[Expense]] = None
    ) -> Tuple[Optional[Expense], Optional[Expense]]:
        """
        Identifies the single highest and lowest expense entries.
        Demonstrates: Tuple collection return, conditions, min/max tracking.
        """
        dataset = self._expenses if expenses is None else expenses
        if not dataset:
            return (None, None)

        highest = dataset[0]
        lowest = dataset[0]

        for exp in dataset[1:]:
            if exp.amount > highest.amount:
                highest = exp
            if exp.amount < lowest.amount:
                lowest = exp

        return (highest, lowest)

    def get_unique_categories(self) -> Set[str]:
        """
        Returns all unique categories present in the tracker.
        Demonstrates: Set collection and set comprehension.
        """
        return {exp.category for exp in self._expenses}

    # ==========================================
    # Filtering
    # ==========================================

    def filter_expenses(
        self,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
    ) -> List[Expense]:
        """
        Filters expenses by multiple optional criteria.
        Demonstrates: Compound boolean conditions, list comprehension.
        """
        filtered = []
        for exp in self._expenses:
            # Condition 1: Category filter
            if category and exp.category.lower() != category.strip().lower():
                continue

            # Condition 2: Date range filter
            if start_date and exp.date < start_date:
                continue
            if end_date and exp.date > end_date:
                continue

            # Condition 3: Amount range filter
            if min_amount is not None and exp.amount < min_amount:
                continue
            if max_amount is not None and exp.amount > max_amount:
                continue

            filtered.append(exp)

        return filtered

    # ==========================================
    # ==========================================
    # Sorting (Python Built-in)
    # ==========================================

    def sort_expenses(
        self,
        by: str = "date",
        ascending: bool = True,
    ) -> List[Expense]:
        """
        Sorts expenses by 'date', 'amount', 'category', or 'id'.
        Demonstrates built-in sorting (Python Timsort) with custom key functions.
        """
        # Valid sort keys
        valid_keys = {"date", "amount", "category", "id"}
        sort_by = by.lower()
        if sort_by not in valid_keys:
            sort_by = "date"

        # Make a copy of the list so we don't unexpectedly mutate original order unless desired
        copied_list = list(self._expenses)

        # Python built-in Timsort (list.sort() / sorted())
        def sort_key(item: Expense):
            if sort_by == "amount":
                return item.amount
            elif sort_by == "category":
                return item.category.lower()
            elif sort_by == "id":
                return item.expense_id or 0
            return item.date

        copied_list.sort(key=sort_key, reverse=not ascending)
        return copied_list

    # ==========================================
    # File Handling (CSV & JSON Persistence)
    # ==========================================

    def save_to_csv(self, filepath: Optional[str] = None) -> bool:
        """
        Saves expense records to a CSV file.
        Demonstrates: File handling, context manager (with open), CSV writer.
        """
        target_path = filepath or self.storage_filepath
        try:
            os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
            with open(target_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(self.CSV_HEADERS)
                for expense in self._expenses:
                    writer.writerow(expense.to_csv_row())
            return True
        except IOError as e:
            raise ExpenseTrackerError(f"Failed to write CSV file: {e}")

    def load_from_csv(self, filepath: Optional[str] = None) -> int:
        """
        Loads expense records from a CSV file.
        Demonstrates: File handling, try-except-finally, CSV reader, Exception handling.
        """
        target_path = filepath or self.storage_filepath
        if not os.path.exists(target_path):
            return 0

        loaded_expenses: List[Expense] = []
        max_id = 0

        file_handle = None
        try:
            file_handle = open(target_path, mode="r", newline="", encoding="utf-8")
            reader = csv.reader(file_handle)
            
            # Read and skip header line if present
            header = next(reader, None)
            
            line_num = 1
            for row in reader:
                line_num += 1
                if not row or not any(row):  # Skip blank lines
                    continue
                try:
                    exp = Expense.from_csv_row(row)
                    if exp.expense_id is not None and exp.expense_id > max_id:
                        max_id = exp.expense_id
                    loaded_expenses.append(exp)
                except ExpenseValidationError as err:
                    print(f"Warning: Skipping corrupted row at line {line_num}: {err}")
                    continue
        except (IOError, csv.Error) as err:
            raise ExpenseTrackerError(f"Error reading CSV file at '{target_path}': {err}")
        finally:
            # Explicit finally block demonstrating file resource safety
            if file_handle is not None and not file_handle.closed:
                file_handle.close()

        self._expenses = loaded_expenses
        self._next_id = max_id + 1 if max_id > 0 else (len(loaded_expenses) + 1)
        return len(self._expenses)

    def export_to_json(self, json_filepath: str) -> bool:
        """
        Exports all expenses to JSON format.
        Demonstrates: JSON serialization, dictionary transformations.
        """
        try:
            os.makedirs(os.path.dirname(json_filepath) or ".", exist_ok=True)
            data = [exp.to_dict() for exp in self._expenses]
            with open(json_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except IOError as e:
            raise ExpenseTrackerError(f"Failed to export JSON file: {e}")

    def import_from_json(self, json_filepath: str) -> int:
        """
        Imports expenses from a JSON file.
        Demonstrates: JSON parsing and validation.
        """
        if not os.path.exists(json_filepath):
            raise ExpenseTrackerError(f"File not found: {json_filepath}")

        try:
            with open(json_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ExpenseValidationError("JSON root must be a list of expense objects.")

            count = 0
            for item in data:
                if isinstance(item, dict):
                    self.add_expense(
                        date=item.get("date", ""),
                        category=item.get("category", ""),
                        amount=item.get("amount", 0.0),
                        description=item.get("description", ""),
                        auto_save=False,
                    )
                    count += 1

            self.save_to_csv()
            return count
        except (IOError, json.JSONDecodeError) as e:
            raise ExpenseTrackerError(f"Failed to import JSON file: {e}")
