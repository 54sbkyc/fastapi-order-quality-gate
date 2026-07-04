# API Documentation

Base URL:

```text
http://127.0.0.1:8000
```

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
- `ORDER_NOT_FOUND`
- `FORBIDDEN_ORDER_ACCESS`
- `INVALID_ORDER_STATE`
- `VALIDATION_ERROR`

