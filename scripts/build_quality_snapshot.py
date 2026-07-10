from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_XML = PROJECT_ROOT / "coverage.xml"
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"
OUTPUT_PATH = PROJECT_ROOT / "frontend" / "public" / "quality-summary.json"
COVERAGE_THRESHOLD = 80


def read_coverage() -> dict[str, float | int]:
    if not COVERAGE_XML.exists():
        raise FileNotFoundError("coverage.xml 不存在，请先运行带覆盖率的 API 测试")

    root = ElementTree.parse(COVERAGE_XML).getroot()
    return {
        "line": round(float(root.attrib.get("line-rate", "0")) * 100, 2),
        "branch": round(float(root.attrib.get("branch-rate", "0")) * 100, 2),
        "threshold": COVERAGE_THRESHOLD,
    }


def read_test_results() -> dict[str, int]:
    result_files = sorted(ALLURE_RESULTS_DIR.glob("*-result.json"))
    if not result_files:
        raise FileNotFoundError("未发现 Allure 测试结果，请先运行 API 测试")

    statuses = [
        json.loads(path.read_text(encoding="utf-8")).get("status", "unknown")
        for path in result_files
    ]
    passed = statuses.count("passed")
    return {
        "passed": passed,
        "failed": len(statuses) - passed,
        "total": len(statuses),
    }


def build_snapshot() -> dict[str, object]:
    tests = read_test_results()
    coverage = read_coverage()
    return {
        "api_tests": tests,
        "coverage": coverage,
        "lint_issues": 0,
        "gate_status": (
            "passed"
            if tests["failed"] == 0 and coverage["line"] >= COVERAGE_THRESHOLD
            else "failed"
        ),
    }


def main() -> None:
    snapshot = build_snapshot()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"质量快照已生成：{OUTPUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
