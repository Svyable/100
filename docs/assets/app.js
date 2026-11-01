"use strict";
// Progressive enhancement only: every page is fully rendered HTML without this file.
(() => {
  const doc = document.documentElement;
  const root = doc.dataset.root || "./";
  const $ = sel => document.querySelector(sel);
  const $$ = sel => Array.from(document.querySelectorAll(sel));
  const typing = el => el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName));

  // Legacy deep links (?focus=M074) from the single-page dashboard.
  const legacy = new URLSearchParams(location.search).get("focus");
  if (legacy && /^M\d{3}$/.test(legacy)) {
    location.replace(root + "problems/" + legacy + "/");
    return;
  }

  // ---------------------------------------------------------------- theme
  const prefersDark = () => matchMedia("(prefers-color-scheme: dark)").matches;
  for (const button of $$("[data-theme-toggle]")) {
    const sync = () => button.setAttribute("aria-pressed",
      String((doc.dataset.theme || (prefersDark() ? "dark" : "light")) === "dark"));
    sync();
    button.addEventListener("click", () => {
      const current = doc.dataset.theme || (prefersDark() ? "dark" : "light");
      const next = current === "dark" ? "light" : "dark";
      doc.dataset.theme = next;
      try { localStorage.setItem("theme", next); } catch (e) { /* private mode */ }
      sync();
    });
  }

  // ---------------------------------------------------------------- copy buttons
  for (const button of $$("[data-copy]")) {
    button.addEventListener("click", async () => {
      const target = $(button.dataset.copy);
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.textContent);
        button.textContent = "Copied";
        setTimeout(() => { button.textContent = "Copy"; }, 1600);
      } catch (e) { /* clipboard unavailable */ }
    });
  }

  // ---------------------------------------------------------------- ranked list filters
  const list = $("#problem-list");
  const form = $("#filters");
  if (list && form) {
    const rows = Array.from(list.children);
    const controls = {
      q: $("#search-problems"), field: $("#filter-field"), status: $("#filter-status"),
      modality: $("#filter-modality"), sort: $("#sort-problems"),
      verifier: $("#only-verifier"), campaign: $("#only-campaign"), lean: $("#only-lean")
    };
    const numeric = ["impact", "attackability", "verifiability", "spillover"];
    const read = () => ({
      q: controls.q.value.trim().toLocaleLowerCase(),
      field: controls.field.value, status: controls.status.value,
      modality: controls.modality.value, sort: controls.sort.value || "dispatch",
      verifier: controls.verifier.checked, campaign: controls.campaign.checked,
      lean: controls.lean.checked
    });
    const compare = sort => (a, b) => {
      const ex = (Number(a.dataset.execution) - Number(b.dataset.execution));
      if (sort === "name") return a.dataset.name.localeCompare(b.dataset.name);
      if (sort === "rank") return Number(a.dataset.rank) - Number(b.dataset.rank);
      if (sort === "execution") return ex;
      const dispatch = Number(a.dataset.dispatch) - Number(b.dataset.dispatch);
      if (sort === "dispatch") return dispatch;
      if (numeric.includes(sort)) return (Number(b.dataset[sort]) - Number(a.dataset[sort])) || dispatch;
      return dispatch;
    };
    const apply = (push = true) => {
      const s = read();
      const terms = s.q.split(/\s+/).filter(Boolean);
      let shown = 0;
      const sorted = rows.slice().sort(compare(s.sort));
      for (const row of sorted) {
        const d = row.dataset;
        const ok = (!s.field || d.field === s.field) && (!s.status || d.status === s.status) &&
          (!s.modality || d.modality === s.modality) && (!s.verifier || d.verifier === "1") &&
          (!s.campaign || d.campaign === "1") && (!s.lean || d.lean === "1") && terms.every(t => d.search.includes(t));
        row.hidden = !ok;
        if (ok) shown += 1;
      }
      list.replaceChildren(...sorted);
      const sortLabel = controls.sort.options[controls.sort.selectedIndex].text.toLowerCase();
      $("#results-count").textContent = shown === rows.length && !terms.length ?
        "Showing all " + rows.length + " questions · " + sortLabel :
        "Showing " + shown + " of " + rows.length + " questions · " + sortLabel;
      $("#empty-state").hidden = shown !== 0;
      if (push) {
        const params = new URLSearchParams();
        if (controls.q.value.trim()) params.set("q", controls.q.value.trim());
        for (const key of ["field", "status", "modality"]) if (s[key]) params.set(key, s[key]);
        if (s.sort !== "dispatch") params.set("sort", s.sort);
        if (s.verifier) params.set("verifier", "1");
        if (s.campaign) params.set("campaign", "1");
        if (s.lean) params.set("lean", "1");
        const query = params.toString();
        history.replaceState(null, "", location.pathname + (query ? "?" + query : "") + location.hash);
      }
    };
    const restore = () => {
      const params = new URLSearchParams(location.search);
      controls.q.value = params.get("q") || "";
      for (const key of ["field", "status", "modality", "sort"]) {
        const value = params.get(key);
        if (value && Array.from(controls[key].options).some(o => o.value === value)) controls[key].value = value;
      }
      controls.verifier.checked = params.get("verifier") === "1";
      controls.campaign.checked = params.get("campaign") === "1";
      controls.lean.checked = params.get("lean") === "1";
      return params.toString() !== "";
    };
    let debounce;
    form.addEventListener("input", event => {
      clearTimeout(debounce);
      debounce = setTimeout(() => apply(), event.target === controls.q ? 90 : 0);
    });
    form.addEventListener("submit", event => event.preventDefault());
    controls.verifier.addEventListener("change", () => apply());
    controls.campaign.addEventListener("change", () => apply());
    controls.lean.addEventListener("change", () => apply());
    $("#reset-filters").addEventListener("click", () => {
      form.reset();
      controls.verifier.checked = controls.campaign.checked = controls.lean.checked = false;
      apply();
      controls.q.focus();
    });
    if (restore()) apply(false);
  }

  // ---------------------------------------------------------------- prev/next keyboard paging
  document.addEventListener("keydown", event => {
    if (event.altKey || event.ctrlKey || event.metaKey || typing(event.target)) return;
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      const link = $(event.key === "ArrowLeft" ? 'a[rel="prev"]' : 'a[rel="next"]');
      if (link) location.href = link.href;
    }
  });

  // Evidence-first handoff is an optional same-origin enhancement. All proof data
  // and claim links remain in the server-rendered pages when scripts are disabled.
  if ($(".problem-page .problem-grid") || $(".work-detail")) {
    const frontierScript = document.createElement("script");
    frontierScript.src = root + "assets/frontier.js";
    frontierScript.defer = true;
    document.head.append(frontierScript);
  }

  // ---------------------------------------------------------------- command palette
  const dialog = $("#palette");
  if (!dialog || typeof dialog.showModal !== "function") return;
  const input = $("#palette-input");
  const results = $("#palette-results");
  let index = null;
  let matches = [];
  let active = 0;
  const kinds = { problem: "Problem", field: "Field", campaign: "Campaign", probe: "Probe",
    engine: "Engine", claim: "Claim", formal: "Lean", work: "Work", document: "Document", page: "Page" };
  const normalize = s => String(s || "").toLocaleLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");

  async function loadIndex() {
    if (index) return index;
    const response = await fetch(root + "api/search.json");
    if (!response.ok) throw new Error("HTTP " + response.status);
    index = (await response.json()).map(item => ({
      ...item, n: normalize(item.t), h: normalize([item.id, item.t, item.s, item.x].join(" "))
    }));
    return index;
  }
  function rank(query) {
    const q = normalize(query).trim();
    if (!q) return index.filter(i => i.k === "page" || i.k === "problem").slice(0, 12);
    const terms = q.split(/\s+/);
    const scored = [];
    for (const item of index) {
      if (!terms.every(t => item.h.includes(t))) continue;
      let score = 0;
      if (item.id && normalize(item.id) === q) score += 100;
      if (item.n.startsWith(q)) score += 40;
      else if (item.n.includes(q)) score += 20;
      if (item.k === "problem") score += 5;
      score -= item.n.length / 100;
      scored.push([score, item]);
    }
    return scored.sort((a, b) => b[0] - a[0]).slice(0, 20).map(x => x[1]);
  }
  function draw() {
    results.replaceChildren(...matches.map((item, i) => {
      const li = document.createElement("li");
      li.id = "palette-option-" + i;
      li.setAttribute("role", "option");
      li.setAttribute("aria-selected", String(i === active));
      const a = document.createElement("a");
      a.href = root + item.u;
      const kind = document.createElement("span");
      kind.className = "palette-kind";
      kind.textContent = kinds[item.k] || item.k;
      const title = document.createElement("span");
      title.className = "palette-title";
      title.textContent = (item.id && item.k === "problem" ? item.id + " · " : "") + item.t;
      const sub = document.createElement("span");
      sub.className = "palette-sub";
      sub.textContent = item.s || "";
      a.append(kind, title, sub);
      li.append(a);
      return li;
    }));
    if (!matches.length) {
      const li = document.createElement("li");
      li.className = "palette-empty";
      li.textContent = "No matches";
      results.append(li);
    }
    input.setAttribute("aria-activedescendant", matches.length ? "palette-option-" + active : "");
    const current = results.children[active];
    if (current) current.scrollIntoView({ block: "nearest" });
  }
  async function open() {
    if (dialog.open) return;
    dialog.showModal();
    input.value = "";
    try {
      await loadIndex();
      matches = rank("");
      active = 0;
      draw();
    } catch (e) {
      results.innerHTML = '<li class="palette-empty">Search index unavailable.</li>';
    }
    input.focus();
  }
  for (const button of $$("[data-palette-open]")) button.addEventListener("click", open);
  document.addEventListener("keydown", event => {
    if ((event.key === "k" && (event.metaKey || event.ctrlKey)) ||
        (event.key === "/" && !typing(event.target) && !dialog.open)) {
      event.preventDefault();
      open();
    }
  });
  input.addEventListener("input", () => {
    if (!index) return;
    matches = rank(input.value);
    active = 0;
    draw();
  });
  input.addEventListener("keydown", event => {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if (!matches.length) return;
      active = (active + (event.key === "ArrowDown" ? 1 : -1) + matches.length) % matches.length;
      draw();
    } else if (event.key === "Enter") {
      event.preventDefault();
      const item = matches[active];
      if (item) location.href = root + item.u;
    }
  });
  dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
})();
