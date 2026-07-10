# Test Plan

## Test Objective

Verify the core API behavior of a small order system and demonstrate automation testing engineering practices suitable for internship interviews.

## Scope

In scope:

- Health check API
- OpenAPI contract
- Authentication API
- Authentication negative and token failure scenarios
- Product query API
- Order creation API
- Order query API
- Order payment and cancellation state transitions
- Concurrent order cancellation consistency
- Inventory consistency and oversell prevention
- Parameterized abnormal and boundary tests
- Response schema validation
- Database assertions
- Allure report metadata
- Allure environment and category metadata
- Coverage threshold
- Coverage XML report delivery
- Meta tests for test-suite quality and Chinese API documentation
- DeepSeek local test-idea helper assets
- CI quality gate
- CI artifacts for failure investigation
- Frontend production build verification
- Browser-level UI smoke testing for the main demo workflow
- Real HTTP black-box testing against configurable environments
- Smoke and regression test selection through Pytest markers
- Redacted request/response diagnostics on live-test failures

Out of scope:

- Real payment gateway integration
- Full browser UI regression suite
- Large-scale performance testing
- Complex role permission systems

## Test Strategy

The fast integration suite uses `pytest` and FastAPI's in-process test client. Each test gets an isolated SQLite database through dependency override. A separate `tests/e2e` suite uses `httpx` and `API_BASE_URL` to call a running service without importing backend services or database objects.

Core fixture responsibilities:

- `client`: API test client with test database override.
- `db_session`: isolated SQLAlchemy session.
- `registered_user`: creates a normal user.
- `auth_headers`: returns a valid JWT authorization header.
- `seed_products`: creates deterministic product data.
- `created_order`: creates one order for state transition tests.
- `live_api`: reusable real HTTP client with timeout, proxy control, redacted history, and health precheck.

## Scenario Matrix

| Module | Scenario | Assertion Focus |
| --- | --- | --- |
| Contract | OpenAPI core route map | Required API paths and methods remain documented |
| Contract | OpenAPI Chinese docs | Core summaries and descriptions remain Chinese |
| Contract | Business response codes | Important `201`, `401`, `403`, `404`, `409`, `422` responses are documented |
| Contract | Error response schema | Reusable `{code, message}` error response contract |
| System | Health check | Service status and version metadata |
| Auth | Register user successfully | Status code and response body |
| Auth | Register duplicate username | `USER_ALREADY_EXISTS` |
| Auth | Login successfully | JWT token response |
| Auth | Login with wrong password or unknown user | `INVALID_CREDENTIALS` |
| Auth | Access protected API without token | `NOT_AUTHENTICATED` |
| Auth | Access protected API with malformed or forged token | `INVALID_TOKEN` |
| Auth | Access protected API with expired token | `INVALID_TOKEN` |
| Auth | Access protected API with token for nonexistent user | `INVALID_TOKEN` |
| Product | List products | Response schema |
| Product | Get product detail | Response schema and product identity |
| Product | Get nonexistent product with multiple invalid IDs | `PRODUCT_NOT_FOUND` |
| Order | Create order successfully | API response, DB order, stock decrease |
| Order | Create order without login | `NOT_AUTHENTICATED` |
| Order | Product not found | `PRODUCT_NOT_FOUND` |
| Order | Insufficient stock | `INSUFFICIENT_STOCK` |
| Order | Inactive product | `PRODUCT_INACTIVE` |
| Order | Invalid quantities: zero, negative, over limit | `VALIDATION_ERROR` |
| Order | List my orders | User data isolation |
| Order | Access another user's order | `FORBIDDEN_ORDER_ACCESS` |
| Inventory | Stale sessions buy last stock | One order succeeds, second returns `INSUFFICIENT_STOCK`, final stock remains 0 |
| State | Pay created order | Status becomes `paid` |
| State | Cancel created order | Status becomes `cancelled`, stock restored |
| State | Parameterized invalid state transitions | `INVALID_ORDER_STATE` |
| State | Two stale sessions cancel one order | Only one cancellation succeeds and stock is restored once |
| Meta | API tests include Allure titles | Report readability |
| Meta | API suite includes parameterized tests | Test design quality |
| Meta | OpenAPI documentation remains Chinese | Demo readability |
| Meta | Allure metadata generator is wired into quality gate | Report explainability |
| Meta | README links testing design documents | Interview readiness |
| Meta | Report delivery wiring remains documented | CI artifacts, `coverage.xml`, and local summary script |
| Meta | DeepSeek helper remains optional | Script and env docs exist, quality gate does not require `DEEPSEEK_API_KEY` |
| Live HTTP smoke | Register, login, query product, create/query/cancel order | Deployed service and stock restoration work through the network |
| Live HTTP regression | Invalid token | Running service returns `INVALID_TOKEN` |
| Live HTTP regression | Cross-user order access | Running service returns `FORBIDDEN_ORDER_ACCESS` |
| Frontend | Production build | TypeScript and Vite integration |
| UI smoke | Main demo workflow with Playwright | Page load, API online status, product rendering, auth, order creation/payment, filtering, and generated quality metrics |

## Quality Gate

GitHub Actions runs these checks on push and pull request:

```bash
python -m ruff check .
python -m pytest tests/api --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=80 --alluredir=allure-results
python scripts/write_allure_metadata.py
python scripts/build_quality_snapshot.py
python -m pytest tests/meta
API_BASE_URL=http://127.0.0.1:8001 python -m pytest tests/e2e -m e2e --alluredir=allure-e2e-results
cd frontend && npm ci && npm run build && npm run ui:smoke
```

If lint, integration tests, live HTTP tests, meta tests, coverage threshold, frontend build, or UI smoke fails, the workflow fails and blocks the change.

Local quality gate can run an extra browser smoke layer:

```powershell
.\scripts\quality-gate.ps1 -UiSmoke
```

The UI smoke layer is intentionally small. API automation covers business rules and database side effects in depth, while Playwright protects the interview demo path from browser-level regressions.

The coverage threshold is set to 80% for the application package. This keeps the gate realistic for an internship project while still proving that the main business paths are protected by automated regression tests.

Local quality gate additionally writes Allure metadata files:

- `allure-results/environment.properties`
- `allure-results/categories.json`

It also cleans stale Allure results, generates `coverage.xml` and `frontend/public/quality-summary.json`, then runs `scripts/report-summary.py` to print a local Chinese summary of the current run.

CI 产物（CI artifacts）preserve evidence after a run:

- `allure-results`: raw Allure result files plus environment and category metadata.
- `allure-e2e-results`: live HTTP results and redacted request/response evidence on failure.
- `coverage-xml`: `coverage.xml` for coverage review.
- `frontend-dist`: built frontend output after a successful production build.
- `playwright-report`: browser smoke HTML report.
- `ui-service-logs`: backend and frontend logs uploaded only after UI smoke failure.

Playwright UI smoke runs in CI to protect the browser demo path. Locally it remains optional through `.\scripts\quality-gate.ps1 -UiSmoke`, so the faster API-focused gate is still convenient during development.

DeepSeek is also kept outside the deterministic quality gate. `scripts/generate-test-ideas.py` can read the local OpenAPI contract and ask DeepSeek for test ideas when `DEEPSEEK_API_KEY` is configured, but generated ideas must be reviewed and converted into Pytest cases manually.
