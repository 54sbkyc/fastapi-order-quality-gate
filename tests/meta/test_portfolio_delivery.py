from pathlib import Path

REQUIRED_FILES = [
    Path("scripts/demo-start.ps1"),
    Path("scripts/quality-gate.ps1"),
    Path("scripts/api-e2e.ps1"),
    Path("scripts/demo-reset.ps1"),
    Path(".env.example"),
    Path("docs/demo-script.md"),
]


def test_portfolio_delivery_assets_exist():
    missing = [str(path) for path in REQUIRED_FILES if not path.exists()]

    assert missing == []


def test_readme_references_portfolio_delivery_assets():
    readme = Path("README.md").read_text(encoding="utf-8")

    for text in [
        "scripts/demo-start.ps1",
        "scripts/quality-gate.ps1",
        "scripts/api-e2e.ps1",
        "scripts/demo-reset.ps1",
        "docs/demo-script.md",
    ]:
        assert text in readme


def test_docker_compose_uses_documented_api_port():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert '"8001:8001"' in compose
    assert "--port 8001" in compose
