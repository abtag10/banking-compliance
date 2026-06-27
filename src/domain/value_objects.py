"""Domain Value Objects - Immutable, no identity."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional
from datetime import datetime


class ComplianceStatus(str, Enum):
    """Customer compliance status."""
    PENDING = "pending"
    VERIFIED = "verified"
    FLAGGED = "flagged"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class RiskLevel(str, Enum):
    """Risk classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TransactionType(str, Enum):
    """Transaction types."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"


class TransactionStatus(str, Enum):
    """Transaction status in compliance."""
    PENDING = "pending"
    APPROVED = "approved"
    FLAGGED = "flagged"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Amount:
    """Immutable Amount value object."""
    value: Decimal
    currency: str = "EUR"

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Amount must be positive")
        if not self.currency:
            raise ValueError("Currency must be specified")

    def __add__(self, other: "Amount") -> "Amount":
        if self.currency != other.currency:
            raise ValueError("Cannot add amounts in different currencies")
        return Amount(self.value + other.value, self.currency)

    def __sub__(self, other: "Amount") -> "Amount":
        if self.currency != other.currency:
            raise ValueError("Cannot subtract amounts in different currencies")
        if self.value < other.value:
            raise ValueError("Insufficient funds")
        return Amount(self.value - other.value, self.currency)

    def is_above(self, threshold: Decimal) -> bool:
        return self.value >= threshold


@dataclass(frozen=True)
class ComplianceScore:
    """Risk score for compliance."""
    score: float  # 0-100
    level: RiskLevel
    calculation_date: datetime
    reason: Optional[str] = None

    def __post_init__(self):
        if not 0 <= self.score <= 100:
            raise ValueError("Score must be between 0 and 100")
        
        # Determine level
        if self.score < 25:
            expected_level = RiskLevel.LOW
        elif self.score < 50:
            expected_level = RiskLevel.MEDIUM
        elif self.score < 75:
            expected_level = RiskLevel.HIGH
        else:
            expected_level = RiskLevel.CRITICAL
        
        if self.level != expected_level:
            object.__setattr__(self, 'level', expected_level)


@dataclass(frozen=True)
class KYCData:
    """Know Your Customer data."""
    first_name: str
    last_name: str
    date_of_birth: str  # ISO format YYYY-MM-DD
    nationality: str
    is_pep: bool = False  # Politically Exposed Person
    pep_reason: Optional[str] = None

    def __post_init__(self):
        if not self.first_name or not self.last_name:
            raise ValueError("First and last name are required")
        if len(self.nationality) != 2:
            raise ValueError("Nationality must be ISO 2-letter code")
