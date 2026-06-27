"""Dependency Injection Container."""

from injector import Module, provider, Injector

from src.domain.ports.repositories import CustomerRepository, TransactionRepository
from src.domain.ports.external_services import (
    KYCService,
    AMLService,
    FraudDetectionService,
    EventPublisher,
    AuditLogger,
)
from src.domain.services.compliance_service import ComplianceService

from src.adapters.outbound.in_memory_repository import (
    InMemoryCustomerRepository,
    InMemoryTransactionRepository,
)
from src.adapters.outbound.mock_services import (
    MockKYCService,
    MockAMLService,
    MockFraudDetectionService,
    MockEventPublisher,
    MockAuditLogger,
)

from src.application.use_cases.create_customer import CreateCustomerUseCase
from src.application.use_cases.verify_customer import VerifyCustomerUseCase
from src.application.use_cases.monitor_transaction import MonitorTransactionUseCase

from src.adapters.inbound.http_adapter import HTTPAdapter


class ApplicationModule(Module):
    """Dependency injection module."""

    @provider
    def customer_repository(self) -> CustomerRepository:
        return InMemoryCustomerRepository()

    @provider
    def transaction_repository(self) -> TransactionRepository:
        return InMemoryTransactionRepository()

    @provider
    def kyc_service(self) -> KYCService:
        return MockKYCService()

    @provider
    def aml_service(self) -> AMLService:
        return MockAMLService()

    @provider
    def fraud_detection_service(self) -> FraudDetectionService:
        return MockFraudDetectionService()

    @provider
    def event_publisher(self) -> EventPublisher:
        return MockEventPublisher()

    @provider
    def audit_logger(self) -> AuditLogger:
        return MockAuditLogger()

    @provider
    def compliance_service(self, customer_repo, aml_service, fraud_service) -> ComplianceService:
        return ComplianceService(customer_repo, aml_service, fraud_service)

    @provider
    def create_customer_use_case(
        self,
        customer_repo,
        audit_logger,
    ) -> CreateCustomerUseCase:
        return CreateCustomerUseCase(customer_repo, audit_logger)

    @provider
    def verify_customer_use_case(
        self,
        customer_repo,
        kyc_service,
        audit_logger,
    ) -> VerifyCustomerUseCase:
        return VerifyCustomerUseCase(customer_repo, kyc_service, audit_logger)

    @provider
    def monitor_transaction_use_case(
        self,
        transaction_repo,
        compliance_service,
        event_publisher,
        audit_logger,
    ) -> MonitorTransactionUseCase:
        return MonitorTransactionUseCase(
            transaction_repo,
            compliance_service,
            event_publisher,
            audit_logger,
        )

    @provider
    def http_adapter(
        self,
        create_customer_uc,
        verify_customer_uc,
        monitor_transaction_uc,
        transaction_repo,
    ) -> HTTPAdapter:
        return HTTPAdapter(
            create_customer_uc,
            verify_customer_uc,
            monitor_transaction_uc,
            transaction_repo,
        )


def create_injector() -> Injector:
    """Create dependency injector."""
    return Injector([ApplicationModule])
