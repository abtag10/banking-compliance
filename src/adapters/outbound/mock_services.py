"""Mock External Services - For testing/development."""

from uuid import UUID
from typing import Optional
from datetime import datetime
from decimal import Decimal

from src.domain.value_objects import ComplianceScore, RiskLevel, KYCData
from src.domain.entities import Transaction
from src.domain.ports.external_services import (
    KYCService,
    AMLService,
    FraudDetectionService,
    EventPublisher,
    AuditLogger,
)


class MockKYCService(KYCService):
    """Mock KYC service for development."""

    def verify(self, kyc_data: KYCData) -> ComplianceScore:
        # Simple scoring logic
        score = 50.0
        
        # Lower risk for non-PEP
        if not kyc_data.is_pep:
            score = 25.0
        else:
            score = 75.0
        
        return ComplianceScore(
            score=score,
            level=RiskLevel.LOW if score < 50 else RiskLevel.MEDIUM,
            calculation_date=datetime.now(),
            reason="Mock KYC verification",
        )

    def check_pep(self, first_name: str, last_name: str) -> bool:
        # Dummy PEP check
        pep_list = ["Vladimir Putin", "Donald Trump"]
        full_name = f"{first_name} {last_name}"
        return full_name in pep_list


class MockAMLService(AMLService):
    """Mock AML service for development."""

    def screen_transaction(self, transaction: Transaction) -> tuple[bool, Optional[str]]:
        # Flag large transactions
        if transaction.amount.value > Decimal("50000"):
            return False, "Amount exceeds AML threshold"
        return True, None

    def check_sanctioned_list(self, entity_name: str) -> bool:
        return False


class MockFraudDetectionService(FraudDetectionService):
    """Mock fraud detection service for development."""

    def analyze_transaction(self, transaction: Transaction) -> tuple[bool, Optional[str]]:
        # Simple heuristic
        if transaction.amount.value > Decimal("100000"):
            return False, "Unusually high amount"
        return True, None


class MockEventPublisher(EventPublisher):
    """Mock event publisher for development."""

    def __init__(self):
        self.events = []

    def publish(self, event: object) -> None:
        self.events.append(event)
        print(f"[Event Published] {event}")


class MockAuditLogger(AuditLogger):
    """Mock audit logger for development."""

    def __init__(self):
        self.logs = []

    def log(self, entity_id: UUID, action: str, details: dict) -> None:
        log_entry = {
            "entity_id": str(entity_id),
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
        self.logs.append(log_entry)
        print(f"[Audit Log] {action} on {entity_id}")
