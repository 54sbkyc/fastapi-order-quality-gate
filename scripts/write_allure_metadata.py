from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"

ENVIRONMENT = {
    "Project": "FastAPI Order Quality Gate",
    "Role Target": "Automation Testing Internship",
    "Backend": "FastAPI",
    "Test Framework": "Pytest + Allure",
    "Test Layers": "In-process integration + live HTTP E2E",
    "Database": "SQLite",
    "Coverage Gate": "80%",
    "Frontend": "React + Vite",
}

CATEGORIES = [
    {
        "name": "Authentication or Authorization Failure",
        "matchedStatuses": ["failed", "broken"],
        "messageRegex": (
            ".*(NOT_AUTHENTICATED|INVALID_TOKEN|INVALID_CREDENTIALS|USER_ALREADY_EXISTS).*"
        ),
    },
    {
        "name": "Validation Failure",
        "matchedStatuses": ["failed", "broken"],
        "messageRegex": ".*(VALIDATION_ERROR|422).*",
    },
    {
        "name": "Business Rule Failure",
        "matchedStatuses": ["failed", "broken"],
        "messageRegex": ".*(INSUFFICIENT_STOCK|INVALID_ORDER_STATE|FORBIDDEN_ORDER_ACCESS).*",
    },
    {
        "name": "Unexpected Error",
        "matchedStatuses": ["broken"],
        "traceRegex": ".*",
    },
]


def write_environment_file() -> None:
    lines = [f"{key}={value}" for key, value in ENVIRONMENT.items()]
    (ALLURE_RESULTS_DIR / "environment.properties").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_categories_file() -> None:
    (ALLURE_RESULTS_DIR / "categories.json").write_text(
        json.dumps(CATEGORIES, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    ALLURE_RESULTS_DIR.mkdir(exist_ok=True)
    write_environment_file()
    write_categories_file()
    print("Allure metadata generated in allure-results/")


if __name__ == "__main__":
    main()
