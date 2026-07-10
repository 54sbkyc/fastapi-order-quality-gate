from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_deepseek_helper_script_and_env_are_documented() -> None:
    assert (PROJECT_ROOT / "scripts/generate-test-ideas.py").exists()

    env_example = read_text(".env.example")
    assert "DEEPSEEK_API_KEY=" in env_example
    assert "DEEPSEEK_BASE_URL=https://api.deepseek.com" in env_example
    assert "DEEPSEEK_MODEL=deepseek-v4-flash" in env_example
    assert "sk-" not in env_example


def test_deepseek_helper_is_documented_but_not_required_by_quality_gate() -> None:
    readme = read_text("README.md")
    interview_guide = read_text("docs/interview-guide.md")
    quality_gate = read_text("scripts/quality-gate.ps1")

    assert "scripts/generate-test-ideas.py" in readme
    assert "DeepSeek" in readme
    assert "DeepSeek" in interview_guide
    assert "DEEPSEEK_API_KEY" not in quality_gate
