import {
  BadgeCheck,
  Boxes,
  ClipboardCheck,
  LogIn,
  PackagePlus,
  RefreshCw,
  ShieldCheck,
  ShoppingCart,
  UserRound
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  cancelOrder,
  checkApiStatus,
  createOrder,
  fetchOrders,
  fetchProducts,
  fetchQualitySummary,
  loginUser,
  payOrder,
  registerUser
} from "./api";
import type { Order, OrderStatus, Product, QualitySummary } from "./types";

type Toast = {
  tone: "success" | "error" | "info";
  text: string;
};

const statusText: Record<OrderStatus, string> = {
  created: "待支付",
  paid: "已支付",
  cancelled: "已取消"
};

const categoryByProduct: Record<string, string> = {
  Keyboard: "键盘",
  Mouse: "鼠标",
  Monitor: "显示器"
};

function formatMoney(value: string | number) {
  return Number(value).toFixed(2);
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function App() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("testuser");
  const [password, setPassword] = useState("Passw0rd!");
  const [token, setToken] = useState(() => localStorage.getItem("order-demo-token") || "");
  const [products, setProducts] = useState<Product[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [orderFilter, setOrderFilter] = useState<"all" | OrderStatus>("all");
  const [selectedProductId, setSelectedProductId] = useState<number | "">("");
  const [quantity, setQuantity] = useState(1);
  const [apiOnline, setApiOnline] = useState(false);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [toast, setToast] = useState<Toast>({
    tone: "info",
    text: "等待接口状态检查"
  });
  const [busy, setBusy] = useState(false);
  const [qualitySummary, setQualitySummary] = useState<QualitySummary | null>(null);

  const productById = useMemo(() => {
    return new Map(products.map((product) => [product.id, product]));
  }, [products]);

  const visibleOrders = useMemo(() => {
    return orderFilter === "all"
      ? orders
      : orders.filter((order) => order.status === orderFilter);
  }, [orderFilter, orders]);

  async function refreshAll() {
    try {
      const ms = await checkApiStatus();
      setApiOnline(true);
      setResponseTime(ms);
    } catch (error) {
      setApiOnline(false);
      setResponseTime(null);
      setToast({ tone: "error", text: error instanceof Error ? error.message : "接口连接失败" });
      return;
    }

    try {
      const productList = await fetchProducts();
      setProducts(productList);
      setSelectedProductId((current) => current || productList[0]?.id || "");
      if (token) {
        setOrders(await fetchOrders(token));
      }
      setToast({ tone: "success", text: "接口数据已刷新" });
    } catch (error) {
      setToast({ tone: "error", text: error instanceof Error ? error.message : "数据刷新失败" });
    }

    try {
      setQualitySummary(await fetchQualitySummary());
    } catch {
      setQualitySummary(null);
    }
  }

  useEffect(() => {
    void refreshAll();
  }, [token]);

  async function handleAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    try {
      if (mode === "register") {
        await registerUser(username, password);
        setToast({ tone: "success", text: "注册成功，可以登录" });
        setMode("login");
      } else {
        const result = await loginUser(username, password);
        localStorage.setItem("order-demo-token", result.access_token);
        setToken(result.access_token);
        setToast({ tone: "success", text: "登录成功，JWT 已获取" });
      }
    } catch (error) {
      setToast({ tone: "error", text: error instanceof Error ? error.message : "认证失败" });
    } finally {
      setBusy(false);
    }
  }

  async function handleCreateOrder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      setToast({ tone: "error", text: "请先登录后再创建订单" });
      return;
    }
    if (!selectedProductId) {
      setToast({ tone: "error", text: "请选择商品" });
      return;
    }
    setBusy(true);
    try {
      const order = await createOrder(Number(selectedProductId), quantity, token);
      setToast({ tone: "success", text: `订单 ${order.id} 创建成功` });
      setProducts(await fetchProducts());
      setOrders(await fetchOrders(token));
    } catch (error) {
      setToast({ tone: "error", text: error instanceof Error ? error.message : "创建订单失败" });
    } finally {
      setBusy(false);
    }
  }

  async function handleOrderAction(orderId: number, action: "pay" | "cancel") {
    if (!token) {
      setToast({ tone: "error", text: "请先登录" });
      return;
    }
    setBusy(true);
    try {
      const updatedOrder = action === "pay" ? await payOrder(orderId, token) : await cancelOrder(orderId, token);
      setToast({
        tone: "success",
        text: action === "pay" ? `订单 ${updatedOrder.id} 已支付` : `订单 ${updatedOrder.id} 已取消`
      });
      setProducts(await fetchProducts());
      setOrders(await fetchOrders(token));
    } catch (error) {
      setToast({ tone: "error", text: error instanceof Error ? error.message : "订单操作失败" });
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    localStorage.removeItem("order-demo-token");
    setToken("");
    setOrders([]);
    setToast({ tone: "info", text: "已退出登录" });
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">
          <ShieldCheck size={24} />
        </div>
        <nav className="nav-list" aria-label="主导航">
          <a className="nav-item active" href="#auth">
            <LogIn size={19} />
            认证登录
          </a>
          <a className="nav-item" href="#products">
            <Boxes size={19} />
            商品列表
          </a>
          <a className="nav-item" href="#orders">
            <ShoppingCart size={19} />
            订单管理
          </a>
          <a className="nav-item" href="#quality">
            <ClipboardCheck size={19} />
            质量门禁
          </a>
        </nav>
        <button className="ghost-action" type="button" onClick={logout}>
          <UserRound size={18} />
          退出登录
        </button>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <h1>订单系统接口自动化测试项目</h1>
            <p>FastAPI + Pytest + CI Gate</p>
          </div>
          <div className="top-actions">
            <span className={`api-pill ${apiOnline ? "ok" : "down"}`}>
              <span />
              API 状态：{apiOnline ? "正常" : "离线"}
            </span>
            <span className="latency">响应时间：{responseTime ?? "--"}ms</span>
            <button className="icon-button" type="button" onClick={refreshAll} aria-label="刷新数据">
              <RefreshCw size={18} />
            </button>
            <span className="user-chip">测试同学</span>
          </div>
        </header>

        <section className="dashboard-grid">
          <section className="panel auth-panel" id="auth">
            <div className="panel-heading">
              <h2>认证登录 / 注册</h2>
            </div>
            <div className="segmented">
              <button className={mode === "login" ? "selected" : ""} onClick={() => setMode("login")} type="button">
                登录
              </button>
              <button className={mode === "register" ? "selected" : ""} onClick={() => setMode("register")} type="button">
                注册
              </button>
            </div>
            <form className="form-stack" onSubmit={handleAuth}>
              <label>
                用户名
                <input
                  autoComplete="username"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                />
              </label>
              <label>
                密码
                <input
                  type="password"
                  autoComplete={mode === "login" ? "current-password" : "new-password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                />
              </label>
              <button className="primary-button" disabled={busy} type="submit">
                <LogIn size={17} />
                {mode === "login" ? "登录" : "注册"}
              </button>
            </form>
            <div className={`toast ${toast.tone}`}>
              <BadgeCheck size={18} />
              <span>{toast.text}</span>
            </div>
          </section>

          <section className="panel products-panel" id="products">
            <div className="panel-heading">
              <h2>商品列表</h2>
              <button className="small-button" type="button" onClick={refreshAll}>
                <RefreshCw size={15} />
                刷新
              </button>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>商品ID</th>
                    <th>商品名称</th>
                    <th>类别</th>
                    <th>单价</th>
                    <th>库存</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((product) => (
                    <tr key={product.id}>
                      <td>{product.id}</td>
                      <td>{product.name}</td>
                      <td>{categoryByProduct[product.name] || "通用"}</td>
                      <td>{formatMoney(product.price)}</td>
                      <td>{product.stock}</td>
                      <td>
                        <span className={product.is_active ? "status-badge paid" : "status-badge cancelled"}>
                          {product.is_active ? "上架" : "下架"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="panel create-panel">
            <div className="panel-heading">
              <h2>创建订单</h2>
            </div>
            <form className="form-stack" onSubmit={handleCreateOrder}>
              <label>
                商品
                <select
                  value={selectedProductId}
                  onChange={(event) => setSelectedProductId(Number(event.target.value))}
                >
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name} / 库存 {product.stock}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                数量
                <div className="stepper">
                  <button type="button" onClick={() => setQuantity((value) => Math.max(1, value - 1))}>
                    -
                  </button>
                  <input
                    min={1}
                    max={100}
                    type="number"
                    value={quantity}
                    onChange={(event) => setQuantity(Number(event.target.value))}
                  />
                  <button type="button" onClick={() => setQuantity((value) => Math.min(100, value + 1))}>
                    +
                  </button>
                </div>
              </label>
              <button className="primary-button" disabled={busy || !token} type="submit">
                <PackagePlus size={17} />
                创建订单
              </button>
            </form>
          </section>
        </section>

        <section className="lower-grid">
          <section className="panel orders-panel" id="orders">
            <div className="panel-heading">
              <h2>订单管理</h2>
              <div className="filter-tabs">
                {([
                  ["all", "全部"],
                  ["created", "待支付"],
                  ["paid", "已支付"],
                  ["cancelled", "已取消"]
                ] as const).map(([value, label]) => (
                  <button
                    aria-pressed={orderFilter === value}
                    className={orderFilter === value ? "selected" : ""}
                    key={value}
                    onClick={() => setOrderFilter(value)}
                    type="button"
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>订单号</th>
                    <th>商品信息</th>
                    <th>数量</th>
                    <th>金额</th>
                    <th>创建时间</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleOrders.length === 0 ? (
                    <tr>
                      <td className="empty-row" colSpan={7}>
                        {orders.length === 0 ? "登录后可查看当前用户订单" : "当前筛选条件下暂无订单"}
                      </td>
                    </tr>
                  ) : (
                    visibleOrders.map((order) => {
                      const product = productById.get(order.product_id);
                      return (
                        <tr key={order.id}>
                          <td>ORD{String(order.id).padStart(6, "0")}</td>
                          <td>{product?.name || `商品 ${order.product_id}`}</td>
                          <td>{order.quantity}</td>
                          <td>{formatMoney(order.total_amount)}</td>
                          <td>{formatDate(order.created_at)}</td>
                          <td>
                            <span className={`status-badge ${order.status}`}>
                              {statusText[order.status]}
                            </span>
                          </td>
                          <td>
                            <div className="row-actions">
                              {order.status === "created" && (
                                <>
                                  <button disabled={busy} type="button" onClick={() => handleOrderAction(order.id, "pay")}>
                                    去支付
                                  </button>
                                  <button disabled={busy} type="button" onClick={() => handleOrderAction(order.id, "cancel")}>
                                    取消订单
                                  </button>
                                </>
                              )}
                              {order.status !== "created" && <span>已完成</span>}
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <aside className="panel quality-panel" id="quality">
            <div className="panel-heading">
              <h2>质量门禁</h2>
              <span className={`status-badge ${qualitySummary?.gate_status === "failed" ? "cancelled" : "paid"}`}>
                {qualitySummary ? (qualitySummary.gate_status === "passed" ? "已通过" : "未通过") : "加载中"}
              </span>
            </div>
            <Metric
              title="Pytest 结果"
              value={qualitySummary ? `${qualitySummary.api_tests.passed} / ${qualitySummary.api_tests.total}` : "--"}
              meta="通过用例"
            />
            <Metric
              title="行覆盖率"
              value={qualitySummary ? `${qualitySummary.coverage.line.toFixed(2)}%` : "--"}
              meta={`目标 ≥ ${qualitySummary?.coverage.threshold ?? 80}%`}
            />
            <Metric
              title="分支覆盖率"
              value={qualitySummary ? `${qualitySummary.coverage.branch.toFixed(2)}%` : "--"}
              meta="条件分支"
            />
            <Metric
              title="Ruff 代码检查"
              value={qualitySummary ? String(qualitySummary.lint_issues) : "--"}
              meta="个问题"
            />
          </aside>
        </section>
      </main>
    </div>
  );
}

function Metric({ title, value, meta }: { title: string; value: string; meta: string }) {
  return (
    <div className="metric-row">
      <div className="metric-icon">
        <ShieldCheck size={20} />
      </div>
      <div>
        <p>{title}</p>
        <strong>{value}</strong>
        <span>{meta}</span>
      </div>
    </div>
  );
}

export default App;
