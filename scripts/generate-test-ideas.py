from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.main import create_app

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"


@dataclass(frozen=True)
class DeepSeekConfig:
    api_key: str
    base_url: str
    model: str


def load_config() -> DeepSeekConfig:
    return DeepSeekConfig(
        api_key=os.getenv("DEEPSEEK_API_KEY", "").strip(),
        base_url=os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        model=os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL,
    )


def build_route_summary() -> list[dict[str, object]]:
    schema = create_app(init_db=False).openapi()
    summary: list[dict[str, object]] = []
    for path, methods in sorted(schema["paths"].items()):
        for method, operation in sorted(methods.items()):
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            summary.append(
                {
                    "method": method.upper(),
                    "path": path,
                    "summary": operation.get("summary", ""),
                    "description": operation.get("description", ""),
                    "responses": sorted(operation.get("responses", {}).keys()),
                }
            )
    return summary


def build_prompt(route_summary: list[dict[str, object]]) -> str:
    intro = (
        "你是一名资深自动化测试工程师。请根据下面的 FastAPI OpenAPI 路由摘要，"
        "提出 10 条高价值 API 自动化测试建议。"
    )
    return f"""{intro}

要求：
1. 用中文输出。
2. 优先考虑业务风险、负向场景、边界值、权限、状态流转、库存一致性和接口契约。
3. 不要只写“测试接口是否成功”，要说明测试目的、步骤和关键断言。
4. 输出 Markdown 表格，列为：模块、测试点、步骤、关键断言、优先级。
5. 已经存在的测试可作为参考，但请优先提出能提升质量的补充测试。

OpenAPI 路由摘要：
```json
{json.dumps(route_summary, ensure_ascii=False, indent=2)}
```
"""


def call_deepseek(config: DeepSeekConfig, prompt: str, timeout_seconds: int) -> str:
    payload = {
        "model": config.model,
        "messages": [
            {
                "role": "system",
                "content": "你是专注接口自动化测试设计的助手，只输出可落地的测试建议。",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "stream": False,
    }
    request = Request(
        f"{config.base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API 返回 HTTP {error.code}: {error_body}") from error
    except URLError as error:
        raise RuntimeError(f"无法连接 DeepSeek API: {error.reason}") from error

    result = json.loads(response_body)
    return result["choices"][0]["message"]["content"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate API automation test ideas from local OpenAPI schema with DeepSeek."
    )
    parser.add_argument(
        "--prompt-only",
        action="store_true",
        help="Only print the generated prompt and skip the DeepSeek API call.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="DeepSeek API timeout in seconds when DEEPSEEK_API_KEY is set.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    prompt = build_prompt(build_route_summary())

    print("DeepSeek 测试用例建议生成器")
    print(f"- Base URL: {config.base_url}")
    print(f"- Model: {config.model}")
    print("- API Key: " + ("已配置" if config.api_key else "未配置"))

    if args.prompt_only or not config.api_key:
        print("")
        print("未检测到 DEEPSEEK_API_KEY，已进入 prompt-only 模式。")
        print("把下面的 prompt 复制到 DeepSeek，或在本地设置 DEEPSEEK_API_KEY 后重新运行。")
        print("")
        print(prompt)
        return

    print("")
    print("正在调用 DeepSeek API 生成测试建议...")
    print(call_deepseek(config, prompt, args.timeout))


if __name__ == "__main__":
    main()
