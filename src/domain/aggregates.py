"""Domain Aggregates - Consistency boundaries."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.domain.entities import Customer, Transaction
from src.domain.value_objects import (
    Amount,
    ComplianceScore,
    ComplianceStatus,
    RiskLevel,
    TransactionStatus,
)
from src.domain.domain_events import (
    DomainEvent,
    CustomerVerified,
    TransactionFlagged,
    ComplianceAlertRaised,
)


@dataclass
class CustomerAggregate:
    """Customer Aggregate Root - ensures consistency."""
    
    customer: Customer = field()
    version: int = field(default=1)
    events: list[DomainEvent] = field(default_factory=list)

    def verify_customer(self, compliance_score: ComplianceScore) -> None:
        """Verify customer through KYC."""
        self.customer.verify_kyc(compliance_score)
        
        # Record event
        event = CustomerVerified(
            customer_id=self.customer.customer_id,
            compliance_status=self.customer.compliance_status,
            risk_level=compliance_score.level,
            timestamp=datetime.now()
        )
        self.events.append(event)
        self.version += 1

    def flag_for_review(self, reason: str) -> None:
        """Flag customer for compliance review."""
        self.customer.flag_for_review(reason)
        
        event = ComplianceAlertRaised(
            entity_id=self.customer.customer_id,
            entity_type="customer",
            alert_type="kyc_review",
            description=reason,
            timestamp=datetime.now()
        )
        self.events.append(event)
        self.version += 1

    def get_uncommitted_events(self) -> list[DomainEvent]:
        """Retrieve events that haven't been persisted yet."""
        return self.events.copy()

    def clear_events(self) -> None:
        """Clear events after they've been published."""
        self.events.clear()


@dataclass
class TransactionAggregate:
    """Transaction Aggregate Root - ensures consistency."""
    
    transaction: Transaction = field()
    version: int = field(default=1)
    events: list[DomainEvent] = field(default_factory=list)

    def approve_transaction(self) -> None:
        """Approve transaction after compliance checks."""
        self.transaction.approve()
        self.version += 1

    def flag_transaction(self, reason: str) -> None:
        """Flag transaction for AML/Fraud review."""
        self.transaction.flag(reason)
        
        event = TransactionFlagged(
            transaction_id=self.transaction.transaction_id,
            customer_id=self.transaction.customer_id,
            amount=self.transaction.amount,
            flag_reason=reason,
            timestamp=datetime.now()
        )
        self.events.append(event)
        self.version += 1

    def reject_transaction(self, reason: str) -> None:
        """Reject transaction and raise alert."""
        self.transaction.reject(reason)
        
        event = ComplianceAlertRaised(
            entity_id=self.transaction.transaction_id,
            entity_type="transaction",
            alert_type="aml_rejection",
            description=reason,
            timestamp=datetime.now()
        )
        self.events.append(event)
        self.version += 1

    def get_uncommitted_events(self) -> list[DomainEvent]:
        return self.events.copy()

    def clear_events(self) -> None:
        self.events.clear()
