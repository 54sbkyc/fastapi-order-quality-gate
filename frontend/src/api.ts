import type { ApiError, Order, Product, QualitySummary, TokenResponse } from "./types";

type RequestOptions = RequestInit & {
  token?: string;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  const response = await fetch(path, {
    ...options,
    headers
  });
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const error = payload as ApiError;
    throw new Error(error.message || `请求失败：${response.status}`);
  }

  return payload as T;
}

export async function checkApiStatus(): Promise<number> {
  const startedAt = performance.now();
  const response = await fetch("/api/health");
  if (!response.ok) {
    throw new Error(`健康检查失败：${response.status}`);
  }
  return Math.round(performance.now() - startedAt);
}

export async function fetchQualitySummary(): Promise<QualitySummary> {
  const response = await fetch("/quality-summary.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`质量快照加载失败：${response.status}`);
  }
  return response.json() as Promise<QualitySummary>;
}

export function registerUser(username: string, password: string) {
  return request<{ id: number; username: string }>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
}

export function loginUser(username: string, password: string) {
  return request<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
}

export function fetchProducts() {
  return request<Product[]>("/api/products");
}

export function fetchOrders(token: string) {
  return request<Order[]>("/api/orders", { token });
}

export function createOrder(productId: number, quantity: number, token: string) {
  return request<Order>("/api/orders", {
    method: "POST",
    token,
    body: JSON.stringify({ product_id: productId, quantity })
  });
}

export function payOrder(orderId: number, token: string) {
  return request<Order>(`/api/orders/${orderId}/pay`, {
    method: "POST",
    token
  });
}

export function cancelOrder(orderId: number, token: string) {
  return request<Order>(`/api/orders/${orderId}/cancel`, {
    method: "POST",
    token
  });
}
