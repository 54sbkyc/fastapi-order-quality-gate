import allure

from app.core.config import Settings, settings


@allure.feature("System API")
@allure.story("Health check")
@allure.title("Health check returns service metadata")
def test_health_check_returns_service_metadata(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "订单系统接口自动化测试项目",
        "version": "0.1.0",
        "commit": "local",
    }


@allure.feature("System API")
@allure.story("Deployment attestation")
@allure.title("Health check exposes the running deployment commit")
def test_health_check_exposes_running_commit(client, monkeypatch):
    monkeypatch.setattr(settings, "render_git_commit", "abc123")

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["commit"] == "abc123"


@allure.feature("System API")
@allure.story("Deployment attestation")
@allure.title("Settings read the Render deployment commit from the environment")
def test_settings_read_render_commit(monkeypatch):
    monkeypatch.setenv("RENDER_GIT_COMMIT", "def456")

    runtime_settings = Settings(_env_file=None)

    assert runtime_settings.render_git_commit == "def456"
