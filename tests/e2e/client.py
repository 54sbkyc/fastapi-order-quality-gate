from __future__ import annotations

import json
from time import perf_counter
from typing import Any

import httpx

SENSITIVE_FIELDS = {"access_token", "authorization", "password", "token"}
MAX_CAPTURE_LENGTH = 5_000


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "***" if str(key).lower() in SENSITIVE_FIELDS else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


class OrderApiClient:
    def __init__(self, base_url: str, timeout_seconds: float, *, trust_env: bool) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout_seconds,
            follow_redirects=False,
            trust_env=trust_env,
        )
        self.history: list[dict[str, Any]] = []

    def close(self) -> None:
        self._client.close()

    def dump_history(self) -> str:
        return json.dumps(self.history, ensure_ascii=False, indent=2)

    def request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> httpx.Response:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        started_at = perf_counter()
        try:
            response = self._client.request(
                method,
                path,
                headers=headers,
                json=json_body,
            )
        except httpx.RequestError as exc:
            self.history.append(
                {
                    "method": method,
                    "url": str(exc.request.url),
                    "request": _redact(json_body),
                    "error": str(exc),
                }
            )
            raise

        elapsed_ms = round((perf_counter() - started_at) * 1_000, 2)
        try:
            response_body: Any = response.json()
        except ValueError:
            response_body = response.text[:MAX_CAPTURE_LENGTH]

        self.history.append(
            {
                "method": method,
                "url": str(response.request.url),
                "request_headers": _redact(dict(response.request.headers)),
                "request_body": _redact(json_body),
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
                "response_body": _redact(response_body),
            }
        )
        return response

    def health(self) -> httpx.Response:
        return self.request("GET", "/api/health")

    def register(self, username: str, password: str) -> httpx.Response:
        return self.request(
            "POST",
            "/api/auth/register",
            json_body={"username": username, "password": password},
        )

    def login(self, username: str, password: str) -> httpx.Response:
        return self.request(
            "POST",
            "/api/auth/login",
            json_body={"username": username, "password": password},
        )

    def list_products(self) -> httpx.Response:
        return self.request("GET", "/api/products")

    def get_product(self, product_id: int) -> httpx.Response:
        return self.request("GET", f"/api/products/{product_id}")

    def create_order(self, token: str, product_id: int, quantity: int) -> httpx.Response:
        return self.request(
            "POST",
            "/api/orders",
            token=token,
            json_body={"product_id": product_id, "quantity": quantity},
        )

    def list_orders(self, token: str) -> httpx.Response:
        return self.request("GET", "/api/orders", token=token)

    def get_order(self, token: str, order_id: int) -> httpx.Response:
        return self.request("GET", f"/api/orders/{order_id}", token=token)

    def pay_order(self, token: str, order_id: int) -> httpx.Response:
        return self.request("POST", f"/api/orders/{order_id}/pay", token=token)

    def cancel_order(self, token: str, order_id: int) -> httpx.Response:
        return self.request("POST", f"/api/orders/{order_id}/cancel", token=token)
