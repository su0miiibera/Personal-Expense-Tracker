"""
Expense Data Models & Custom Exceptions
Demonstrating:
- Classes and Objects (OOP, encapsulation, properties, dunder methods)
- Custom Exception Handling Hierarchy
- Conditions & Input Validation
- Collections (Sets, Tuples, Dictionaries)
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Set


# ==========================================
# Custom Exception Hierarchy
# ==========================================

class ExpenseTrackerError(Exception):
    """Base exception for all expense tracker errors."""
    pass


class ExpenseValidationError(ExpenseTrackerError):
    """Raised when an expense field fails validation."""
    pass


class InvalidAmountError(ExpenseValidationError):
    """Raised when an entered expense amount is non-positive or invalid."""
    def __init__(self, amount: Any, message: str = "Expense amount must be a positive number."):
        self.amount = amount
        super().__init__(f"{message} Received: {amount!r}")


class InvalidDateError(ExpenseValidationError):
    """Raised when an entered date does not adhere to YYYY-MM-DD or is in the future."""
    def __init__(self, date_str: str, message: str = "Invalid date format. Expected 'YYYY-MM-DD'."):
        self.date_str = date_str
        super().__init__(f"{message} Received: {date_str!r}")


class InvalidCategoryError(ExpenseValidationError):
    """Raised when an entered category is empty or invalid."""
    def __init__(self, category: str, message: str = "Category cannot be empty."):
        self.category = category
        super().__init__(f"{message} Received: {category!r}")


# ==========================================
# Standard Categories (Collection: Set / Tuple)
# ==========================================

# Using a tuple for ordered display and a set for O(1) membership testing
DEFAULT_CATEGORIES_TUPLE: tuple = (
    "Food",
    "Travel",
    "Education",
    "Shopping",
    "Entertainment",
    "Utilities",
    "Healthcare",
    "Miscellaneous",
)

DEFAULT_CATEGORIES_SET: Set[str] = set(DEFAULT_CATEGORIES_TUPLE)


# ==========================================
# Expense Class (OOP)
# ==========================================

class Expense:
    """
    Represents an individual expense record.

    Attributes:
        date (str): Expense date formatted as 'YYYY-MM-DD'.
        category (str): Standardized category name.
        amount (float): Monetary value greater than 0.
        description (str): Optional context or note.
        expense_id (int, optional): Unique numeric identifier.
    """

    def __init__(
        self,
        date: str,
        category: str,
        amount: float,
        description: str = "",
        expense_id: Optional[int] = None,
    ):
        self.expense_id = expense_id
        # Use setters/validation methods to enforce integrity
        self._date = self._validate_and_normalize_date(date)
        self._category = self._validate_and_normalize_category(category)
        self._amount = self._validate_and_normalize_amount(amount)
        self._description = str(description).strip() if description else "N/A"

    # Properties for Encapsulation
    @property
    def date(self) -> str:
        """Returns the formatted date string."""
        return self._date

    @property
    def category(self) -> str:
        """Returns the normalized category string."""
        return self._category

    @property
    def amount(self) -> float:
        """Returns the expense amount as a float."""
        return self._amount

    @property
    def description(self) -> str:
        """Returns the description."""
        return self._description

    # Validation Methods demonstrating conditions & exception handling
    @staticmethod
    def _validate_and_normalize_date(date_str: str) -> str:
        """
        Validates date format (YYYY-MM-DD) and checks future date constraints.
        Demonstrates: Conditions, Date Parsing, Exception Handling.
        """
        if not isinstance(date_str, str):
            raise InvalidDateError(str(date_str), "Date must be a string in YYYY-MM-DD format.")

        cleaned = date_str.strip()
        try:
            parsed_date = datetime.strptime(cleaned, "%Y-%m-%d").date()
        except ValueError:
            raise InvalidDateError(cleaned, "Date must match format YYYY-MM-DD (e.g., 2026-05-15).")

        # Condition check: expense should not be unnaturally far into future
        today = datetime.now().date()
        if parsed_date > today:
            raise InvalidDateError(cleaned, f"Expense date cannot be in the future (today is {today}).")

        return parsed_date.strftime("%Y-%m-%d")

    @staticmethod
    def _validate_and_normalize_category(category_str: str) -> str:
        """
        Validates and title-cases category names.
        Demonstrates: String manipulation and conditions.
        """
        if not category_str or not isinstance(category_str, str):
            raise InvalidCategoryError(str(category_str), "Category must be a non-empty string.")

        cleaned = category_str.strip().title()
        if len(cleaned) == 0:
            raise InvalidCategoryError(category_str, "Category name cannot be blank.")

        return cleaned

    @staticmethod
    def _validate_and_normalize_amount(amount_val: Any) -> float:
        """
        Validates that amount is positive numeric.
        Demonstrates: Type conversion, conditions, and custom exceptions.
        """
        try:
            numeric_amount = float(amount_val)
        except (ValueError, TypeError):
            raise InvalidAmountError(amount_val, "Expense amount must be a valid numeric value.")

        # Condition check
        if numeric_amount <= 0:
            raise InvalidAmountError(numeric_amount, "Expense amount must be strictly greater than 0.")

        # Round to 2 decimal places for financial accuracy
        return round(numeric_amount, 2)

    # Conversion & Serialization Methods
    def to_dict(self) -> Dict[str, Any]:
        """Converts the expense to a Python dictionary (Collection: Dict)."""
        return {
            "id": self.expense_id,
            "date": self.date,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
        }

    def to_csv_row(self) -> List[str]:
        """Converts the expense to a list of strings for CSV export (Collection: List)."""
        return [
            str(self.expense_id if self.expense_id is not None else ""),
            self.date,
            self.category,
            f"{self.amount:.2f}",
            self.description,
        ]

    def to_tuple(self) -> tuple:
        """Returns key elements as a tuple (Collection: Tuple)."""
        return (self.date, self.category, self.amount, self.description)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expense":
        """Instantiates an Expense object from a dictionary."""
        return cls(
            date=data.get("date", ""),
            category=data.get("category", ""),
            amount=data.get("amount", 0.0),
            description=data.get("description", ""),
            expense_id=data.get("id"),
        )

    @classmethod
    def from_csv_row(cls, row: List[str]) -> "Expense":
        """Instantiates an Expense object from a CSV row list."""
        if len(row) < 4:
            raise ExpenseValidationError(f"CSV row has insufficient columns: {row}")

        # Check if first column is ID or Date
        if len(row) >= 5:
            expense_id = int(row[0]) if row[0].strip().isdigit() else None
            return cls(
                date=row[1],
                category=row[2],
                amount=row[3],
                description=row[4],
                expense_id=expense_id,
            )
        else:
            return cls(
                date=row[0],
                category=row[1],
                amount=row[2],
                description=row[3] if len(row) > 3 else "",
            )

    # Magic / Dunder Methods for Pythonic behavior
    def __repr__(self) -> str:
        return f"Expense(id={self.expense_id}, date='{self.date}', category='{self.category}', amount={self.amount:.2f})"

    def __str__(self) -> str:
        return f"[{self.date}] {self.category:<14} | ₹{self.amount:>8.2f} | {self.description}"

    def __eq__(self, other: object) -> bool:
        """Equality comparison between expenses."""
        if not isinstance(other, Expense):
            return False
        return (
            self.date == other.date
            and self.category == other.category
            and self.amount == other.amount
            and self.description == other.description
        )

    def __lt__(self, other: "Expense") -> bool:
        """Less-than comparison (defaults to sorting by date then amount)."""
        if not isinstance(other, Expense):
            return NotImplemented
        if self.date == other.date:
            return self.amount < other.amount
        return self.date < other.date
