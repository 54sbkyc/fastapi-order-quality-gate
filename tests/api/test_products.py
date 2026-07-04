from tests.schemas.product_schema import ProductResponse


def test_list_products_success(client, seed_products):
    response = client.get("/api/products")

    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 2
    ProductResponse.model_validate(body[0])


def test_get_product_detail_success(client, seed_products):
    product = seed_products[0]

    response = client.get(f"/api/products/{product.id}")

    assert response.status_code == 200
    body = ProductResponse.model_validate(response.json())
    assert body.id == product.id
    assert body.name == product.name


def test_get_nonexistent_product_returns_business_error(client):
    response = client.get("/api/products/999999")

    assert response.status_code == 404
    assert response.json()["code"] == "PRODUCT_NOT_FOUND"
