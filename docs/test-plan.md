# Test Plan

## Test Objective

Verify the core API behavior of a small order system and demonstrate automation testing engineering practices suitable for internship interviews.

## Scope

In scope:

- Authentication API
- Product query API
- Order creation API
- Order query API
- Order payment and cancellation state transitions
- Parameterized abnormal and boundary tests
- Response schema validation
- Database assertions
- Allure report metadata
- Coverage threshold
- CI quality gate

Out of scope:

- Real payment gateway integration
- Frontend UI testing
- Large-scale performance testing
- Complex role permission systems

## Test Strategy

The tests use `pytest` and FastAPI's in-process test client. Each test gets an isolated SQLite database through dependency override, so cases do not depend on execution order.

Core fixture responsibilities:

- `client`: API test client with test database override.
- `db_session`: isolated SQLAlchemy session.
- `registered_user`: creates a normal user.
- `auth_headers`: returns a valid JWT authorization header.
- `seed_products`: creates deterministic product data.
- `created_order`: creates one order for state transition tests.

## Scenario Matrix

| Module | Scenario | Assertion Focus |
| --- | --- | --- |
| Auth | Register user successfully | Status code and response body |
| Auth | Login successfully | JWT token response |
| Auth | Login with wrong password or unknown user | `INVALID_CREDENTIALS` |
| Auth | Access protected API without token | `NOT_AUTHENTICATED` |
| Product | List products | Response schema |
| Product | Get product detail | Response schema and product identity |
| Product | Get nonexistent product with multiple invalid IDs | `PRODUCT_NOT_FOUND` |
| Order | Create order successfully | API response, DB order, stock decrease |
| Order | Create order without login | `NOT_AUTHENTICATED` |
| Order | Product not found | `PRODUCT_NOT_FOUND` |
| Order | Insufficient stock | `INSUFFICIENT_STOCK` |
| Order | Invalid quantities: zero, negative, over limit | `VALIDATION_ERROR` |
| Order | List my orders | User data isolation |
| Order | Access another user's order | `FORBIDDEN_ORDER_ACCESS` |
| State | Pay created order | Status becomes `paid` |
| State | Cancel created order | Status becomes `cancelled`, stock restored |
| State | Parameterized invalid state transitions | `INVALID_ORDER_STATE` |
| Meta | API tests include Allure titles | Report readability |
| Meta | API suite includes parameterized tests | Test design quality |

## Quality Gate

GitHub Actions runs lint and API tests on push and pull request:

```bash
python -m ruff check .
python -m pytest tests/api --cov=app --cov-report=term-missing --cov-fail-under=80 --alluredir=allure-results
```

If any key API test fails, the workflow fails and blocks the change.

The coverage threshold is set to 80% for the application package. This keeps the gate realistic for an internship project while still proving that the main business paths are protected by automated regression tests.
