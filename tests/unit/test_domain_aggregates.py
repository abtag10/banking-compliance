"""Unit tests for domain aggregates."""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.entities import Customer, Transaction
from src.domain.aggregates import CustomerAggregate, TransactionAggregate
from src.domain.value_objects import (
    Amount,
    KYCData,
    ComplianceScore,
    RiskLevel,
    TransactionType,
)
from src.domain.domain_events import CustomerVerified, TransactionFlagged


class TestCustomerAggregate:
    """Tests for Customer Aggregate."""

    def test_verify_customer_emits_event(self):
        """Test that verifying customer emits event."""
        kyc = KYCData(
            first_name="Alice",
            last_name="Brown",
            date_of_birth="1988-07-10",
            nationality="ES",
        )
        customer = Customer(kyc_data=kyc)
        agg = CustomerAggregate(customer=customer)

        score = ComplianceScore(
            score=40.0,
            level=RiskLevel.MEDIUM,
            calculation_date=datetime.now(),
        )
        agg.verify_customer(score)

        events = agg.get_uncommitted_events()
        assert len(events) == 1
        assert isinstance(events[0], CustomerVerified)

    def test_aggregate_version_increments(self):
        """Test that aggregate version increments with changes."""
        kyc = KYCData(
            first_name="Test",
            last_name="User",
            date_of_birth="1990-01-01",
            nationality="FR",
        )
        customer = Customer(kyc_data=kyc)
        agg = CustomerAggregate(customer=customer)

        assert agg.version == 1

        score = ComplianceScore(
            score=25.0,
            level=RiskLevel.LOW,
            calculation_date=datetime.now(),
        )
        agg.verify_customer(score)

        assert agg.version == 2


class TestTransactionAggregate:
    """Tests for Transaction Aggregate."""

    def test_flag_transaction_emits_event(self):
        """Test that flagging transaction emits event."""
        tx = Transaction(
            customer_id=uuid4(),
            amount=Amount(Decimal("75000"), "EUR"),
            transaction_type=TransactionType.TRANSFER,
        )
        agg = TransactionAggregate(transaction=tx)

        agg.flag_transaction("High amount")

        events = agg.get_uncommitted_events()
        assert len(events) == 1
        assert isinstance(events[0], TransactionFlagged)
        assert events[0].flag_reason == "High amount"

    def test_approve_transaction(self):
        """Test approving transaction."""
        tx = Transaction(
            customer_id=uuid4(),
            amount=Amount(Decimal("500"), "EUR"),
            transaction_type=TransactionType.DEPOSIT,
        )
        agg = TransactionAggregate(transaction=tx)

        agg.approve_transaction()

        assert agg.transaction.is_approved()
