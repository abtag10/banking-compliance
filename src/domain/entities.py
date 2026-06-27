"""Domain Entities - Objects with identity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.domain.value_objects import (
    Amount,
    ComplianceScore,
    ComplianceStatus,
    KYCData,
    RiskLevel,
    TransactionStatus,
    TransactionType,
)


@dataclass
class Customer:
    """Customer Entity - has identity (customer_id)."""
    
    customer_id: UUID = field(default_factory=uuid4)
    kyc_data: KYCData = field()
    compliance_status: ComplianceStatus = ComplianceStatus.PENDING
    compliance_score: Optional[ComplianceScore] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    email: Optional[str] = None
    phone: Optional[str] = None

    def verify_kyc(self, score: ComplianceScore) -> None:
        """Mark customer as verified after KYC check."""
        if score.level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            self.compliance_status = ComplianceStatus.FLAGGED
        else:
            self.compliance_status = ComplianceStatus.VERIFIED
        
        self.compliance_score = score
        self.updated_at = datetime.now()

    def flag_for_review(self, reason: str) -> None:
        """Flag customer for manual review."""
        self.compliance_status = ComplianceStatus.FLAGGED
        self.updated_at = datetime.now()

    def suspend(self) -> None:
        """Suspend customer account."""
        self.compliance_status = ComplianceStatus.SUSPENDED
        self.updated_at = datetime.now()

    def is_compliant(self) -> bool:
        return self.compliance_status == ComplianceStatus.VERIFIED


@dataclass
class Transaction:
    """Transaction Entity - has identity (transaction_id)."""
    
    transaction_id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field()
    amount: Amount = field()
    transaction_type: TransactionType = field()
    compliance_status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None
    recipient_info: Optional[str] = None
    flags: list[str] = field(default_factory=list)  # AML flags, fraud flags, etc.

    def approve(self) -> None:
        """Approve transaction after compliance checks."""
        self.compliance_status = TransactionStatus.APPROVED
        self.updated_at = datetime.now()

    def flag(self, reason: str) -> None:
        """Flag transaction for review."""
        self.compliance_status = TransactionStatus.FLAGGED
        self.flags.append(reason)
        self.updated_at = datetime.now()

    def reject(self, reason: str) -> None:
        """Reject transaction."""
        self.compliance_status = TransactionStatus.REJECTED
        self.flags.append(reason)
        self.updated_at = datetime.now()

    def is_approved(self) -> bool:
        return self.compliance_status == TransactionStatus.APPROVED
