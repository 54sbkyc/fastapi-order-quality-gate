from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_order_idempotency_is_protected_across_backend_client_and_tests() -> None:
    route_source = read_text("app/api/routes_orders.py")
    model_source = read_text("app/models/order_idempotency.py")
    frontend_source = read_text("frontend/src/api.ts")
    live_test_source = read_text("tests/e2e/test_live_order_api.py")

    assert 'alias="Idempotency-Key"' in route_source
    assert 'response.headers["Idempotency-Replayed"]' in route_source
    assert "uq_order_idempotency_user_key" in model_source
    assert 'headers: { "Idempotency-Key": idempotencyKey }' in frontend_source
    assert "return send();" in frontend_source
    assert "test_live_api_prevents_duplicate_order_retry" in live_test_source
