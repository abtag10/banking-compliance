"""Repository Ports - Abstractions for persistence."""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from src.domain.entities import Customer, Transaction
from src.domain.aggregates import CustomerAggregate, TransactionAggregate


class CustomerRepository(ABC):
    """Port for Customer persistence."""

    @abstractmethod
    def save(self, aggregate: CustomerAggregate) -> None:
        """Save customer aggregate."""
        pass

    @abstractmethod
    def find_by_id(self, customer_id: UUID) -> Optional[CustomerAggregate]:
        """Retrieve customer by ID."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[CustomerAggregate]:
        """Retrieve customer by email."""
        pass

    @abstractmethod
    def find_all_flagged(self) -> list[CustomerAggregate]:
        """Retrieve all flagged customers."""
        pass


class TransactionRepository(ABC):
    """Port for Transaction persistence."""

    @abstractmethod
    def save(self, aggregate: TransactionAggregate) -> None:
        """Save transaction aggregate."""
        pass

    @abstractmethod
    def find_by_id(self, transaction_id: UUID) -> Optional[TransactionAggregate]:
        """Retrieve transaction by ID."""
        pass

    @abstractmethod
    def find_by_customer(self, customer_id: UUID) -> list[TransactionAggregate]:
        """Retrieve all transactions for a customer."""
        pass

    @abstractmethod
    def find_flagged(self) -> list[TransactionAggregate]:
        """Retrieve all flagged transactions."""
        pass
