import { expect, test } from "@playwright/test";

test("中文演示后台可以完成注册、登录、下单、支付、筛选和质量指标校验", async ({ page }) => {
  const consoleErrors: string[] = [];
  const username = `ui_smoke_${Date.now()}`;
  const password = "Passw0rd!";

  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });
  page.on("pageerror", (error) => {
    consoleErrors.push(error.message);
  });

  await page.goto("/");
  await page.evaluate(() => window.localStorage.clear());
  await page.reload({ waitUntil: "domcontentloaded" });

  await expect(page).toHaveTitle(/订单系统接口自动化测试项目/);
  await expect(page.locator("vite-error-overlay, .vite-error-overlay, #webpack-dev-server-client-overlay")).toHaveCount(0);
  await expect(page.getByText("订单系统接口自动化测试项目")).toBeVisible();
  await expect(page.getByText("API 状态：正常")).toBeVisible();

  await expect(page.getByRole("cell", { name: "Keyboard" })).toBeVisible();
  await expect(page.getByRole("cell", { name: "Mouse" })).toBeVisible();
  await expect(page.getByRole("cell", { name: "Monitor" })).toBeVisible();

  await page.getByRole("button", { name: "注册" }).first().click();
  await page.getByLabel("用户名").fill(username);
  await page.getByLabel("密码").fill(password);
  await page.getByRole("button", { name: "注册" }).last().click();
  await expect(page.getByText("注册成功，可以登录")).toBeVisible();

  await page.getByRole("button", { name: "登录" }).last().click();

  const createOrderButton = page.getByRole("button", { name: /创建订单/ });
  await expect(createOrderButton).toBeEnabled();
  await createOrderButton.click();
  await expect(page.getByText(/订单 [0-9]+ 创建成功/)).toBeVisible();
  await expect(page.getByText(/ORD[0-9]{6}/).first()).toBeVisible();
  const orderNumber = await page.getByText(/ORD[0-9]{6}/).first().textContent();
  await page.getByRole("button", { name: "去支付" }).first().click();
  await expect(page.getByText(/订单 [0-9]+ 已支付/)).toBeVisible();

  await page.getByRole("button", { name: "已支付", exact: true }).click();
  await expect(page.getByText(orderNumber || "ORD")).toBeVisible();
  await page.getByRole("button", { name: "待支付", exact: true }).click();
  await expect(page.getByText("当前筛选条件下暂无订单")).toBeVisible();

  const qualityResponse = await page.request.get("/quality-summary.json");
  expect(qualityResponse.ok()).toBeTruthy();
  const quality = await qualityResponse.json();
  await expect(page.getByText("Pytest 结果")).toBeVisible();
  await expect(page.getByText(`${quality.api_tests.passed} / ${quality.api_tests.total}`)).toBeVisible();
  await expect(page.getByText(`${quality.coverage.line.toFixed(2)}%`)).toBeVisible();
  await expect(page.getByText(`${quality.coverage.branch.toFixed(2)}%`)).toBeVisible();
  expect(consoleErrors).toEqual([]);
});
