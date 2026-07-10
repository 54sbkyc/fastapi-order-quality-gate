from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LiveApiSettings:
    base_url: str
    timeout_seconds: float
    trust_env: bool

    @classmethod
    def from_env(cls) -> LiveApiSettings:
        raw_timeout = os.getenv("API_TIMEOUT_SECONDS", "10")
        try:
            timeout_seconds = float(raw_timeout)
        except ValueError as exc:
            raise ValueError("API_TIMEOUT_SECONDS 必须是数字") from exc
        if timeout_seconds <= 0:
            raise ValueError("API_TIMEOUT_SECONDS 必须大于 0")

        base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8001").strip().rstrip("/")
        if not base_url:
            raise ValueError("API_BASE_URL 不能为空")

        raw_trust_env = os.getenv("API_TRUST_ENV", "false").strip().lower()
        if raw_trust_env not in {"true", "false"}:
            raise ValueError("API_TRUST_ENV 只能是 true 或 false")
        return cls(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            trust_env=raw_trust_env == "true",
        )
