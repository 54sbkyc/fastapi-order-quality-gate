from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_ui_smoke_files_are_present() -> None:
    required_paths = [
        "scripts/ui-smoke.ps1",
        "frontend/playwright.config.ts",
        "frontend/tests/ui-smoke.spec.ts",
    ]

    for relative_path in required_paths:
        assert (PROJECT_ROOT / relative_path).exists(), f"{relative_path} is missing"


def test_ui_smoke_is_wired_into_quality_gate() -> None:
    script = read_text("scripts/quality-gate.ps1")
    workflow = read_text(".github/workflows/api-quality-gate.yml")

    assert "[switch]$UiSmoke" in script
    assert "scripts\\ui-smoke.ps1" in script or "scripts/ui-smoke.ps1" in script
    assert "npm --prefix frontend run ui:smoke" in workflow
    assert "npx playwright install --with-deps chromium" in workflow


def test_ui_smoke_is_documented_for_interviews() -> None:
    readme = read_text("README.md")
    test_plan = read_text("docs/test-plan.md")
    interview_guide = read_text("docs/interview-guide.md")
    demo_script = read_text("docs/demo-script.md")

    assert ".\\scripts\\ui-smoke.ps1" in readme
    assert ".\\scripts\\quality-gate.ps1 -UiSmoke" in readme
    assert "UI smoke" in test_plan or "UI 冒烟" in test_plan
    assert "Playwright" in interview_guide
    assert "UI 冒烟" in demo_script or "UI smoke" in demo_script
