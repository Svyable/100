"use strict";
// Browser-based launch acceptance for the public Pages deployment. This is
// deliberately separate from generated-site byte tests: it requests LIVE URLs
// and exercises real DOM behavior with an isolated Chromium session.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const crypto = require("node:crypto");
const { chromium } = require("playwright");
const axe = require("axe-core");

const PUBLIC = "https://svyable.github.io/100/";
const PREVIEW = "http://127.0.0.1:8000/";
const BASE = process.env.PAGES_BASE || PUBLIC;
if (BASE !== PUBLIC && BASE !== PREVIEW) throw Error("Only the public site or the local PR preview is allowed");
const checks = [];
const metrics = {};
const stamp = new Date().toISOString();
const requestedBase = BASE;

async function run(label, work) {
  const started = Date.now();
  try {
    const detail = await work();
    checks.push({label, status: "pass", elapsed_ms: Date.now() - started, detail: detail || ""});
    console.log("PASS", label, detail || "");
  } catch (error) {
    checks.push({label, status: "fail", elapsed_ms: Date.now() - started, error: String(error.stack || error)});
    console.error("FAIL", label, error.message);
  }
}
async function responseOK(response, name) {
  assert(response && response.status() === 200, name + " returned " + (response?.status() || "no response"));
}
async function axeAudit(page, title) {
  await page.addScriptTag({content: axe.source});
  const result = await page.evaluate(async () => window.axe.run(document, {
    runOnly: {type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]}
  }));
  const serious = result.violations.filter(v => ["serious", "critical"].includes(v.impact));
  metrics["axe_" + title] = {passes: result.passes.length, violations: result.violations.map(v => ({
    id: v.id, impact: v.impact, elements: v.nodes.length,
    examples: v.nodes.slice(0, 35).map(n => ({
      target: n.target, html: n.html.slice(0, 160),
      details: n.any.map(x => ({message: x.message, data: x.data}))
    }))
  }))};
  if (serious.length) console.error("Axe examples:", JSON.stringify(metrics["axe_" + title].violations, null, 2).slice(0, 12000));
  assert.equal(serious.length, 0,
    title + ": " + serious.map(v => v.id + " (" + v.nodes.length + " elements)").join("; "));
}


async function assertCurrentDeployment(context) {
  // Verify that the remote CSS and homepage bytes match the checked-out commit.
  // For push-to-main runs, allow time for GitHub Pages' deployment to catch up.
  const dig = data => crypto.createHash("sha256").update(data).digest("hex");
  const paths = ["index.html", "assets/style.css"];
  const expected = paths.map(p => dig(fs.readFileSync("docs/" + p)));
  for (let attempt = 0; attempt < (BASE === PUBLIC ? 13 : 1); attempt++) {
    const actual = await Promise.all(paths.map(async p => {
      const response = await context.request.get(BASE + p, {timeout: 12000});
      return response.status() === 200 ? dig(await response.body()) : "http-" + response.status();
    }));
    if (actual.every((x, i) => x === expected[i])) return;
    if (attempt === (BASE === PUBLIC ? 12 : 0)) {
      throw Error("Pages deployment does not match checked-out index.html + style.css");
    }
    await new Promise(resolve => setTimeout(resolve, 15000));
  }
}

