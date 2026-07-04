# FastAPI Order Quality Gate

一个面向自动化测试实习求职的项目：自己开发小型 FastAPI 订单系统，并使用 Pytest 搭建 API 自动化测试框架和 GitHub Actions 质量门禁。

## Highlights

- FastAPI 后端接口：注册登录、商品查询、订单创建、支付模拟、取消订单。
- JWT 鉴权：订单接口需要登录后访问。
- SQLAlchemy + SQLite：本地和 CI 都能轻量运行。
- Pytest API 自动化：覆盖正常、异常、边界和订单状态流转。
- 数据库断言：验证订单落库、库存扣减、取消恢复库存。
- Pydantic 响应校验：测试中校验接口返回结构。
- Allure 报告：支持生成自动化测试报告。
- 覆盖率门禁：CI 要求 `app` 包覆盖率不低于 80%。
- GitHub Actions：提交后自动执行 lint、接口测试和覆盖率检查，失败则质量门禁失败。

## Project Structure

```text
app/
  api/          # FastAPI routes
  core/         # config, JWT, business exceptions
  db/           # SQLAlchemy session and seed data
  models/       # database models
  schemas/      # API request/response schemas
  services/     # business logic
tests/
  api/          # API automation cases
  schemas/      # test-only response validation models
docs/
  architecture.md
  api.md
  test-plan.md
  resume-points.md
```

## Quick Start

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Run the API:

```powershell
python -m uvicorn app.main:app --reload
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

Run API automation tests:

```powershell
python -m pytest tests/api -q
```

Run test-suite quality checks:

```powershell
python -m pytest tests/meta -q
```

Run tests with coverage gate:

```powershell
python -m pytest tests/api --cov=app --cov-report=term-missing --cov-fail-under=80
```

Generate Allure raw results:

```powershell
python -m pytest tests/api --alluredir=allure-results
```

If the Allure CLI is installed, view the report:

```powershell
allure serve allure-results
```

## Docker Compose

```powershell
docker compose up
```

The API runs at:

```text
http://127.0.0.1:8000
```

## Quality Gate

The GitHub Actions workflow runs:

```bash
python -m ruff check .
python -m pytest tests/api --cov=app --cov-report=term-missing --cov-fail-under=80 --alluredir=allure-results
```

If any API automation test fails, the workflow fails. This is the CI quality gate.

Current local verification snapshot:

```text
23 API tests passed
2 meta tests passed
app coverage: about 95%
```

## Documentation

- [Architecture](docs/architecture.md)
- [API documentation](docs/api.md)
- [Test plan](docs/test-plan.md)
- [Resume points](docs/resume-points.md)

## Seed Products

The system seeds these products when needed:

| Name | Price | Stock |
| --- | ---: | ---: |
| Keyboard | 199.00 | 10 |
| Mouse | 99.00 | 20 |
| Monitor | 899.00 | 5 |

## Core Test Coverage

- Auth: register, login, invalid password, protected API without token.
- Product: list, detail, nonexistent product.
- Order: create order, insufficient stock, nonexistent product, user isolation.
- State transitions: pay, cancel, stock restore, double pay, cancelled order cannot be paid.
- Meta tests: ensure API tests have Allure titles and enough parameterized cases.

## Resume Positioning

For automation testing internships, emphasize:

- Pytest API automation framework
- fixture-based test data management
- response schema validation
- database assertions
- Allure report
- coverage quality gate
- GitHub Actions quality gate

For future backend development roles, emphasize:

- FastAPI backend API design
- SQLAlchemy persistence
- JWT authentication
- service-layer business rules
- automated regression protection
