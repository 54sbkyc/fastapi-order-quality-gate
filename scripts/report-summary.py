from __future__ import annotations

import io
import json
from pathlib import Path
from xml.etree import ElementTree

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"
ALLURE_E2E_RESULTS_DIR = PROJECT_ROOT / "allure-e2e-results"
FRONTEND_ROOT = PROJECT_ROOT / "frontend"


def status_for(path: Path) -> str:
    return "已生成" if path.exists() else "未生成"


def coverage_summary() -> str:
    coverage_xml = PROJECT_ROOT / "coverage.xml"
    coverage_data = PROJECT_ROOT / ".coverage"

    if coverage_xml.exists():
        root = ElementTree.parse(coverage_xml).getroot()
        line_rate = float(root.attrib.get("line-rate", "0")) * 100
        branch_rate = float(root.attrib.get("branch-rate", "0")) * 100
        return f"{line_rate:.2f}% 行覆盖率，{branch_rate:.2f}% 分支覆盖率（coverage.xml）"

    if coverage_data.exists():
        try:
            from coverage import Coverage
        except ImportError:
            return "已发现 .coverage，但当前环境无法导入 coverage 包"

        output = io.StringIO()
        coverage = Coverage(data_file=str(coverage_data))
        coverage.load()
        total = coverage.report(file=output)
        return f"{total:.2f}%（.coverage）"

    return "未发现 coverage.xml 或 .coverage"


def allure_result_summary(result_dir: Path) -> tuple[int, int]:
    if not result_dir.exists():
        return 0, 0

    result_files = list(result_dir.glob("*-result.json"))
    passed = 0
    for path in result_files:
        result = json.loads(path.read_text(encoding="utf-8"))
        if result.get("status") == "passed":
            passed += 1
    return passed, len(result_files)


def build_summary() -> dict[str, str | int]:
    playwright_report = FRONTEND_ROOT / "playwright-report"
    playwright_results = FRONTEND_ROOT / "test-results"
    passed_tests, total_tests = allure_result_summary(ALLURE_RESULTS_DIR)
    passed_e2e_tests, total_e2e_tests = allure_result_summary(ALLURE_E2E_RESULTS_DIR)

    return {
        "coverage": coverage_summary(),
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "passed_e2e_tests": passed_e2e_tests,
        "total_e2e_tests": total_e2e_tests,
        "allure_environment": status_for(ALLURE_RESULTS_DIR / "environment.properties"),
        "allure_categories": status_for(ALLURE_RESULTS_DIR / "categories.json"),
        "frontend_dist": status_for(FRONTEND_ROOT / "dist" / "index.html"),
        "playwright_report": status_for(playwright_report),
        "playwright_results": status_for(playwright_results),
    }


def main() -> None:
    summary = build_summary()

    print("")
    print("质量报告摘要")
    print(f"- 覆盖率：{summary['coverage']}")
    print(f"- API 测试：{summary['passed_tests']} / {summary['total_tests']} 通过")
    print(
        f"- 真实 HTTP E2E：{summary['passed_e2e_tests']} / "
        f"{summary['total_e2e_tests']} 通过"
    )
    print(f"- Allure 环境信息：{summary['allure_environment']}")
    print(f"- Allure 失败分类：{summary['allure_categories']}")
    print(f"- 前端构建产物：{summary['frontend_dist']}（frontend/dist/index.html）")
    print(
        f"- Playwright HTML 报告：{summary['playwright_report']}"
        "（frontend/playwright-report/index.html）"
    )
    print(
        f"- Playwright trace/截图目录：{summary['playwright_results']}"
        "（frontend/test-results）"
    )
    print("")
    print(
        "CI 产物建议查看：allure-results、allure-e2e-results、"
        "coverage-xml、frontend-dist。"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
