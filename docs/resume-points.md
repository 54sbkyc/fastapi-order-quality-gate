# Resume Points

## Automation Testing Version

Project:

`基于 FastAPI + Pytest 的订单系统接口自动化测试与 CI 质量门禁`

Resume bullets:

- 基于 Pytest 搭建订单系统 API 自动化测试框架，覆盖登录、商品查询、订单创建、支付、取消等核心接口。
- 使用 fixture 管理测试用户、JWT token、商品种子数据和隔离数据库，保证用例可重复执行且互不依赖。
- 通过参数化思路覆盖正常、异常和状态流转场景，并结合 Pydantic 响应结构校验与 SQLAlchemy 数据库断言验证接口真实落库结果。
- 集成 Allure 测试报告与 GitHub Actions 质量门禁，实现提交后自动执行 lint 和接口测试，核心用例失败时阻断流水线。

Interview talking points:

- 为什么接口测试不只断言状态码，还要断言业务错误码和数据库状态。
- 如何用 pytest fixture 降低登录、测试数据准备和清理的重复成本。
- 如何设计订单状态流转测试，比如 `created -> paid`、`created -> cancelled`、重复支付、已支付取消。
- CI 质量门禁如何帮助团队在代码合并前发现接口回归。

## Backend Development Version

Project:

`FastAPI 订单管理系统与自动化质量保障`

Resume bullets:

- 基于 FastAPI 开发小型订单管理系统，实现用户注册登录、JWT 鉴权、商品查询、订单创建、支付模拟和取消订单等接口。
- 使用 SQLAlchemy + SQLite 完成用户、商品、订单数据持久化，并在服务层实现库存扣减、库存恢复和订单状态流转规则。
- 设计统一业务异常响应结构，覆盖未登录、商品不存在、库存不足、非法状态流转、越权访问等错误场景。
- 为核心业务接口配套 Pytest 自动化测试与 GitHub Actions 持续集成，保证后端接口变更后的稳定性。

Interview talking points:

- FastAPI 路由层、服务层、模型层如何分工。
- JWT 鉴权如何接入受保护接口。
- 订单创建为什么要同时创建订单记录并扣减库存。
- 为什么取消订单要恢复库存，已支付订单不能取消。

