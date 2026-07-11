# Demo Script

这份演示稿适合面试时照着走，目标是在 3 分钟内讲清楚：这个项目不是简单调接口，而是一套接口自动化测试和质量门禁闭环。

## 演示前准备

```powershell
.\scripts\demo-reset.ps1
.\scripts\demo-start.ps1
.\scripts\ui-smoke.ps1
.\scripts\api-e2e.ps1
.\.venv\Scripts\python scripts\report-summary.py
.\.venv\Scripts\python scripts\generate-test-ideas.py --prompt-only
```

打开：

- 前端后台：`http://127.0.0.1:5173`
- Swagger：`http://127.0.0.1:8001/docs`

## 3 分钟演示流程

### 1. 先看项目定位

可以这样说：

> 这个项目是我为了自动化测试实习做的作品。后端是我自己写的 FastAPI 订单系统，测试侧用 Pytest 搭了接口自动化框架，并接入了覆盖率、Allure 和 GitHub Actions 质量门禁。

要点：

- 不是只会用工具调接口。
- 自己写后端，说明理解接口背后的业务规则。
- 自动化测试验证的是业务风险，不只是状态码。

### 2. 打开前端，看 API 状态

点击或说明右上角：

- `API 状态：正常`
- `响应时间`

可以这样说：

> 前端通过 `/api/health` 做健康检查。演示前先确认后端服务在线，避免面试时不知道是前端问题还是接口问题。

证明点：

- 有健康检查意识。
- 前后端联调不是靠猜。

### 3. 登录或注册

使用默认账号：

- 用户名：`testuser`
- 密码：`Passw0rd!`

如果登录失败，就切到注册再登录。

可以这样说：

> 登录成功后会拿到 JWT，订单相关接口都需要带 Authorization header，这部分测试里也覆盖了未登录访问和错误登录。

证明点：

- 理解鉴权。
- 知道受保护接口要测未授权场景。

### 4. 创建订单

选择商品，创建 1 个订单。

可以这样说：

> 创建订单不是只看接口返回成功，我的测试还会查数据库，验证订单是否落库、库存是否扣减。

可以补充：

> 库存这里我还加了一个 stale-session 测试，模拟两个会话都先读到最后 1 件库存，最终只能有 1 个订单成功。实现上用数据库条件更新 `stock >= quantity` 做原子扣减；取消订单也用状态条件更新，避免并发取消重复恢复库存。

证明点：

- 有数据库断言。
- 能测接口副作用。
- 能从真实业务风险出发设计库存一致性测试。

### 5. 支付或取消订单

对待支付订单点击支付或取消。

可以这样说：

> 订单状态是一个小状态机。`created` 可以支付或取消，但已支付不能取消，已取消不能再支付，这些非法流转我用参数化测试覆盖了。

证明点：

- 会设计状态流转测试。
- 参数化不是为了炫技，是为了减少重复并覆盖更多组合。

### 6. 展示质量门禁

滚到右侧或底部质量门禁区域。

可以这样说：

> 本地可以运行 `.\scripts\quality-gate.ps1`，CI 会运行 Ruff、API 测试、覆盖率、meta 测试、前端构建和 Playwright 冒烟。核心链路失败或覆盖率不达标，门禁就失败。

证明点：

- 有 CI 思维。
- 知道自动化测试要接入交付流程。
- Allure 原始结果会包含环境信息和失败分类，方便解释报告。
- 看板中的用例数、行覆盖率和分支覆盖率来自本次真实测试产物，不需要手工修改。
- 演示前可运行 `.\scripts\ui-smoke.ps1`，确认浏览器层面的主流程可用；如果想把它并入本地门禁，运行 `.\scripts\quality-gate.ps1 -UiSmoke`。
- 本地可运行 `.\.venv\Scripts\python scripts\report-summary.py` 汇总覆盖率、Allure 结果、前端构建和 Playwright 产物位置。

可以补充：

> CI 失败后我不会只看控制台最后几行，而是下载 CI 产物。`allure-results` 看接口失败细节，`coverage-xml` 看覆盖率，`playwright-report` 看浏览器步骤，UI 失败时再看前后端服务日志。

还可以展示真实 HTTP 层：

```powershell
.\scripts\api-e2e.ps1 -Marker smoke
```

说明这组测试通过 `API_BASE_URL` 请求运行中的服务，失败时 Allure 会保存脱敏后的请求、响应、状态码和耗时。

### 7. 展示 OpenAPI 契约和 DeepSeek 辅助测试设计

可以这样说：

> 我还加了 OpenAPI 契约测试，保护核心路径、中文接口文档、业务响应码和统一错误结构 `{code, message}`。另外 `scripts/generate-test-ideas.py` 可以读取本地 OpenAPI 契约生成 DeepSeek prompt；如果配置了 `DEEPSEEK_API_KEY`，就能直接调用 DeepSeek 给出候选测试点。但 AI 只是辅助发现思路，真正进入质量门禁的还是 Pytest 用例。

命令：

```powershell
.\.venv\Scripts\python scripts\generate-test-ideas.py --prompt-only
```

## Swagger 备用演示

如果前端临时不可用，直接打开：

```text
http://127.0.0.1:8001/docs
```

备用讲法：

1. 先调 `/api/health`，证明服务正常。
2. 调 `/api/auth/register` 和 `/api/auth/login`。
3. 复制 token，点 Swagger 的 Authorize。
4. 调 `/api/products` 看商品。
5. 调 `/api/orders` 创建订单。
6. 调支付或取消接口说明状态流转。

## 常见问题处理

### API 状态离线

先运行：

```powershell
.\scripts\demo-start.ps1
```

再看日志：

```text
.runtime/backend.err.log
```

### 端口被占用

先运行：

```powershell
.\scripts\demo-reset.ps1
```

然后重新启动：

```powershell
.\scripts\demo-start.ps1
```

### 想重新演示干净数据

运行：

```powershell
.\scripts\demo-reset.ps1
.\scripts\demo-start.ps1
```

### 想确认浏览器主流程可用

运行：

```powershell
.\scripts\ui-smoke.ps1
```

如果想把 UI 冒烟和本地质量门禁一起跑：

```powershell
.\scripts\quality-gate.ps1 -UiSmoke
```

### 想查看本地报告摘要

运行：

```powershell
.\.venv\Scripts\python scripts\report-summary.py
```

这个摘要会展示本次 API 通过数、覆盖率、Allure 元数据、前端构建产物，以及 Playwright HTML 报告和 trace/截图目录。

### 想用 DeepSeek 辅助生成测试建议

无 key 时先看 prompt：

```powershell
.\.venv\Scripts\python scripts\generate-test-ideas.py --prompt-only
```

有 DeepSeek API Key 时本地运行：

```powershell
$env:DEEPSEEK_API_KEY="你的 key"
.\.venv\Scripts\python scripts\generate-test-ideas.py
```

## 结束语

可以这样收尾：

> 这个项目我主要想展示三件事：第一，我能理解接口背后的业务逻辑；第二，我能用 Pytest 把正常、异常、边界和状态流转场景自动化；第三，我知道自动化测试要进入质量门禁，并用 Playwright 冒烟测试保护真实演示链路。
