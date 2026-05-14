import { test, expect } from "@playwright/test";

test("new user can browse, book and cancel a reservation", async ({ page }) => {
  await page.goto(process.env.NEKOCAFE_BASE_URL ?? "http://localhost:8080");
  await page.getByRole("link", { name: /门店|Stores/ }).click();
  await page.getByRole("button", { name: /预约|Book/ }).click();
  await page.getByLabel(/手机号|Phone/).fill("13800000001");
  await page.getByLabel(/宠物|Pet/).fill("橘猫");
  await page.getByRole("button", { name: /提交|Submit/ }).click();
  await expect(page.getByText(/预约成功|confirmed/i)).toBeVisible();
  await page.getByRole("button", { name: /取消|Cancel/ }).click();
  await expect(page.getByText(/已取消|cancelled/i)).toBeVisible();
});
