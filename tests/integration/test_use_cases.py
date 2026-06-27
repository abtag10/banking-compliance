"""Integration tests for use cases."""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.value_objects import (
    Amount,
    KYCData,
    RiskLevel,
    TransactionType,
)
from src.domain.entities import Customer, Transaction
from src.domain.aggregates import CustomerAggregate, TransactionAggregate
from src.application.dtos import KYCDataDTO
from src.application.use_cases.create_customer import CreateCustomerUseCase
from src.application.use_cases.verify_customer import VerifyCustomerUseCase
from src.application.use_cases.monitor_transaction import MonitorTransactionUseCase

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
from src.domain.services.compliance_service import ComplianceService


@pytest.fixture
def repositories():
    return (
        InMemoryCustomerRepository(),
        InMemoryTransactionRepository(),
    )


@pytest.fixture
def services():
    return (
        MockKYCService(),
        MockAMLService(),
        MockFraudDetectionService(),
        MockEventPublisher(),
        MockAuditLogger(),
    )


class TestCreateCustomerUseCase:
    """Integration tests for CreateCustomer use case."""

    def test_create_customer_successfully(self, repositories, services):
        customer_repo, _ = repositories
        _, _, _, _, audit_logger = services

        uc = CreateCustomerUseCase(customer_repo, audit_logger)

        kyc_dto = KYCDataDTO(
            first_name="Carlos",
            last_name="Garcia",
            date_of_birth="1991-09-25",
            nationality="ES",
            email="carlos@example.com",
        )

        result = uc.execute(kyc_dto)

        assert result.first_name == "Carlos"
        assert result.email == "carlos@example.com"
        assert result.compliance_status == "pending"


class TestVerifyCustomerUseCase:
    """Integration tests for VerifyCustomer use case."""

    def test_verify_customer_successfully(self, repositories, services):
        customer_repo, _ = repositories
        kyc_service, _, _, _, audit_logger = services

        # First create a customer
        kyc = KYCData(
            first_name="Maria",
            last_name="Rodriguez",
            date_of_birth="1989-04-12",
            nationality="CO",
        )
        customer = Customer(kyc_data=kyc, email="maria@example.com")
        agg = CustomerAggregate(customer=customer)
        customer_repo.save(agg)

        # Now verify
        uc = VerifyCustomerUseCase(customer_repo, kyc_service, audit_logger)
        result = uc.execute(customer.customer_id)

        assert result.compliance_status == "verified"
        assert result.risk_score is not None


class TestMonitorTransactionUseCase:
    """Integration tests for MonitorTransaction use case."""

    def test_monitor_small_transaction_from_compliant_customer(self, repositories, services):
        customer_repo, transaction_repo = repositories
        kyc_service, aml_service, fraud_service, event_publisher, audit_logger = services

        # Create and verify customer first
        kyc = KYCData(
            first_name="Pierre",
            last_name="Dupont",
            date_of_birth="1993-11-30",
            nationality="FR",
        )
        customer = Customer(kyc_data=kyc, email="pierre@example.com")
        agg = CustomerAggregate(customer=customer)
        customer_repo.save(agg)

        # Verify customer
        verify_uc = VerifyCustomerUseCase(customer_repo, kyc_service, audit_logger)
        verify_uc.execute(customer.customer_id)

        # Create transaction
        tx = Transaction(
            customer_id=customer.customer_id,
            amount=Amount(Decimal("1000"), "EUR"),
            transaction_type=TransactionType.TRANSFER,
            description="Regular transfer",
        )
        tx_agg = TransactionAggregate(transaction=tx)
        transaction_repo.save(tx_agg)

        # Monitor transaction
        compliance_service = ComplianceService(
            customer_repo,
            aml_service,
            fraud_service,
        )
        uc = MonitorTransactionUseCase(
            transaction_repo,
            compliance_service,
            event_publisher,
            audit_logger,
        )
        result = uc.execute(tx.transaction_id)

        assert result.compliance_status == "approved"
        assert len(result.flags) == 0

    def test_monitor_large_transaction_is_flagged(self, repositories, services):
        customer_repo, transaction_repo = repositories
        kyc_service, aml_service, fraud_service, event_publisher, audit_logger = services

        # Create compliant customer
        kyc = KYCData(
            first_name="Sophie",
            last_name="Martin",
            date_of_birth="1987-06-08",
            nationality="FR",
        )
        customer = Customer(kyc_data=kyc)
        agg = CustomerAggregate(customer=customer)
        customer_repo.save(agg)
        verify_uc = VerifyCustomerUseCase(customer_repo, kyc_service, audit_logger)
        verify_uc.execute(customer.customer_id)

        # Create large transaction
        tx = Transaction(
            customer_id=customer.customer_id,
            amount=Amount(Decimal("100000"), "EUR"),
            transaction_type=TransactionType.TRANSFER,
        )
        tx_agg = TransactionAggregate(transaction=tx)
        transaction_repo.save(tx_agg)

        # Monitor
        compliance_service = ComplianceService(
            customer_repo,
            aml_service,
            fraud_service,
        )
        uc = MonitorTransactionUseCase(
            transaction_repo,
            compliance_service,
            event_publisher,
            audit_logger,
        )
        result = uc.execute(tx.transaction_id)

        assert result.compliance_status == "flagged"
        assert len(result.flags) > 0
