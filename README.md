# FastAPI 订单系统接口自动化测试与质量门禁

[![Quality Gate](https://github.com/54sbkyc/fastapi-order-quality-gate/actions/workflows/api-quality-gate.yml/badge.svg)](https://github.com/54sbkyc/fastapi-order-quality-gate/actions/workflows/api-quality-gate.yml)
[![Remote API Smoke](https://github.com/54sbkyc/fastapi-order-quality-gate/actions/workflows/remote-api-smoke.yml/badge.svg)](https://github.com/54sbkyc/fastapi-order-quality-gate/actions/workflows/remote-api-smoke.yml)

这是一个面向自动化测试实习求职的简历项目：自己开发一个小型 FastAPI 订单系统，再用 Pytest 搭建接口自动化测试框架，并接入 GitHub Actions 质量门禁。

项目重点不是“写了几个接口”，而是建立可落地的双层测试：进程内集成测试快速验证业务和数据库副作用，真实 HTTP 黑盒测试通过 `API_BASE_URL` 验证已经运行或部署的服务。两层测试都进入 GitHub Actions，并保留 Allure、覆盖率和服务日志等失败证据。

## 在线验证

- [中文演示后台](https://fastapi-order-quality-gate.onrender.com)
- [Swagger 接口文档](https://fastapi-order-quality-gate.onrender.com/docs)
- [健康检查](https://fastapi-order-quality-gate.onrender.com/api/health)
- [在线 Allure 测试报告](https://54sbkyc.github.io/fastapi-order-quality-gate/)
- [GitHub Actions 公网 Smoke 记录](https://github.com/54sbkyc/fastapi-order-quality-gate/actions/workflows/remote-api-smoke.yml)

公网地址运行在 Render 免费测试环境，闲置后首次访问可能需要等待服务唤醒。演示数据允许重置，不作为生产数据保存。

## 实用型测试分层

| 层级 | 入口 | 解决的问题 |
| --- | --- | --- |
| 进程内 API 集成测试 | `tests/api` | 快速验证业务规则、数据库副作用、并发一致性和接口契约 |
| 真实 HTTP 黑盒测试 | `tests/e2e` | 验证部署后网络访问、鉴权、完整业务链路和用户隔离 |
| 浏览器冒烟 | `frontend/tests` | 保护用户实际操作的最短主链路 |

`tests/e2e` 不导入后端 service、ORM 模型或数据库 Session，只通过 `httpx` 请求目标环境。测试账号使用随机唯一值，订单在 `finally` 中清理；失败时把脱敏后的请求、响应、状态码和耗时附加到 Allure。

## 面试官看点

- 能测接口：覆盖注册登录、商品查询、订单创建、支付、取消、越权访问、库存不足、库存防超卖、幂等重试和非法状态流转。
- 懂业务逻辑：测试不只断言状态码，还验证订单落库、库存扣减、取消恢复库存，以及超卖和重复下单防护等真实副作用。
- 会搭测试框架：使用 fixture 管理用户、JWT token、隔离数据库和真实环境 API Client，并支持 `smoke`、`regression`、`e2e` 分组。
- 会做负向测试：覆盖重复注册、伪造 token、过期 token、不存在用户 token 等认证失败场景。
- 有质量门禁意识：CI 自动运行 Ruff、接口测试、覆盖率门禁、meta 测试、前端构建和 Playwright 主流程冒烟测试。
- 能稳定演示：提供中文 Swagger 文档、中文 React 演示后台、带部署提交号的 `/api/health` 健康检查接口，以及由真实测试产物生成的质量看板。
- 能测试真实环境：通过 `API_BASE_URL`、超时和代理开关切换本地、测试或预发布环境，CI 强制执行黑盒验收。

## 2 分钟演示路径

1. 打开前端：`http://127.0.0.1:5173`
2. 看右上角 API 状态，确认前端通过 `/api/health` 连到后端。
3. 注册或使用自动填充账号登录。
4. 创建订单，观察库存扣减。
5. 支付或取消订单，观察订单状态变化。
6. 使用订单状态筛选，并展示由 `coverage.xml` 和 Allure 结果生成的质量指标。
7. 打开 Swagger：`http://127.0.0.1:8001/docs`
8. 展示测试命令和 CI 质量门禁，说明提交后会自动阻断回归。

## 技术栈

- Backend: FastAPI, SQLAlchemy, SQLite, Pydantic, PyJWT
- Testing: Pytest, FastAPI TestClient, httpx, pytest-cov, Allure pytest, Ruff, Playwright
- Frontend: React, TypeScript, Vite, lucide-react
- CI: GitHub Actions
- Local Demo: Uvicorn, Docker Compose

## 项目结构

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
  e2e/          # real HTTP black-box tests and reusable API client
  meta/         # test-suite and documentation quality checks
  schemas/      # test-only response validation models
frontend/
  src/          # React dashboard frontend
  tests/        # Playwright UI smoke test
docs/
  architecture.md
  api.md
  test-plan.md
  resume-points.md
  interview-guide.md
```

## 快速启动

推荐使用一键演示脚本：

```powershell
.\scripts\demo-start.ps1
```

脚本会启动后端和前端，并检查：

- 后端健康检查：`http://127.0.0.1:8001/api/health`
- Swagger 文档：`http://127.0.0.1:8001/docs`
- 前端后台：`http://127.0.0.1:5173`

演示前想恢复干净数据：

```powershell
.\scripts\demo-reset.ps1
```

本地运行完整质量门禁：

```powershell
.\scripts\quality-gate.ps1
```

运行真实 HTTP 黑盒测试。默认目标未启动时，脚本会临时启动本地 FastAPI，测试后自动停止：

```powershell
.\scripts\api-e2e.ps1
```

只跑发布阻断的最小主链路：

```powershell
.\scripts\api-e2e.ps1 -Marker smoke
```

测试指定环境：

```powershell
$env:API_BASE_URL="https://test-api.example.com"
$env:API_TIMEOUT_SECONDS="15"
.\.venv\Scripts\python -m pytest tests/e2e -m smoke
```

运行包含真实 HTTP 层的本地门禁：

```powershell
.\scripts\quality-gate.ps1 -LiveApi
```

运行 UI 冒烟测试：

```powershell
.\scripts\ui-smoke.ps1
```

运行包含 UI 冒烟的本地质量门禁：

```powershell
.\scripts\quality-gate.ps1 -UiSmoke
```

查看本地质量报告摘要：

```powershell
.\.venv\Scripts\python scripts\report-summary.py
```

根据 OpenAPI 契约生成 DeepSeek 测试建议 prompt：

```powershell
.\.venv\Scripts\python scripts\generate-test-ideas.py --prompt-only
```

如果你本地配置了 DeepSeek API Key：

```powershell
$env:DEEPSEEK_API_KEY="你的 key"
.\.venv\Scripts\python scripts\generate-test-ideas.py
```

脚本默认使用 `https://api.deepseek.com` 和 `deepseek-v4-flash`。DeepSeek 只用于辅助发现测试点，不进入 CI 必跑门禁。

如果想模拟 CI 的干净前端依赖安装，先关闭前端 dev server，再运行：

```powershell
.\scripts\quality-gate.ps1 -CleanInstall
```

脚本文件：[scripts/demo-start.ps1](scripts/demo-start.ps1)、[scripts/quality-gate.ps1](scripts/quality-gate.ps1)、[scripts/api-e2e.ps1](scripts/api-e2e.ps1)、[scripts/ui-smoke.ps1](scripts/ui-smoke.ps1)、[scripts/demo-reset.ps1](scripts/demo-reset.ps1)。可选测试设计工具：[scripts/generate-test-ideas.py](scripts/generate-test-ideas.py)。

脚本说明见 [Demo script](docs/demo-script.md)。

### 手动启动

创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

启动后端 API：

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

打开接口文档：

```text
http://127.0.0.1:8001/docs
```

启动中文前端演示后台：

```powershell
cd frontend
npm install
npm run dev
```

打开前端：

```text
http://127.0.0.1:5173
```

前端通过 Vite proxy 调用后端，所以使用前端时需要保持 FastAPI 运行在 `127.0.0.1:8001`。

## 测试与质量门禁

运行接口自动化测试：

```powershell
python -m pytest tests/api -q
```

直接运行 `pytest` 默认排除需要外部服务的 `e2e` 标记，避免日常开发误连测试环境。按风险选择真实 HTTP 测试：

```powershell
python -m pytest tests/e2e -m smoke
python -m pytest tests/e2e -m regression
python -m pytest tests/e2e -m e2e
```

运行测试工程质量检查：

```powershell
python -m pytest tests/meta -q
```

运行覆盖率门禁：

```powershell
python -m pytest tests/api --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=80
```

生成 Allure 原始结果：

```powershell
python -m pytest tests/api --alluredir=allure-results
```

检查前端构建：

```powershell
cd frontend
npm run build
```

运行浏览器层 UI 冒烟测试：

```powershell
.\scripts\ui-smoke.ps1
```

这条 Playwright 用例覆盖页面加载、API 在线状态、商品列表、注册登录、创建订单、订单展示和质量指标展示。API 自动化负责业务规则深度，UI 冒烟负责保护面试演示主链路。

查看当前本地报告摘要：

```powershell
.\.venv\Scripts\python scripts\report-summary.py
```

GitHub Actions 质量门禁会运行：

```bash
python -m ruff check .
python -m pytest tests/api --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=80 --alluredir=allure-results
python scripts/write_allure_metadata.py
python scripts/build_quality_snapshot.py
python -m pytest tests/meta
docker build --tag order-quality-gate:ci .
# 启动生产容器后：
API_BASE_URL=http://127.0.0.1:8001 python -m pytest tests/e2e -m e2e --alluredir=allure-e2e-results
cd frontend && npm ci && npm run build && npm run ui:smoke
```

CI 产物（CI artifacts）用于失败后复盘：

- `allure-results`：Allure 原始结果、环境信息和失败分类。
- `allure-e2e-results`：真实 HTTP 黑盒测试结果及失败时的脱敏请求响应记录。
- `coverage-xml`：`coverage.xml` 覆盖率数据。
- `frontend-dist`：前端生产构建产物。
- `playwright-report`：浏览器主链路测试的 HTML 报告。
- `ui-service-logs`：仅在 UI 冒烟失败时上传的前后端启动日志。

`main` 分支的质量门禁成功后，独立工作流会合并进程内 API 和真实 HTTP
Allure 结果，并发布到 [在线 Allure 报告](https://54sbkyc.github.io/fastapi-order-quality-gate/)。
发布工作流不处理 PR 产物，只接受 `main` 分支成功的 `push` 运行。

当前本地验证快照：

```text
57 API tests passed
4 live HTTP E2E tests passed
27 meta tests passed
line coverage: 96.04%
branch coverage: 84.62%
coverage.xml generated
quality-summary.json generated from current test artifacts
frontend build passed
UI smoke passed
```

## 核心测试覆盖

- Auth: 注册、登录、错误密码、未登录访问受保护接口。
- Auth negative: 重复注册、伪造 token、过期 token、不存在用户 token。
- Product: 商品列表、商品详情、不存在商品。
- Order: 创建订单、库存不足、不存在商品、用户数据隔离，以及 `Idempotency-Key` 重试防重复下单。
- Inventory: 两个陈旧会话同时购买最后一件库存时，只允许一个订单成功，避免超卖。
- Idempotency: 同一用户、同一键和同一参数只创建一个订单且只扣一次库存；同一键参数冲突返回 `409`；并发唯一键冲突会回滚重复副作用。
- State transitions: 支付、取消、取消恢复库存、重复支付、已取消订单不能支付，以及并发取消只能恢复一次库存。
- System: 健康检查接口返回服务状态、版本和当前部署提交号，支持 CI 核对目标版本是否真正上线。
- Contract: OpenAPI 契约测试保护核心路径、中文接口文档、业务响应码、幂等请求头和 `{code, message}` 错误结构。
- Live HTTP: 对运行中的服务完成健康检查、注册登录、商品查询、创建/查询/取消订单、幂等重试、库存恢复、非法 Token 和跨用户隔离验证。
- Meta: API 测试必须有 Allure title，测试套件必须包含参数化用例，OpenAPI 文档保持中文。
- UI smoke: Playwright 验证页面加载、API 在线、商品渲染、注册登录、创建与支付订单、状态筛选和动态质量指标。

## Docker Compose

```powershell
docker compose up --build
```

同一个容器会运行 FastAPI 并托管构建后的 React 前端：

```text
前端：http://127.0.0.1:8001
Swagger：http://127.0.0.1:8001/docs
健康检查：http://127.0.0.1:8001/api/health
```

Compose 使用 `order-data` 命名卷保存本地 SQLite 数据。删除该卷会重置演示数据：

```powershell
docker compose down -v
```

## 公网测试环境

仓库根目录的 `render.yaml` 用于创建 Render 免费 Web Service。部署采用多阶段
`Dockerfile`：Node 阶段只负责构建 React，最终 Python 镜像以非 root 用户运行
FastAPI，并在同一个公网域名下提供前端、Swagger 和 API。

1. 在 Render Dashboard 选择 `New > Blueprint`，连接此 GitHub 仓库。
2. 确认服务计划为 `Free`，然后应用 Blueprint。
3. 部署完成后打开 Render 分配的 `https://<service>.onrender.com` 地址。
4. 仓库变量 `PUBLIC_API_BASE_URL` 保存公网地址；`Remote API Smoke` 每周自动巡检，
   也可以在 GitHub Actions 手动运行并用 `api_base_url` 临时覆盖目标地址。

生产部署不依赖 Render 偶发漏触发的原生 CI 事件。`Deploy Render` 工作流只接受
`main` 分支成功的 `Quality Gate` push 运行，再通过仓库 Secret
`RENDER_DEPLOY_HOOK_URL` 触发部署。工作流会记录已经通过门禁的完整 Git SHA，并轮询
`/api/health`，直到 Render 运行实例通过 `RENDER_GIT_COMMIT` 返回同一提交；确认目标版本上线后，
才检出该精确提交并执行公网 `smoke`。PR、失败门禁和非主分支 push 都不能进入部署任务，
Hook 也不会写入仓库。Render 原生 Auto-Deploy 保持关闭，避免同一提交重复部署。

也可以直接从本地验证公网环境：

```powershell
.\scripts\api-e2e.ps1 -BaseUrl "https://<service>.onrender.com" -Marker smoke -TimeoutSeconds 20
```

免费实例适合作为可重复初始化的测试环境，不用于保存业务数据：闲置后服务会休眠，
休眠、重启或重新部署会清空本地 SQLite。应用启动时会重新建表并补齐演示商品，
远程 smoke 每次使用随机账号并取消测试订单，因此不依赖历史数据。

## 文档

- [Architecture](docs/architecture.md)
- [API documentation](docs/api.md)
- [Test plan](docs/test-plan.md)
- [Test case design](docs/test-case-design.md)
- [Bug analysis](docs/bug-analysis.md)
- [Resume points](docs/resume-points.md)
- [Interview guide](docs/interview-guide.md)
- [Demo script](docs/demo-script.md)

前端概念图和验证截图：

- [Dashboard concept](docs/assets/frontend-dashboard-concept.png)
- [Rendered dashboard](docs/assets/frontend-dashboard-render.png)
- [Mobile dashboard](docs/assets/frontend-dashboard-mobile.png)

## 简历定位

自动化测试实习版本：

`基于 FastAPI + Pytest 的订单系统接口自动化测试与 CI 质量门禁`

后续转开发岗版本：

`FastAPI 订单管理系统与自动化质量保障`
