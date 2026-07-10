export type Product = {
  id: number;
  name: string;
  price: string;
  stock: number;
  is_active: boolean;
};

export type OrderStatus = "created" | "paid" | "cancelled";

export type Order = {
  id: number;
  user_id: number;
  product_id: number;
  quantity: number;
  total_amount: string;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type ApiError = {
  code: string;
  message: string;
};

export type QualitySummary = {
  api_tests: {
    passed: number;
    failed: number;
    total: number;
  };
  coverage: {
    line: number;
    branch: number;
    threshold: number;
  };
  lint_issues: number;
  gate_status: "passed" | "failed";
};
