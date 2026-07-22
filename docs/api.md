# API Documentation

Base URL:

```text
http://127.0.0.1:8001
```

Swagger UI:

```text
http://127.0.0.1:8001/docs
```

## System

### Health Check

`GET /api/health`

Response:

```json
{
  "status": "ok",
  "service": "订单系统接口自动化测试项目",
  "version": "0.1.0"
}
```

Use this endpoint for local demo status checks, frontend connectivity checks, and lightweight smoke verification.

## Authentication

### Register

`POST /api/auth/register`

Request:

```json
{
  "username": "alice",
  "password": "Passw0rd!"
}
```

Response:

```json
{
  "id": 1,
  "username": "alice"
}
```

### Login

`POST /api/auth/login`

Request:

```json
{
  "username": "alice",
  "password": "Passw0rd!"
}
```

Response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

Use the token in protected requests:

```http
Authorization: Bearer <jwt-token>
```

## Products

### List Products

`GET /api/products`

Returns active and inactive products currently stored in the system.

### Get Product Detail

`GET /api/products/{product_id}`

Returns `PRODUCT_NOT_FOUND` when the product does not exist.

## Orders

### Create Order

`POST /api/orders`

Optional request header:

```http
Idempotency-Key: order-checkout-20260722-0001
```

Request:

```json
{
  "product_id": 1,
  "quantity": 2
}
```

Rules:

- Requires login.
- Product must exist.
- Product must be active.
- Stock must be enough.
- Creating an order decreases stock.
- `Idempotency-Key` must be 8-64 characters and can contain letters, numbers, `.`, `_`, `:`, `-`.
- The first request returns `201` and `Idempotency-Replayed: false`.
- Retrying the same user, key, and payload returns the original order with `200` and `Idempotency-Replayed: true`; stock is not deducted again.
- Reusing the same key with a different product or quantity returns `409 IDEMPOTENCY_KEY_CONFLICT`.
- Idempotency keys are scoped by user, so two users may use the same key independently.

### List My Orders

`GET /api/orders`

Only returns orders owned by the current user.

### Get Order Detail

`GET /api/orders/{order_id}`

Users cannot access another user's order.

### Pay Order

`POST /api/orders/{order_id}/pay`

Only `created` orders can be paid.

### Cancel Order

`POST /api/orders/{order_id}/cancel`

Only `created` orders can be cancelled. Cancelling restores product stock.

## Error Format

All business errors use the same structure:

```json
{
  "code": "INSUFFICIENT_STOCK",
  "message": "Insufficient product stock"
}
```

Common business codes:

- `NOT_AUTHENTICATED`
- `INVALID_TOKEN`
- `INVALID_CREDENTIALS`
- `PRODUCT_NOT_FOUND`
- `PRODUCT_INACTIVE`
- `INSUFFICIENT_STOCK`
- `IDEMPOTENCY_KEY_CONFLICT`
- `ORDER_NOT_FOUND`
- `FORBIDDEN_ORDER_ACCESS`
- `INVALID_ORDER_STATE`
- `VALIDATION_ERROR`
