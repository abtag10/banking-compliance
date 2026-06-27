"""Domain Events - Immutable records of what happened."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional

from src.domain.value_objects import Amount, RiskLevel


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""
    timestamp: datetime


@dataclass(frozen=True)
class CustomerVerified(DomainEvent):
    """Event: Customer successfully verified through KYC."""
    customer_id: UUID
    compliance_status: str
    risk_level: RiskLevel


@dataclass(frozen=True)
class CustomerFlagged(DomainEvent):
    """Event: Customer flagged for compliance review."""
    customer_id: UUID
    reason: str


@dataclass(frozen=True)
class TransactionFlagged(DomainEvent):
    """Event: Transaction flagged for AML/Fraud review."""
    transaction_id: UUID
    customer_id: UUID
    amount: Amount
    flag_reason: str


@dataclass(frozen=True)
class ComplianceAlertRaised(DomainEvent):
    """Event: Compliance alert raised for review."""
    entity_id: UUID
    entity_type: str  # "customer" or "transaction"
    alert_type: str  # "kyc_review", "aml_alert", etc.
    description: str


@dataclass(frozen=True)
class ComplianceReportGenerated(DomainEvent):
    """Event: Compliance report generated."""
    report_id: UUID
    report_type: str  # "aml", "kyc", "transaction_monitoring", etc.
    period_start: datetime
    period_end: datetime
    record_count: int
