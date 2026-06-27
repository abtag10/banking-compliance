"""Compliance Service - Domain-level compliance rules."""

from decimal import Decimal
from typing import Optional

from src.domain.entities import Customer, Transaction
from src.domain.value_objects import Amount, RiskLevel, TransactionStatus
from src.domain.aggregates import TransactionAggregate, CustomerAggregate
from src.domain.ports.repositories import CustomerRepository
from src.domain.ports.external_services import AMLService, FraudDetectionService


class ComplianceService:
    """Pure business logic for compliance checks."""

    def __init__(
        self,
        customer_repo: CustomerRepository,
        aml_service: AMLService,
        fraud_service: FraudDetectionService,
    ):
        self.customer_repo = customer_repo
        self.aml_service = aml_service
        self.fraud_service = fraud_service

    def check_transaction_compliance(
        self,
        transaction_aggregate: TransactionAggregate,
    ) -> tuple[bool, Optional[str]]:
        """Perform all compliance checks on a transaction."""
        transaction = transaction_aggregate.transaction

        # Check customer compliance
        customer_agg = self.customer_repo.find_by_id(transaction.customer_id)
        if not customer_agg:
            return False, "Customer not found"

        if not customer_agg.customer.is_compliant():
            return False, "Customer is not compliant"

        # Check AML
        is_aml_ok, aml_reason = self.aml_service.screen_transaction(transaction)
        if not is_aml_ok:
            transaction_aggregate.flag_transaction(f"AML Flag: {aml_reason}")
            return False, aml_reason

        # Check Fraud
        is_fraud_ok, fraud_reason = self.fraud_service.analyze_transaction(transaction)
        if not is_fraud_ok:
            transaction_aggregate.flag_transaction(f"Fraud Flag: {fraud_reason}")
            return False, fraud_reason

        # Check transaction amount limits based on risk
        is_amount_ok = self._check_amount_limits(
            transaction.amount,
            customer_agg.customer.compliance_score.level,
        )
        if not is_amount_ok:
            reason = f"Amount {transaction.amount.value} exceeds limit for risk level"
            transaction_aggregate.flag_transaction(reason)
            return False, reason

        return True, None

    def _check_amount_limits(
        self,
        amount: Amount,
        risk_level: RiskLevel,
    ) -> bool:
        """Check if amount respects limits for risk level."""
        limits = {
            RiskLevel.LOW: Decimal("100000"),
            RiskLevel.MEDIUM: Decimal("50000"),
            RiskLevel.HIGH: Decimal("10000"),
            RiskLevel.CRITICAL: Decimal("0"),  # No transactions allowed
        }

        limit = limits.get(risk_level, Decimal("0"))
        return amount.value <= limit
