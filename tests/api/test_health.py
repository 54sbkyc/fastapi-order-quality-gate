import allure


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
    }
