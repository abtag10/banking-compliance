"""Data Transfer Objects - Request/Response models."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional


@dataclass
class KYCDataDTO:
    """DTO for KYC data."""
    first_name: str
    last_name: str
    date_of_birth: str
    nationality: str
    email: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class CustomerDTO:
    """DTO for Customer response."""
    customer_id: UUID
    first_name: str
    last_name: str
    compliance_status: str
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    is_pep: bool = False
    created_at: datetime = None


@dataclass
class TransactionDTO:
    """DTO for Transaction response."""
    transaction_id: UUID
    customer_id: UUID
    amount: Decimal
    currency: str
    transaction_type: str
    compliance_status: str
    description: Optional[str] = None
    flags: list[str] = None
    created_at: datetime = None


@dataclass
class ComplianceReportDTO:
    """DTO for compliance report."""
    report_id: UUID
    report_type: str
    period_start: datetime
    period_end: datetime
    total_records: int
    flagged_count: int
    approved_count: int
    generated_at: datetime
