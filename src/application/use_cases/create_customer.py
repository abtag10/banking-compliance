"""Use Case: Create Customer."""

from uuid import uuid4

from src.domain.value_objects import KYCData
from src.domain.entities import Customer
from src.domain.aggregates import CustomerAggregate
from src.domain.ports.repositories import CustomerRepository
from src.domain.ports.external_services import AuditLogger
from src.application.dtos import CustomerDTO, KYCDataDTO
from src.application.mappers import CustomerDTOMapper


class CreateCustomerUseCase:
    """Use Case for customer creation."""

    def __init__(
        self,
        customer_repo: CustomerRepository,
        audit_logger: AuditLogger,
    ):
        self.customer_repo = customer_repo
        self.audit_logger = audit_logger
        self.mapper = CustomerDTOMapper()

    def execute(self, kyc_dto: KYCDataDTO) -> CustomerDTO:
        """Create new customer."""

        # Create value object
        kyc_data = KYCData(
            first_name=kyc_dto.first_name,
            last_name=kyc_dto.last_name,
            date_of_birth=kyc_dto.date_of_birth,
            nationality=kyc_dto.nationality,
        )

        # Create entity
        customer = Customer(
            kyc_data=kyc_data,
            email=kyc_dto.email,
            phone=kyc_dto.phone,
        )

        # Create aggregate
        aggregate = CustomerAggregate(customer=customer)

        # Save
        self.customer_repo.save(aggregate)

        # Log
        self.audit_logger.log(
            entity_id=customer.customer_id,
            action="customer_created",
            details={
                "email": kyc_dto.email,
                "nationality": kyc_dto.nationality,
            },
        )

        return self.mapper.to_dto(customer)
