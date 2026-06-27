"""Mappers - Domain to DTO conversions."""

from datetime import datetime
from uuid import UUID

from src.domain.entities import Customer, Transaction
from src.application.dtos import CustomerDTO, TransactionDTO


class CustomerDTOMapper:
    """Map Customer entity to DTO."""

    @staticmethod
    def to_dto(customer: Customer) -> CustomerDTO:
        return CustomerDTO(
            customer_id=customer.customer_id,
            first_name=customer.kyc_data.first_name,
            last_name=customer.kyc_data.last_name,
            compliance_status=customer.compliance_status.value,
            risk_score=customer.compliance_score.score if customer.compliance_score else None,
            risk_level=customer.compliance_score.level.value if customer.compliance_score else None,
            is_pep=customer.kyc_data.is_pep,
            created_at=customer.created_at,
        )


class TransactionDTOMapper:
    """Map Transaction entity to DTO."""

    @staticmethod
    def to_dto(transaction: Transaction) -> TransactionDTO:
        return TransactionDTO(
            transaction_id=transaction.transaction_id,
            customer_id=transaction.customer_id,
            amount=transaction.amount.value,
            currency=transaction.amount.currency,
            transaction_type=transaction.transaction_type.value,
            compliance_status=transaction.compliance_status.value,
            description=transaction.description,
            flags=transaction.flags,
            created_at=transaction.created_at,
        )
