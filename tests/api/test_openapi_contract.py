import allure
import pytest

EXPECTED_OPERATIONS = {
    ("get", "/api/health"),
    ("post", "/api/auth/register"),
    ("post", "/api/auth/login"),
    ("get", "/api/products"),
    ("get", "/api/products/{product_id}"),
    ("post", "/api/orders"),
    ("get", "/api/orders"),
    ("get", "/api/orders/{order_id}"),
    ("post", "/api/orders/{order_id}/pay"),
    ("post", "/api/orders/{order_id}/cancel"),
}

EXPECTED_RESPONSE_CODES = {
    ("post", "/api/auth/register"): {"201", "409", "422"},
    ("post", "/api/auth/login"): {"200", "401", "422"},
    ("post", "/api/orders"): {"201", "401", "404", "409", "422"},
    ("get", "/api/orders/{order_id}"): {"200", "401", "403", "404"},
}


@allure.feature("OpenAPI Contract")
@allure.story("Route map")
@allure.title("OpenAPI exposes all core API operations")
def test_openapi_exposes_core_operations(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    actual_operations = {
        (method, path)
        for path, methods in schema["paths"].items()
        for method in methods
        if method in {"get", "post"}
    }

    assert EXPECTED_OPERATIONS <= actual_operations


@allure.feature("OpenAPI Contract")
@allure.story("Chinese documentation")
@allure.title("Core OpenAPI operations keep Chinese summary and description")
@pytest.mark.parametrize(("method", "path"), sorted(EXPECTED_OPERATIONS))
def test_core_operations_keep_chinese_docs(client, method, path):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    api_operation = schema["paths"][path][method]
    text = f"{api_operation.get('summary', '')} {api_operation.get('description', '')}"

    assert any("\u4e00" <= character <= "\u9fff" for character in text)


@allure.feature("OpenAPI Contract")
@allure.story("Response codes")
@allure.title("OpenAPI documents important business response codes")
@pytest.mark.parametrize(
    ("method", "path", "expected_codes"),
    [(method, path, codes) for (method, path), codes in EXPECTED_RESPONSE_CODES.items()],
)
def test_openapi_documents_important_response_codes(client, method, path, expected_codes):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    responses = schema["paths"][path][method]["responses"]

    assert expected_codes <= set(responses)


@allure.feature("OpenAPI Contract")
@allure.story("Error schema")
@allure.title("OpenAPI exposes reusable error response schema")
def test_openapi_exposes_error_response_schema(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    error_schema = schema["components"]["schemas"]["ErrorResponse"]

    assert set(error_schema["properties"]) >= {"code", "message"}
    assert set(error_schema["required"]) >= {"code", "message"}
