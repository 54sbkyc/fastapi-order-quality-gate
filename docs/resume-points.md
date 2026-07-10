# Resume Points

## Automation Testing Version

Project:

`基于 FastAPI + Pytest 的订单系统接口自动化测试与 CI 质量门禁`

Resume bullets:

- 基于 Pytest 搭建双层 API 自动化框架：进程内集成测试覆盖业务规则、数据库副作用和并发一致性，真实 HTTP 黑盒测试通过可配置 `API_BASE_URL` 验证部署后的完整订单链路。
- 使用 fixture 管理测试用户、JWT token、商品种子数据和隔离数据库，保证用例可重复执行且互不依赖。
- 封装 `httpx` API Client，支持环境地址、超时和代理配置，使用随机账号和 `finally` 清理订单；失败时向 Allure 附加脱敏请求、响应、状态码与耗时。
- 通过参数化思路覆盖正常、异常和状态流转场景，并结合 Pydantic 响应结构校验与 SQLAlchemy 数据库断言验证接口真实落库结果。
- 集成 Allure、`coverage.xml` 与 GitHub Actions 质量门禁，自动执行 48 条集成测试、3 条真实 HTTP 验收、meta 检查、前端构建和 Playwright 冒烟，核心链路失败或覆盖率低于 80% 时阻断流水线。
- 设计质量快照与报告摘要脚本，从本次 Allure 和覆盖率产物动态生成前端指标，并在 CI artifacts 中保留接口、覆盖率、构建和 UI 报告，避免历史结果累积或手工数字失真。
- 接入 DeepSeek 本地测试建议生成脚本，根据 OpenAPI 契约生成候选测试点；AI 仅辅助设计，最终通过 Pytest 用例进入确定性质量门禁。

Interview talking points:

- 为什么接口测试不只断言状态码，还要断言业务错误码和数据库状态。
- 如何用 pytest fixture 降低登录、测试数据准备和清理的重复成本。
- 如何设计订单状态流转测试，比如 `created -> paid`、`created -> cancelled`、重复支付、已支付取消。
- 如何设计 stale-session 库存一致性测试，验证最后 1 件库存不会被两个会话同时买走。
- 如何用条件更新保护支付/取消状态流转，避免并发取消重复恢复库存。
- 为什么进程内 `TestClient` 不能替代部署后 HTTP 验收，以及两层测试如何平衡速度和真实性。
- 如何覆盖伪造 token、过期 token、重复注册等认证负向场景。
- CI 质量门禁如何帮助团队在代码合并前发现接口回归。
- 为什么给 CI 增加覆盖率阈值，以及覆盖率不能替代业务断言。
- 为什么把前端构建、测试套件质量检查和 Playwright 主链路也放进 CI。
- 如何通过 CI 产物查看 Allure 原始结果、coverage.xml 和前端构建证据。
- OpenAPI 契约测试如何保护路径、中文文档、响应码和 `{code, message}` 错误结构。
- DeepSeek 如何辅助发现测试点，以及为什么不能替代自动化测试断言。

## Backend Development Version

Project:

`FastAPI 订单管理系统与自动化质量保障`

Resume bullets:

- 基于 FastAPI 开发小型订单管理系统，实现用户注册登录、JWT 鉴权、商品查询、订单创建、支付模拟和取消订单等接口。
- 使用 SQLAlchemy + SQLite 完成用户、商品、订单数据持久化，并在服务层实现库存扣减、库存恢复和订单状态流转规则。
- 使用数据库条件更新实现库存原子扣减和订单状态原子流转，避免超卖及并发取消重复恢复库存。
- 使用 FastAPI lifespan 初始化数据库，避免模块导入时产生建库副作用。
- 设计统一业务异常响应结构，覆盖未登录、商品不存在、库存不足、非法状态流转、越权访问等错误场景。
- 为核心业务接口和健康检查接口配套 Pytest 自动化测试与 GitHub Actions 持续集成，保证后端接口变更后的稳定性。

Interview talking points:

- FastAPI 路由层、服务层、模型层如何分工。
- JWT 鉴权如何接入受保护接口。
- 订单创建为什么要同时创建订单记录并扣减库存。
- 为什么扣库存要使用条件更新而不是只依赖内存对象扣减。
- 为什么取消订单要恢复库存，已支付订单不能取消。
