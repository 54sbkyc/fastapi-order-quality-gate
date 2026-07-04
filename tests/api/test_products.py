import allure
import pytest

from tests.schemas.product_schema import ProductResponse


@allure.feature("Product API")
@allure.story("Product query")
@allure.title("List seeded products successfully")
def test_list_products_success(client, seed_products):
    with allure.step("Request product list"):
        response = client.get("/api/products")

    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 2
    ProductResponse.model_validate(body[0])


@allure.feature("Product API")
@allure.story("Product query")
@allure.title("Get product detail successfully")
def test_get_product_detail_success(client, seed_products):
    product = seed_products[0]

    with allure.step("Request product detail"):
        response = client.get(f"/api/products/{product.id}")

    assert response.status_code == 200
    body = ProductResponse.model_validate(response.json())
    assert body.id == product.id
    assert body.name == product.name


@allure.feature("Product API")
@allure.story("Product errors")
@allure.title("Reject nonexistent product query")
@pytest.mark.parametrize(
    "product_id",
    [pytest.param(999999, id="large-id"), pytest.param(-1, id="negative-id")],
)
def test_get_nonexistent_product_returns_business_error(client, product_id):
    with allure.step("Request product detail with invalid product id"):
        response = client.get(f"/api/products/{product_id}")

    assert response.status_code == 404
    assert response.json()["code"] == "PRODUCT_NOT_FOUND"
