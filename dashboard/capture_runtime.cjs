const { chromium } = require('playwright');
const fs = require('fs');

async function capture() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  console.log('Capturing Login...');
  await page.goto('http://127.0.0.1:5173/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'docs/implementation/screenshots/runtime_fix/01_login.png' });

  // Click login
  console.log('Logging in...');
  await page.click('button:has-text("Continue with GitHub")');
  await page.waitForTimeout(2000);

  console.log('Capturing Dashboard...');
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'docs/implementation/screenshots/runtime_fix/02_dashboard.png' });

  console.log('Capturing Repositories...');
  await page.goto('http://127.0.0.1:5173/repositories', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'docs/implementation/screenshots/runtime_fix/03_repositories.png' });

  console.log('Capturing Pull Requests...');
  await page.goto('http://127.0.0.1:5173/pull-requests', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'docs/implementation/screenshots/runtime_fix/04_pull_requests.png' });

  await browser.close();
  console.log('Done!');
}

capture().catch(console.error);
