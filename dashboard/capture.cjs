const { chromium, devices } = require('playwright');
const fs = require('fs');

async function capture() {
  const outDir = '../docs/implementation/screenshots/phase14';
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });

  async function takeScreenshots(viewport, prefix) {
    const context = await browser.newContext({
      viewport: viewport
    });

    const page = await context.newPage();

    // Set auth cookie
    await context.addCookies([{
      name: 'codegate_session',
      value: 'playwright-test-token-123456789',
      domain: '127.0.0.1',
      path: '/',
      httpOnly: true,
      secure: false,
      sameSite: 'Lax'
    }]);

    const baseUrl = 'http://127.0.0.1:5173';

    // 01_overview
    await page.goto(`${baseUrl}/`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${outDir}/01_overview${prefix}.png`, fullPage: true });

    // 02_repositories
    await page.goto(`${baseUrl}/repositories`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${outDir}/02_repositories${prefix}.png`, fullPage: true });

    // 03_pull_requests
    await page.goto(`${baseUrl}/pull-requests`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${outDir}/03_pull_requests${prefix}.png`, fullPage: true });

    // 04_pr_detail
    await page.goto(`${baseUrl}/pull-requests/101`);
    await page.waitForTimeout(3000); // Give time for charts to render
    await page.screenshot({ path: `${outDir}/04_pr_detail${prefix}.png`, fullPage: true });

    // 05_integrations
    await page.goto(`${baseUrl}/integrations`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${outDir}/05_integrations${prefix}.png`, fullPage: true });

    // 06_members
    await page.goto(`${baseUrl}/settings/members`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${outDir}/06_members${prefix}.png`, fullPage: true });

    // 07_login (clear cookies first)
    await context.clearCookies();
    await page.goto(`${baseUrl}/login`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${outDir}/07_login${prefix}.png`, fullPage: true });

    await context.close();
  }

  console.log("Capturing desktop (1440x900)...");
  // The user asked for specific filenames without prefix for desktop: docs/implementation/screenshots/phase14/01_overview.png
  await takeScreenshots({ width: 1440, height: 900 }, '');

  console.log("Capturing mobile (390x844)...");
  await takeScreenshots({ width: 390, height: 844 }, '_mobile');

  await browser.close();
  console.log("Capture complete.");
}

capture().catch(err => {
  console.error("Capture failed:", err);
  process.exit(1);
});
