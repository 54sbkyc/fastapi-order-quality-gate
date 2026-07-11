from __future__ import annotations

from collections.abc import Generator

import allure
import httpx
import pytest

from tests.e2e.client import OrderApiClient
from tests.e2e.config import LiveApiSettings


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture()
def live_api(request: pytest.FixtureRequest) -> Generator[OrderApiClient, None, None]:
    settings = LiveApiSettings.from_env()
    api = OrderApiClient(
        settings.base_url,
        settings.timeout_seconds,
        trust_env=settings.trust_env,
    )
    try:
        try:
            health_response = api.health()
        except httpx.RequestError as exc:
            pytest.fail(
                f"无法连接测试环境 {settings.base_url}：{exc}。"
                "请运行 scripts/api-e2e.ps1 或设置 API_BASE_URL。"
            )
        if health_response.status_code != 200:
            pytest.fail(
                f"测试环境健康检查失败：HTTP {health_response.status_code}，"
                f"base_url={settings.base_url}"
            )

        yield api
    finally:
        report = getattr(request.node, "rep_call", None) or getattr(
            request.node, "rep_setup", None
        )
        if report is not None and report.failed:
            allure.attach(
                api.dump_history(),
                name="脱敏后的 HTTP 请求响应记录",
                attachment_type=allure.attachment_type.JSON,
            )
        api.close()
