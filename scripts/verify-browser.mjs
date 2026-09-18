// Run with ARXIV_PLAYWRIGHT pointing to an existing Playwright package directory.
import { createServer } from 'node:http';
import { readFile, mkdir } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import path from 'node:path';
import assert from 'node:assert/strict';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.ARXIV_PLAYWRIGHT || 'playwright');
const root = path.resolve('site');
const fixture = execFileSync('python3', ['-c', `
import importlib.util
s=importlib.util.spec_from_file_location('p','scripts/publish-day.py'); p=importlib.util.module_from_spec(s); s.loader.exec_module(p)
entries=[dict(date='2026-09-17',title='Test Paper '+str(i),title_zh='测试论文 '+str(i),arxiv_id=aid,direction=d,tags=[d],summary='用于验证阅读状态的测试卡片',path='2026-09-17/',slides='slides.html') for i,(aid,d) in enumerate([('2609.00001v2','AI'),('2609.00002v1','金融'),('2609.00003v1','AI')])]
print(p.render_home_page(entries))
`], { encoding: 'utf8' });
const server = createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  if (url.pathname === '/fixture/') { res.setHeader('content-type', 'text/html;charset=utf-8'); res.end(fixture); return; }
  let requested = decodeURIComponent(url.pathname.replace(/^\/fixture\//, '/'));
  if (requested.endsWith('/')) requested += 'index.html';
  const filename = path.resolve(root, '.' + requested);
  if (!filename.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return; }
  try {
    const type = { '.js': 'text/javascript', '.css': 'text/css', '.html': 'text/html', '.json': 'application/json' }[path.extname(filename)] || 'text/plain';
    res.setHeader('content-type', type + ';charset=utf-8');
    res.end(await readFile(filename));
  } catch (_) { res.writeHead(404); res.end(); }
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
let browser;
try {
  browser = await chromium.launch({ headless: true, executablePath: process.env.ARXIV_CHROMIUM });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto(base + '/fixture/');
  await page.locator('[data-read-filter="unread"]').click();
  assert.equal(await page.locator('.paper:visible').count(), 3);
  await page.locator('[data-read-toggle]').first().click();
  assert.equal(await page.locator('.paper:visible').count(), 2);
  assert.equal(await page.evaluate(() => localStorage.getItem('arxiv-daily:read:v1:2609.00001')), '1');
  await page.reload();
  assert.equal(await page.locator('.paper:visible').count(), 2);
  await page.locator('[data-read-filter="read"]').click();
  assert.equal(await page.locator('.paper:visible').count(), 1);
  await page.locator('[data-tag="金融"]').click();
  assert.equal(await page.locator('.paper:visible').count(), 0);
  assert.equal(await page.locator('#no-results').isVisible(), true);
  await page.goBack();
  assert.equal(await page.locator('.paper:visible').count(), 1);
  const second = await context.newPage();
  await second.goto(base + '/fixture/?status=read');
  await second.locator('[data-read-toggle]').first().click();
  await page.waitForFunction(() => document.querySelectorAll('.paper:not([hidden])').length === 0);
  await page.goto(base + '/fixture/?tag=unknown&status=unknown');
  assert.equal(await page.locator('.paper:visible').count(), 3);
  await page.evaluate(() => localStorage.setItem('arxiv-daily:read:v1:2609.00001', '{corrupt'));
  await page.reload();
  assert.equal(await page.locator('[data-read-toggle]').first().getAttribute('aria-pressed'), 'false');
  await page.evaluate(() => {
    Storage.prototype.setItem = () => { throw new Error('temporary quota failure'); };
  });
  await page.locator('[data-read-toggle="2609.00002v1"]').click();
  assert.equal(await page.locator('[data-read-toggle="2609.00002v1"]').getAttribute('aria-pressed'), 'true');
  await second.evaluate(() => localStorage.setItem('arxiv-daily:read:v1:2609.00002', '0'));
  await page.waitForFunction(() => document.querySelector('[data-read-toggle="2609.00002v1"]').getAttribute('aria-pressed') === 'false');
  const denied = await browser.newContext();
  await denied.addInitScript(() => {
    Storage.prototype.getItem = () => { throw new Error('blocked'); };
    Storage.prototype.setItem = () => { throw new Error('blocked'); };
  });
  const deniedPage = await denied.newPage();
  await deniedPage.goto(base + '/fixture/');
  await deniedPage.locator('[data-read-toggle]').first().click();
  assert.equal(await deniedPage.locator('[data-read-toggle]').first().getAttribute('aria-pressed'), 'true');
  assert.equal(await deniedPage.locator('[data-storage-notice]').isVisible(), true);
  const noJS = await browser.newContext({ javaScriptEnabled: false });
  const staticPage = await noJS.newPage();
  await staticPage.goto(base + '/fixture/');
  assert.equal(await staticPage.locator('.paper:visible').count(), 3);
  await page.goto(base + '/');
  const out = process.env.ARXIV_SCREENSHOTS || '/tmp/arxiv-batch-qa';
  await mkdir(out, { recursive: true });
  await page.screenshot({ path: path.join(out, 'home-desktop.png') });
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  await page.screenshot({ path: path.join(out, 'home-mobile.png') });
  const entries = JSON.parse(await readFile(path.join(root, 'papers.json'), 'utf8'));
  const newestDate = entries.map((entry) => entry.date).sort().at(-1);
  let capturedLesson = false;
  for (const entry of entries) {
    if (entry.path === '2026-09-17/') continue;
    await page.goto(base + '/' + entry.path + 'notes.html');
    assert.equal(await page.locator('pre.mermaid').count(), 0, entry.path + ' unrendered diagram markup');
    if (entry.date === newestDate) {
      assert.equal(await page.locator('div.mermaid').count(), 0, entry.path + ' unrendered diagram container');
    }
    await page.waitForFunction(() => [...document.querySelectorAll('[data-mermaid]')].every((figure) => ['ready', 'error'].includes(figure.dataset.mermaidState)));
    assert.equal(await page.locator('[data-mermaid-state="error"]').count(), 0, entry.path + ' Mermaid');
    assert.ok(await page.locator('[data-mermaid-output] svg').count(), entry.path + ' diagram');
    assert.equal(await page.locator('[data-mermaid-output]').evaluateAll((outputs) =>
      outputs.every((output) => output.scrollWidth <= output.clientWidth + 1)), true, entry.path + ' initial diagram fit');
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, entry.path + ' article overflow');
    if (!capturedLesson) await page.screenshot({ path: path.join(out, 'lesson-notes-mobile.png') });
    await page.goto(base + '/' + entry.path + 'slides.html');
    assert.equal(await page.locator('pre.mermaid').count(), 0, entry.path + ' unrendered slide diagram');
    if (entry.date === newestDate) {
      assert.equal(await page.locator('div.mermaid').count(), 0, entry.path + ' unrendered slide diagram container');
    }
    assert.equal(await page.locator('.slide:visible').count(), 1);
    await page.locator('#next').click();
    assert.equal(await page.locator('#slide-2').isVisible(), true);
    const n = await page.locator('.slide').count();
    if (!capturedLesson) {
      await page.locator('#page-select').selectOption('3');
      await page.waitForFunction(() => document.querySelector('[data-mermaid]')?.dataset.mermaidState === 'ready');
      await page.screenshot({ path: path.join(out, 'lesson-map-mobile.png') });
      await page.locator('#page-select').selectOption('4');
      await page.screenshot({ path: path.join(out, 'lesson-slide-mobile.png') });
      capturedLesson = true;
    }
    await page.locator('#page-select').selectOption(String(n));
    assert.equal(await page.locator('#next').isDisabled(), true);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, entry.path + ' slides overflow');
  }
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ ok: true, papers: entries.length, checks: ['persistent base-ID read state', 'combined filters', 'reload', 'browser back', 'cross-tab sync', 'unknown filters', 'corrupt value', 'blocked storage fallback', 'no JavaScript', 'mobile layout', 'all new Mermaid diagrams and pagination'], screenshots: out }));
} finally {
  if (browser) await browser.close();
  await new Promise((resolve) => server.close(resolve));
}
