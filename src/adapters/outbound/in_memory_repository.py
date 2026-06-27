"""In-Memory Repository Adapter - For testing/simple use cases."""

from uuid import UUID
from typing import Optional, Dict

from src.domain.entities import Customer, Transaction
from src.domain.aggregates import CustomerAggregate, TransactionAggregate
from src.domain.ports.repositories import CustomerRepository, TransactionRepository


class InMemoryCustomerRepository(CustomerRepository):
    """In-memory implementation of CustomerRepository."""

    def __init__(self):
        self.customers: Dict[UUID, CustomerAggregate] = {}

    def save(self, aggregate: CustomerAggregate) -> None:
        self.customers[aggregate.customer.customer_id] = aggregate
        aggregate.clear_events()

    def find_by_id(self, customer_id: UUID) -> Optional[CustomerAggregate]:
        return self.customers.get(customer_id)

    def find_by_email(self, email: str) -> Optional[CustomerAggregate]:
        for agg in self.customers.values():
            if agg.customer.email == email:
                return agg
        return None

    def find_all_flagged(self) -> list[CustomerAggregate]:
        from src.domain.value_objects import ComplianceStatus
        return [
            agg for agg in self.customers.values()
            if agg.customer.compliance_status == ComplianceStatus.FLAGGED
        ]


class InMemoryTransactionRepository(TransactionRepository):
    """In-memory implementation of TransactionRepository."""

    def __init__(self):
        self.transactions: Dict[UUID, TransactionAggregate] = {}

    def save(self, aggregate: TransactionAggregate) -> None:
        self.transactions[aggregate.transaction.transaction_id] = aggregate
        aggregate.clear_events()

    def find_by_id(self, transaction_id: UUID) -> Optional[TransactionAggregate]:
        return self.transactions.get(transaction_id)

    def find_by_customer(self, customer_id: UUID) -> list[TransactionAggregate]:
        return [
            agg for agg in self.transactions.values()
            if agg.transaction.customer_id == customer_id
        ]

    def find_flagged(self) -> list[TransactionAggregate]:
        from src.domain.value_objects import TransactionStatus
        return [
            agg for agg in self.transactions.values()
            if agg.transaction.compliance_status == TransactionStatus.FLAGGED
        ]
