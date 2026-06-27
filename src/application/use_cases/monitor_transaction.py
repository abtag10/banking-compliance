"""Use Case: Monitor Transaction for Compliance."""

from uuid import UUID

from src.domain.entities import Transaction
from src.domain.aggregates import TransactionAggregate
from src.domain.ports.repositories import TransactionRepository
from src.domain.ports.external_services import AuditLogger, EventPublisher
from src.domain.services.compliance_service import ComplianceService
from src.application.dtos import TransactionDTO
from src.application.mappers import TransactionDTOMapper


class MonitorTransactionUseCase:
    """Use Case for transaction monitoring and compliance checks."""

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        compliance_service: ComplianceService,
        event_publisher: EventPublisher,
        audit_logger: AuditLogger,
    ):
        self.transaction_repo = transaction_repo
        self.compliance_service = compliance_service
        self.event_publisher = event_publisher
        self.audit_logger = audit_logger
        self.mapper = TransactionDTOMapper()

    def execute(self, transaction_id: UUID) -> TransactionDTO:
        """Monitor transaction and apply compliance checks."""

        # Retrieve transaction
        transaction_agg = self.transaction_repo.find_by_id(transaction_id)
        if not transaction_agg:
            raise ValueError(f"Transaction {transaction_id} not found")

        # Perform compliance checks
        is_compliant, reason = self.compliance_service.check_transaction_compliance(
            transaction_agg
        )

        if is_compliant:
            transaction_agg.approve_transaction()
        else:
            transaction_agg.flag_transaction(reason or "Unknown compliance issue")

        # Save changes
        self.transaction_repo.save(transaction_agg)

        # Publish events
        for event in transaction_agg.get_uncommitted_events():
            self.event_publisher.publish(event)

        # Log audit
        self.audit_logger.log(
            entity_id=transaction_id,
            action="transaction_monitored",
            details={
                "is_compliant": is_compliant,
                "status": transaction_agg.transaction.compliance_status.value,
                "flags": transaction_agg.transaction.flags,
            },
        )

        return self.mapper.to_dto(transaction_agg.transaction)
