from pathlib import Path

REQUIRED_FILES = [
    Path("Dockerfile"),
    Path(".dockerignore"),
    Path("render.yaml"),
    Path(".github/workflows/remote-api-smoke.yml"),
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
    assert "order-data:/data" in compose


def test_public_deployment_uses_ci_gated_container_and_health_check():
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    blueprint = Path("render.yaml").read_text(encoding="utf-8")
    workflow = Path(".github/workflows/remote-api-smoke.yml").read_text(encoding="utf-8")
    quality_gate = Path(".github/workflows/api-quality-gate.yml").read_text(
        encoding="utf-8"
    )

    assert "FROM node:22-slim AS frontend-build" in dockerfile
    assert 'USER app' in dockerfile
    assert 'runtime: docker' in blueprint
    assert 'autoDeployTrigger: checksPass' in blueprint
    assert 'healthCheckPath: /api/health' in blueprint
    assert 'API_BASE_URL: ${{ inputs.api_base_url || vars.PUBLIC_API_BASE_URL }}' in workflow
    assert 'cron: "17 2 * * 1"' in workflow
    assert 'actions/checkout@v6' in workflow
    assert 'actions/setup-python@v6' in workflow
    assert 'actions/upload-artifact@v6' in workflow
    assert 'python -m pytest tests/e2e -m smoke' in workflow
    assert 'docker build --tag order-quality-gate:ci .' in quality_gate
    assert 'order-quality-gate:ci)' in quality_gate
    assert 'actions/setup-node@v6' in quality_gate


def test_containerized_app_serves_the_built_frontend():
    app_source = Path("app/main.py").read_text(encoding="utf-8")

    assert 'StaticFiles(directory=FRONTEND_DIST, html=True)' in app_source
