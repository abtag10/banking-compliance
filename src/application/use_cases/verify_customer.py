"""Use Case: Verify Customer through KYC."""

from uuid import UUID
from typing import Optional

from src.domain.value_objects import KYCData
from src.domain.entities import Customer
from src.domain.aggregates import CustomerAggregate
from src.domain.ports.repositories import CustomerRepository
from src.domain.ports.external_services import KYCService, AuditLogger
from src.application.dtos import CustomerDTO, KYCDataDTO
from src.application.mappers import CustomerDTOMapper


class VerifyCustomerUseCase:
    """Use Case for customer KYC verification."""

    def __init__(
        self,
        customer_repo: CustomerRepository,
        kyc_service: KYCService,
        audit_logger: AuditLogger,
    ):
        self.customer_repo = customer_repo
        self.kyc_service = kyc_service
        self.audit_logger = audit_logger
        self.mapper = CustomerDTOMapper()

    def execute(self, customer_id: UUID) -> CustomerDTO:
        """Execute KYC verification."""

        # Retrieve customer aggregate
        customer_agg = self.customer_repo.find_by_id(customer_id)
        if not customer_agg:
            raise ValueError(f"Customer {customer_id} not found")

        # Perform KYC verification
        compliance_score = self.kyc_service.verify(customer_agg.customer.kyc_data)

        # Update aggregate
        customer_agg.verify_customer(compliance_score)

        # Save changes
        self.customer_repo.save(customer_agg)

        # Log audit trail
        self.audit_logger.log(
            entity_id=customer_id,
            action="kyc_verified",
            details={
                "risk_score": compliance_score.score,
                "risk_level": compliance_score.level.value,
                "status": customer_agg.customer.compliance_status.value,
            },
        )

        # Return DTO
        return self.mapper.to_dto(customer_agg.customer)
