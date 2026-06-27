"""HTTP Adapter - REST API endpoints."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from decimal import Decimal

from src.application.dtos import KYCDataDTO, CustomerDTO, TransactionDTO
from src.application.use_cases.create_customer import CreateCustomerUseCase
from src.application.use_cases.verify_customer import VerifyCustomerUseCase
from src.application.use_cases.monitor_transaction import MonitorTransactionUseCase
from src.domain.value_objects import Amount, TransactionType
from src.domain.entities import Transaction
from src.domain.aggregates import TransactionAggregate
from src.domain.ports.repositories import TransactionRepository


class HTTPAdapter:
    """HTTP REST API adapter."""

    def __init__(
        self,
        create_customer_uc: CreateCustomerUseCase,
        verify_customer_uc: VerifyCustomerUseCase,
        monitor_transaction_uc: MonitorTransactionUseCase,
        transaction_repo: TransactionRepository,
    ):
        self.create_customer_uc = create_customer_uc
        self.verify_customer_uc = verify_customer_uc
        self.monitor_transaction_uc = monitor_transaction_uc
        self.transaction_repo = transaction_repo
        self.router = APIRouter(prefix="/api/v1")
        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes."""

        @self.router.post("/customers", response_model=CustomerDTO)
        async def create_customer(kyc_data: KYCDataDTO):
            try:
                return self.create_customer_uc.execute(kyc_data)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e),
                )

        @self.router.post("/customers/{customer_id}/verify", response_model=CustomerDTO)
        async def verify_customer(customer_id: UUID):
            try:
                return self.verify_customer_uc.execute(customer_id)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=str(e),
                )

        @self.router.post("/transactions")
        async def create_transaction(
            customer_id: UUID,
            amount: Decimal,
            transaction_type: str,
            description: str = None,
        ):
            try:
                # Create transaction
                tx = Transaction(
                    customer_id=customer_id,
                    amount=Amount(amount, "EUR"),
                    transaction_type=TransactionType(transaction_type),
                    description=description,
                )
                agg = TransactionAggregate(transaction=tx)
                self.transaction_repo.save(agg)

                # Monitor it
                return self.monitor_transaction_uc.execute(tx.transaction_id)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e),
                )

        @self.router.get("/transactions/{transaction_id}", response_model=TransactionDTO)
        async def get_transaction(transaction_id: UUID):
            agg = self.transaction_repo.find_by_id(transaction_id)
            if not agg:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaction not found",
                )
            from src.application.mappers import TransactionDTOMapper
            return TransactionDTOMapper.to_dto(agg.transaction)

    def get_router(self):
        """Get FastAPI router."""
        return self.router
