"""External Service Ports - Abstractions for external integrations."""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from src.domain.value_objects import ComplianceScore, KYCData
from src.domain.entities import Transaction


class KYCService(ABC):
    """Port for Know Your Customer verification."""

    @abstractmethod
    def verify(self, kyc_data: KYCData) -> ComplianceScore:
        """Verify customer KYC data and return compliance score."""
        pass

    @abstractmethod
    def check_pep(self, first_name: str, last_name: str) -> bool:
        """Check if person is politically exposed."""
        pass


class AMLService(ABC):
    """Port for Anti-Money Laundering checks."""

    @abstractmethod
    def screen_transaction(self, transaction: Transaction) -> tuple[bool, Optional[str]]:
        """Screen transaction for AML risk. Returns (is_compliant, reason)."""
        pass

    @abstractmethod
    def check_sanctioned_list(self, entity_name: str) -> bool:
        """Check if entity is on OFAC sanctioned list."""
        pass


class FraudDetectionService(ABC):
    """Port for Fraud Detection."""

    @abstractmethod
    def analyze_transaction(self, transaction: Transaction) -> tuple[bool, Optional[str]]:
        """Analyze transaction for fraud. Returns (is_legitimate, fraud_reason)."""
        pass


class EventPublisher(ABC):
    """Port for publishing domain events."""

    @abstractmethod
    def publish(self, event: object) -> None:
        """Publish domain event."""
        pass


class AuditLogger(ABC):
    """Port for immutable audit logging."""

    @abstractmethod
    def log(self, entity_id: UUID, action: str, details: dict) -> None:
        """Log compliance action."""
        pass
