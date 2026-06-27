# Banking Compliance System

Architecture: DDD + Hexagonal + Clean Architecture

## 📁 Project Structure

```
banking_compliance/
├── src/
│   ├── domain/              # Core business logic (pure)
│   │   ├── entities.py
│   │   ├── value_objects.py
│   │   ├── aggregates.py
│   │   ├── domain_events.py
│   │   ├── services/
│   │   │   └── compliance_service.py
│   │   └── ports/
│   │       ├── repositories.py
│   │       └── external_services.py
│   ├── application/         # Use cases & orchestration
│   │   ├── dtos.py
│   │   ├── mappers.py
│   │   └── use_cases/
│   │       ├── create_customer.py
│   │       ├── verify_customer.py
│   │       └── monitor_transaction.py
│   ├── adapters/            # Concrete implementations
│   │   ├── inbound/
│   │   │   └── http_adapter.py
│   │   └── outbound/
│   │       ├── in_memory_repository.py
│   │       └── mock_services.py
│   └── infrastructure/      # Configuration & DI
│       ├── container.py
│       └── app.py
├── tests/
│   ├── unit/
│   │   ├── test_domain_entities.py
│   │   └── test_domain_aggregates.py
│   └── integration/
│       └── test_use_cases.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── main.py
```

## 🚀 Setup

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

## ✅ Tests

```bash
python -m pytest tests/ -v
```

## 🏃 Run API

```bash
python main.py
```

API disponible sur: http://localhost:8000

### Endpoints

**Créer un client**:
```bash
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "date_of_birth": "1990-01-01",
    "nationality": "FR",
    "email": "jean@example.com"
  }'
```

**Vérifier KYC**:
```bash
curl -X POST http://localhost:8000/api/v1/customers/{customer_id}/verify
```

**Créer une transaction**:
```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "...",
    "amount": 1000,
    "transaction_type": "transfer",
    "description": "Regular transfer"
  }'
```

## 🏗️ Architecture Highlights

### Domain Layer
- Pure business logic, zero external dependencies
- Value Objects: Amount, ComplianceScore, KYCData
- Entities: Customer, Transaction
- Aggregates: CustomerAggregate, TransactionAggregate
- Domain Events: CustomerVerified, TransactionFlagged, ComplianceAlertRaised

### Application Layer
- Use Cases: CreateCustomer, VerifyCustomer, MonitorTransaction
- DTOs for request/response mapping
- Mappers for Domain ↔ DTO conversions

### Ports & Adapters (Hexagonal)
- **Inbound**: REST API (FastAPI)
- **Outbound**: Repositories, External Services (KYC, AML, Fraud Detection)

### Infrastructure
- Dependency Injection Container (python-injector)
- FastAPI App Factory
- Configuration Management

## 📚 Bounded Contexts

1. **Customer Management**: KYC, Identity, PEP checks
2. **Transaction Monitoring**: AML, Fraud detection, Thresholds
3. **Compliance Reporting**: Regulatory reports
4. **Audit & Traceability**: Immutable logs, Domain events
5. **Risk Management**: Risk scoring, Alerts

## 🧪 Testing Strategy

- Unit tests for domain logic (no dependencies)
- Integration tests for use cases (with mock adapters)
- Contract tests for external APIs (todo)

## 📝 Next Steps

- [ ] SQLAlchemy persistence adapter
- [ ] PostgreSQL integration
- [ ] Event Sourcing / Event Store
- [ ] Compliance Reports generation
- [ ] Real external KYC/AML APIs integration
- [ ] WebSocket for real-time alerts
- [ ] Docker setup
- [ ] CI/CD pipeline

## 📄 License

MIT
