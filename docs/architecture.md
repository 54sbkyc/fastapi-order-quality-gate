# Architecture

## Application Layers

```mermaid
flowchart LR
    Frontend["React 中文演示后台"] --> Routes["FastAPI Routes"]
    Client["Pytest API 自动化"] --> Routes
    Routes --> Security["JWT Auth Dependency"]
    Routes --> Schemas["Pydantic Schemas"]
    Routes --> Services["Service Layer"]
    Services --> Models["SQLAlchemy Models"]
    Models --> DB["SQLite Database"]
```

## Automation Test Flow

```mermaid
flowchart TD
    Start["pytest starts"] --> Fixtures["Load fixtures"]
    Fixtures --> DBSetup["Create isolated SQLite database"]
    DBSetup --> Seed["Seed deterministic product data"]
    Seed --> API["Call FastAPI endpoints"]
    API --> AssertAPI["Assert status code, body, business code"]
    AssertAPI --> AssertDB["Assert database side effects"]
    AssertDB --> Allure["Write Allure results"]
    Allure --> Coverage["Calculate app coverage"]
    Coverage --> Gate["Quality gate passes or fails"]
```

## Order State Machine

```mermaid
stateDiagram-v2
    [*] --> created
    created --> paid: pay
    created --> cancelled: cancel
    paid --> [*]
    cancelled --> [*]
```

Invalid transitions covered by automated tests:

- `paid -> cancelled`
- `cancelled -> paid`
- `paid -> paid`

## Why This Design Helps Interviews

- The backend is small enough to explain in a few minutes.
- The frontend makes the core workflow easier to demonstrate than Swagger alone.
- The test suite proves business behavior, not only HTTP status codes.
- Fixtures show test data setup and cleanup ability.
- Database assertions show that API tests can verify real persistence effects.
- CI quality gate shows how automation protects code changes before merge.
