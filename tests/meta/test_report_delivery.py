import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_report_summary_script_is_present_and_wired() -> None:
    assert (PROJECT_ROOT / "scripts/report-summary.py").exists()
    assert (PROJECT_ROOT / "scripts/build_quality_snapshot.py").exists()
    assert (PROJECT_ROOT / "frontend/public/quality-summary.json").exists()

    quality_gate = read_text("scripts/quality-gate.ps1")
    assert "scripts/report-summary.py" in quality_gate
    assert "scripts/build_quality_snapshot.py" in quality_gate
    assert "清理旧测试报告" in quality_gate
    assert "--cov-report=xml:coverage.xml" in quality_gate


def test_frontend_quality_snapshot_has_real_gate_metrics() -> None:
    snapshot = json.loads(read_text("frontend/public/quality-summary.json"))
    app_source = read_text("frontend/src/App.tsx")

    assert snapshot["api_tests"]["passed"] == snapshot["api_tests"]["total"]
    assert snapshot["api_tests"]["total"] > 0
    assert snapshot["coverage"]["line"] >= snapshot["coverage"]["threshold"]
    assert snapshot["coverage"]["branch"] > 0
    assert snapshot["gate_status"] == "passed"
    assert "fetchQualitySummary" in app_source
    assert 'value="46 / 46"' not in app_source


def test_ci_uploads_quality_evidence_artifacts() -> None:
    workflow = read_text(".github/workflows/api-quality-gate.yml")

    assert "scripts/write_allure_metadata.py" in workflow
    assert "scripts/build_quality_snapshot.py" in workflow
    assert "--cov-report=xml:coverage.xml" in workflow
    assert "name: allure-results" in workflow
    assert "name: allure-e2e-results" in workflow
    assert "name: coverage-xml" in workflow
    assert "name: frontend-dist" in workflow
    assert "name: playwright-report" in workflow
    assert "if-no-files-found: warn" in workflow
    assert "python -m pytest tests/e2e -m e2e" in workflow


def test_successful_main_quality_gate_publishes_trusted_allure_report() -> None:
    workflow = read_text(".github/workflows/publish-allure-report.yml")

    assert 'workflows: ["Quality Gate"]' in workflow
    assert "github.event.workflow_run.conclusion == 'success'" in workflow
    assert "github.event.workflow_run.event == 'push'" in workflow
    assert "github.event.workflow_run.head_branch == 'main'" in workflow
    assert "actions: read" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow
    assert "actions/download-artifact@v8" in workflow
    assert "allure-results" in workflow
    assert "allure-e2e-results" in workflow
    assert "allure-commandline@2.43.0" in workflow
    assert "actions/configure-pages@v6" in workflow
    assert "actions/upload-pages-artifact@v5" in workflow
    assert "actions/deploy-pages@v5" in workflow
    assert "test -s allure-report/index.html" in workflow


def test_report_delivery_is_documented() -> None:
    readme = read_text("README.md")
    test_plan = read_text("docs/test-plan.md")
    interview_guide = read_text("docs/interview-guide.md")
    demo_script = read_text("docs/demo-script.md")
    resume_points = read_text("docs/resume-points.md")

    combined = "\n".join([readme, test_plan, interview_guide, demo_script, resume_points])
    assert "coverage.xml" in combined
    assert "CI artifacts" in combined or "CI 产物" in combined
    assert "scripts/report-summary.py" in combined
    assert "https://54sbkyc.github.io/fastapi-order-quality-gate/" in combined
