const { chromium } = require("playwright-core");

const EDGE =
  process.env.EDGE_PATH ||
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

async function waitForText(page, selector, text) {
  await page.waitForFunction(
    ({ selector, text }) => {
      const el = document.querySelector(selector);
      return el && el.textContent && el.textContent.includes(text);
    },
    { selector, text },
    { timeout: 15000 },
  );
}

(async () => {
  const browser = await chromium.launch({
    executablePath: EDGE,
    headless: true,
  });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  const base = process.env.YUME_URL || "http://127.0.0.1:8787";

  await page.goto(`${base}/#/`, { waitUntil: "networkidle" });
  await waitForText(page, ".brand-name", "yumeVNGame");
  await waitForText(page, ".hero h1", "把世界写成一封");
  console.log("PASS  home");

  await page.goto(`${base}/#/play/demo-mistharbor`, {
    waitUntil: "networkidle",
  });
  await page.waitForSelector(".dialogue", { timeout: 15000 });
  await waitForText(page, ".vn-title strong", "雨夜来信");
  console.log("PASS  player loads");

  await page.locator(".dialogue").click();
  await page.waitForTimeout(350);
  await page.locator(".dialogue").click();
  await waitForText(page, ".vn-title strong", "没有署名的信");
  console.log("PASS  advance");

  await page.locator(".dialogue").click();
  await page.waitForTimeout(350);
  await page.locator(".dialogue").click();
  await page.waitForSelector(".choice-btn", { timeout: 15000 });
  console.log("PASS  choices visible");

  await page.locator(".choice-btn").first().click();
  await waitForText(page, ".vn-title strong", "旧港");
  console.log("PASS  choose branch");

  await page.goto(`${base}/#/gallery/demo-mistharbor`, {
    waitUntil: "networkidle",
  });
  await page.waitForSelector(".gallery-grid", { timeout: 15000 });
  const cards = await page.locator(".gallery-card").count();
  if (cards < 10) throw new Error(`gallery cards too few: ${cards}`);
  console.log("PASS  gallery");

  await page.goto(`${base}/#/settings`, { waitUntil: "networkidle" });
  await waitForText(page, ".settings-page h1", "设置");
  await waitForText(page, ".plugin-panel h2", "外部数据集与插件包");
  const pluginCards = await page.locator(".plugin-card").count();
  if (pluginCards < 1) throw new Error(`plugin cards too few: ${pluginCards}`);
  console.log("PASS  settings / plugins");

  await browser.close();
  console.log("ALL UI SMOKE TESTS PASSED");
})().catch((error) => {
  console.error(error);
  process.exit(1);
});