async function main() {
  const browser = await chromium.launch({headless: true});
  try {
    const context = await browser.newContext({viewport: {width: 1440, height: 900}});
    const page = await context.newPage();
    await run("exact deployed source matches checked-out site", () => assertCurrentDeployment(context));
    await run("public home and canonical document", async () => {
      const res = await page.goto(BASE, {waitUntil: "networkidle", timeout: 45000});
      await responseOK(res, "public home");
      assert.match(await page.title(), /100/);
      assert.equal(await page.locator("h1").count(), 1);
      assert.equal(await page.locator('link[rel="canonical"]').getAttribute("href"), PUBLIC);
      metrics.navigation_ms = Math.round(await page.evaluate(() =>
        performance.getEntriesByType("navigation")[0]?.domContentLoadedEventEnd || 0));
      assert(metrics.navigation_ms > 0 && metrics.navigation_ms < 15000,
        "DOM content loaded outside the audited 15-second browser budget");
      return "DOMContentLoaded " + metrics.navigation_ms + " ms";
    });

    await run("100 unique problem rows and JSON parity", async () => {
      const apiResponse = await context.request.get(BASE + "api/problems.json");
      await responseOK(apiResponse, "api/problems.json");
      const api = await apiResponse.json();
      assert.equal(api.count, 100);
      assert.equal(api.problems.length, 100);
      const ids = api.problems.map(p => p.id);
      assert.equal(new Set(ids).size, 100);
      const shown = await page.locator("#problem-list > li.row").evaluateAll(rows =>
        rows.map(row => row.dataset.id));
      assert.equal(shown.length, 100);
      assert.deepEqual(new Set(shown), new Set(ids));
      const png = await context.request.get(BASE + "assets/favicon.svg");
      await responseOK(png, "favicon");
      metrics.problems = ids.length;
      return "100/100 matching IDs";
    });

    await run("all 100 problem detail URLs resolve", async () => {
      const api = await (await context.request.get(BASE + "api/problems.json")).json();
      const ids = api.problems.map(p => p.id);
      const bad = [];
      // Bounded concurrency keeps the smoke test polite to GitHub Pages.
      for (let i = 0; i < ids.length; i += 8) {
        await Promise.all(ids.slice(i, i + 8).map(async id => {
          try {
            const result = await context.request.get(BASE + "problems/" + id + "/", {timeout: 15000});
            if (result.status() !== 200 || !(await result.text()).includes("<title>")) bad.push(id);
          } catch { bad.push(id); }
        }));
      }
      assert.deepEqual(bad, [], "Broken problem pages: " + bad.join(", "));
      metrics.problem_detail_ok = 100;
      return "100/100 HTTP 200 HTML pages";
    });

    await run("interactive search, field, evidence, and sort", async () => {
      await page.locator("#search-problems").fill("M095");
      await page.waitForFunction(() =>
        document.querySelectorAll("#problem-list > li.row:not([hidden])").length === 1);
      assert.equal(await page.locator("#problem-list > li.row:not([hidden])").first().getAttribute("data-id"), "M095");
      await page.locator("#reset-filters").click();
      await page.locator("#filter-field").selectOption("Combinatorics");
      await page.waitForTimeout(150);
      const fields = await page.locator("#problem-list > li.row:not([hidden])").evaluateAll(rows =>
        rows.map(row => row.dataset.field));
      assert(fields.length > 0 && fields.every(f => f === "Combinatorics"));
      await page.locator("#reset-filters").click();
      await page.locator("#filter-status").selectOption("verified_open");
      await page.waitForTimeout(150);
      const statuses = await page.locator("#problem-list > li.row:not([hidden])").evaluateAll(rows =>
        rows.map(row => row.dataset.status));
      assert(statuses.length > 0 && statuses.every(s => s === "verified_open"));
      await page.locator("#reset-filters").click();
      await page.locator("#sort-problems").selectOption("name");
      await page.waitForTimeout(150);
      const sorted = await page.locator("#problem-list > li.row").evaluateAll(rows =>
        rows.map(row => row.dataset.name));
      assert(sorted.every((n, i) => i === 0 || sorted[i - 1].localeCompare(n) <= 0),
        "Name sort did not reorder the live DOM");
      return "search + domain + evidence + alphabetical sort";
    });

    await run("quick campaign filter and reset", async () => {
      await page.locator("#reset-filters").click();
      await page.locator("#only-campaign").check();
      await page.waitForTimeout(150);
      const rows = await page.locator("#problem-list > li.row:not([hidden])").evaluateAll(rows =>
        rows.map(row => row.dataset.campaign));
      assert(rows.length >= 5 && rows.every(v => v === "1"));
      await page.locator("#reset-filters").click();
      assert.equal(await page.locator("#problem-list > li.row:not([hidden])").count(), 100);
      return rows.length + " campaign-linked entries; reset restores all";
    });

    await run("at least five campaign destinations and warning boundaries", async () => {
      const response = await context.request.get(BASE + "data/portfolio.json");
      await responseOK(response, "data/portfolio.json");
      const portfolio = await response.json();
      assert(portfolio.campaigns.length >= 5);
      const links = portfolio.campaigns.slice(0, 5).map(x => BASE + "problems/" + x.problem_id + "/");
      for (const link of links) await responseOK(await context.request.get(link), link);
      assert.match(await page.locator(".status-note").innerText(),
        /does not mean independently confirmed unsolved/i);
      metrics.campaigns = portfolio.campaigns.length;
      return "5/5 sample campaign-linked problem pages + unverified warning";
    });

    await run("legacy M095 focus deep link redirects", async () => {
      const res = await page.goto(BASE + "?focus=M095", {waitUntil: "domcontentloaded"});
      assert(res);
      await page.waitForURL(BASE + "problems/M095/", {timeout: 12000});
      assert.match(await page.locator("h1").first().innerText(), /Ramsey/i);
      return "redirected to permanent M095 page";
    });

    await run("WCAG axe audit on home and a problem dossier", async () => {
      await page.goto(BASE, {waitUntil: "networkidle"});
      await axeAudit(page, "home");
      await page.goto(BASE + "problems/M095/", {waitUntil: "networkidle"});
      await axeAudit(page, "M095");
      return "no serious/critical WCAG A/AA violations (automated scan only)";
    });

    await run("mobile viewport, keyboard focus and reduced motion", async () => {
      const mobile = await browser.newContext({
        viewport: {width: 390, height: 844}, isMobile: true,
        deviceScaleFactor: 2, hasTouch: true, reducedMotion: "reduce"
      });
      try {
        const small = await mobile.newPage();
        await responseOK(await small.goto(BASE, {waitUntil: "networkidle"}), "mobile home");
        const size = await small.evaluate(() => ({
          scroll: document.documentElement.scrollWidth, width: document.documentElement.clientWidth,
          motion: matchMedia("(prefers-reduced-motion: reduce)").matches
        }));
        assert(size.scroll <= size.width + 2, "horizontal overflow " + JSON.stringify(size));
        assert(size.motion, "reduced-motion media preference not active");
        await small.keyboard.press("Tab");
        const focused = await small.evaluate(() => document.activeElement?.classList.contains("skip-link"));
        assert(focused, "skip-link is not first keyboard focus target");
        metrics.mobile = size;
        await small.screenshot({path: "artifacts/pages-mobile.png", fullPage: false});
        return "390px viewport, no overflow, focus and reduced-motion checked";
      } finally { await mobile.close(); }
    });

    await run("performance budget and snapshot stability", async () => {
      await page.goto(BASE, {waitUntil: "networkidle"});
      const p = await page.evaluate(() => ({
        dom_ms: Math.round(performance.getEntriesByType("navigation")[0]?.domContentLoadedEventEnd || 0),
        load_ms: Math.round(performance.getEntriesByType("navigation")[0]?.loadEventEnd || 0),
        resource_count: performance.getEntriesByType("resource").length
      }));
      assert(p.dom_ms > 0 && p.dom_ms < 15000, "DOMContentLoaded exceeds 15s budget");
      assert(p.load_ms < 20000, "load event exceeds 20s budget");
      assert(p.resource_count < 150, "unexpected asset request fanout");
      metrics.performance = p;
      return JSON.stringify(p);
    });
    await context.close();
  } finally {
    await browser.close();
    fs.mkdirSync("artifacts", {recursive: true});
    const report = {audit: "svyable.pages-live.v1", as_of: stamp, site: BASE, checks, metrics,
      passed: checks.filter(x => x.status === "pass").length,
      failed: checks.filter(x => x.status === "fail").length};
    fs.writeFileSync("artifacts/pages-live.json", JSON.stringify(report, null, 2) + "\n");
    console.log(JSON.stringify({passed: report.passed, failed: report.failed, metrics}, null, 2));
    if (report.failed) process.exitCode = 1;
  }
}
main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
