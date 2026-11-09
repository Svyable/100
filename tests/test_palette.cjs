"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// Tiny DOM boundary: test transitions without adding a browser framework to the static site.
function harness() {
  class Element {
    constructor(tag) {
      this.tagName = tag.toUpperCase();
      this.listeners = {};
      this.children = [];
      this.attributes = {};
      this.dataset = {};
      this.textContent = "";
      this.value = "";
      this.open = false;
      this.focusCount = 0;
    }
    addEventListener(name, callback) {
      (this.listeners[name] ||= []).push(callback);
    }
    fire(name, options = {}) {
      for (const callback of this.listeners[name] || [])
        callback({ target: this, ...options });
    }
    setAttribute(key, value) { this.attributes[key] = value; }
    replaceChildren(...children) { this.children = children; }
    append(...children) { this.children.push(...children); }
    focus() { this.focusCount += 1; }
    scrollIntoView() {}
    showModal() { this.open = true; }
    close() { this.open = false; this.fire("close"); }
  }
  const dialog = new Element("dialog");
  const input = new Element("input");
  const results = new Element("ul");
  const opener = new Element("button");
  const nodes = {"#palette": dialog, "#palette-input": input, "#palette-results": results};
  const requests = [];
  const document = {
    documentElement: { dataset: { root: "./" } },
    querySelector: selector => nodes[selector] || null,
    querySelectorAll: selector => selector === "[data-palette-open]" ? [opener] : [],
    addEventListener() {},
    createElement: tag => new Element(tag)
  };
  const context = {
    document, location: { pathname: "/100/", search: "", hash: "" },
    history: { replaceState() {} },
    navigator: {}, URLSearchParams, setTimeout, clearTimeout,
    matchMedia: () => ({ matches: false }),
    fetch: () => new Promise((resolve, reject) => requests.push({resolve, reject}))
  };
  const script = fs.readFileSync(path.join(__dirname, "../docs/assets/app.js"), "utf8");
  vm.runInNewContext(script, context, {filename: "app.js"});
  return { dialog, input, results, requests, open: () => opener.fire("click") };
}
const records = [
  { k: "page", id: "", t: "Start here", s: "Getting started", x: "", u: "start/" },
  { k: "problem", id: "M074", t: "Caccetta-Haggkvist", s: "Open target", x: "", u: "problems/M074/" }
];
const response = {ok: true, json: async () => records};
const tick = async () => {
  await new Promise(resolve => setImmediate(resolve));
  await new Promise(resolve => setImmediate(resolve));
};

test("palette immediately focuses, shows pending state, and retains search typed during fetch", async () => {
  const ui = harness();
  ui.open();
  assert.equal(ui.dialog.open, true);
  assert.equal(ui.input.focusCount, 1);
  assert.equal(ui.results.attributes["aria-busy"], "true");
  assert.equal(ui.results.children[0].textContent, "Loading search…");
  ui.input.value = "M074";
  ui.input.fire("input");
  assert.equal(ui.requests.length, 1);
  ui.requests[0].resolve(response);
  await tick();
  assert.equal(ui.results.attributes["aria-busy"], "false");
  assert.equal(ui.results.children.length, 1);
  assert.equal(ui.results.children[0].children[0].href, "./problems/M074/");
  ui.dialog.close();
  ui.open();
  await tick();
  assert.equal(ui.requests.length, 1, "successful index is cached");
});

test("closed palette never repaints from an outdated async response", async () => {
  const ui = harness();
  ui.open();
  ui.dialog.close();
  ui.requests[0].resolve(response);
  await tick();
  assert.equal(ui.dialog.open, false);
  assert.equal(ui.results.children[0].textContent, "Loading search…");
  ui.open();
  await tick();
  assert.equal(ui.results.children[0].children[0].href, "./start/");
  assert.equal(ui.requests.length, 1);
});

test("failed index can be retried and is not cached as success", async () => {
  const ui = harness();
  ui.open();
  ui.requests[0].reject(new Error("offline"));
  await tick();
  assert.match(ui.results.children[0].textContent, /Close and reopen to retry/);
  assert.equal(ui.results.attributes["aria-busy"], "false");
  ui.dialog.close();
  ui.open();
  assert.equal(ui.requests.length, 2);
  ui.requests[1].resolve(response);
  await tick();
  assert.equal(ui.results.children[0].children[0].href, "./start/");
});
