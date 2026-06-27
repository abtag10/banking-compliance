"""Unit tests for domain entities."""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.entities import Customer, Transaction
from src.domain.value_objects import (
    Amount,
    KYCData,
    ComplianceScore,
    RiskLevel,
    TransactionType,
)


class TestCustomer:
    """Tests for Customer entity."""

    def test_create_customer(self):
        """Test creating a customer."""
        kyc = KYCData(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            nationality="FR",
        )

        customer = Customer(kyc_data=kyc, email="john@example.com")

        assert customer.kyc_data.first_name == "John"
        assert customer.email == "john@example.com"
        assert not customer.is_compliant()

    def test_verify_customer(self):
        """Test customer verification."""
        kyc = KYCData(
            first_name="Jane",
            last_name="Smith",
            date_of_birth="1985-05-15",
            nationality="DE",
        )
        customer = Customer(kyc_data=kyc)

        score = ComplianceScore(
            score=30.0,
            level=RiskLevel.LOW,
            calculation_date=datetime.now(),
        )
        customer.verify_kyc(score)

        assert customer.is_compliant()
        assert customer.compliance_score.score == 30.0

    def test_flag_customer(self):
        """Test flagging a customer."""
        kyc = KYCData(
            first_name="Bob",
            last_name="Johnson",
            date_of_birth="1992-03-20",
            nationality="IT",
        )
        customer = Customer(kyc_data=kyc)

        customer.flag_for_review("Suspicious activity")

        assert not customer.is_compliant()


class TestTransaction:
    """Tests for Transaction entity."""

    def test_create_transaction(self):
        """Test creating a transaction."""
        customer_id = uuid4()
        amount = Amount(Decimal("1000.50"), "EUR")

        tx = Transaction(
            customer_id=customer_id,
            amount=amount,
            transaction_type=TransactionType.TRANSFER,
            description="Test transfer",
        )

        assert tx.customer_id == customer_id
        assert tx.amount.value == Decimal("1000.50")
        assert not tx.is_approved()

    def test_approve_transaction(self):
        """Test approving a transaction."""
        tx = Transaction(
            customer_id=uuid4(),
            amount=Amount(Decimal("500"), "EUR"),
            transaction_type=TransactionType.DEPOSIT,
        )

        tx.approve()

        assert tx.is_approved()

    def test_flag_transaction(self):
        """Test flagging a transaction."""
        tx = Transaction(
            customer_id=uuid4(),
            amount=Amount(Decimal("100000"), "EUR"),
            transaction_type=TransactionType.TRANSFER,
        )

        tx.flag("Amount exceeds limit")

        assert not tx.is_approved()
        assert "Amount exceeds limit" in tx.flags


class TestAmount:
    """Tests for Amount value object."""

    def test_create_amount(self):
        """Test creating an amount."""
        amount = Amount(Decimal("100.50"), "EUR")
        assert amount.value == Decimal("100.50")
        assert amount.currency == "EUR"

    def test_amount_addition(self):
        """Test adding amounts."""
        a1 = Amount(Decimal("100"), "EUR")
        a2 = Amount(Decimal("50"), "EUR")

        result = a1 + a2

        assert result.value == Decimal("150")

    def test_amount_invalid_currency_add(self):
        """Test that adding different currencies raises error."""
        a1 = Amount(Decimal("100"), "EUR")
        a2 = Amount(Decimal("50"), "USD")

        with pytest.raises(ValueError):
            a1 + a2

    def test_amount_is_above(self):
        """Test amount comparison."""
        amount = Amount(Decimal("1000"), "EUR")

        assert amount.is_above(Decimal("500"))
        assert not amount.is_above(Decimal("2000"))
