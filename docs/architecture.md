# Architecture

## Application Layers

```mermaid
flowchart LR
    Frontend["React 中文演示后台"] --> Routes["FastAPI Routes"]
    Client["进程内 Pytest 集成测试"] --> Routes
    LiveClient["httpx 真实 HTTP E2E"] -->|"API_BASE_URL"| Routes
    Routes --> Health["/api/health 健康检查"]
    Routes --> Security["JWT Auth Dependency"]
    Routes --> Schemas["Pydantic Schemas"]
    Routes --> Services["Service Layer"]
    Services --> Models["SQLAlchemy Models"]
    Models --> DB["SQLite Database"]
    Coverage["coverage.xml + Allure 结果"] --> Snapshot["质量快照 JSON"]
    Snapshot --> Frontend
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
    Coverage --> Snapshot["Generate quality snapshot"]
    Snapshot --> Meta["Run meta tests"]
    Meta --> FrontendBuild["Build frontend"]
    FrontendBuild --> UISmoke["Run Playwright smoke"]
    UISmoke --> Gate["Quality gate passes or fails"]
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
- concurrent `cancel -> cancel`

## Why This Design Helps Interviews

- The backend is small enough to explain in a few minutes.
- The frontend makes the core workflow easier to demonstrate than Swagger alone.
- The health endpoint gives the frontend and demo flow a clear API status signal.
- The test suite proves business behavior, not only HTTP status codes.
- Fixtures show test data setup and cleanup ability.
- Database assertions show that API tests can verify real persistence effects.
- Application startup uses FastAPI lifespan, so importing modules does not create database files as a side effect.
- CI quality gate protects backend behavior, test-suite quality, frontend build stability, and the browser demo path before merge.
