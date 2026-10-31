"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const statusNames = Object.freeze({
    official_open: "Officially open",
    verified_open: "Specialist verified",
    needs_review: "Needs review",
    claim_needs_review: "Claim under review"
  });
  const campaignIds = new Set(["M074", "M075", "M088", "M092", "M095"]);
  const state = { all: [], filtered: [], limit: 20, sort: "rank", search: "", field: "", status: "" };
  const escapeHTML = (s) => String(s ?? "").replace(/[&<>"']/g,
    (ch) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  const safeExternal = (value) => {
    try {
      const url = new URL(value);
      return url.protocol === "https:" ? url.href : null;
    } catch { return null; }
  };
  const score = (p) => 6*p.impact + 6*p.attackability + 5*p.verifiability + 3*p.spillover;
  const statusName = (p) => statusNames[p.evidence_state] || "Status unknown";
  const metric = (label, value) =>
    '<div class="detail-metric"><span>' + escapeHTML(label) + '</span>' +
    '<div class="meter"><i style="width:' + (Number(value)*20) + '%"></i></div>' +
    '<b>' + Number(value) + '/5</b></div>';
  function item(p) {
    const status = Object.hasOwn(statusNames, p.evidence_state) ? p.evidence_state : "needs_review";
    const source = safeExternal(p.source_url);
    const date = p.checked_on ? 'Source intake: ' + escapeHTML(p.checked_on) + '. ' : 'Source status not yet audited. ';
    const detailLinks = (source
      ? '<a href="' + escapeHTML(source) + '" target="_blank" rel="noopener noreferrer">Primary / starting source ↗</a>' : '') +
      '<a href="https://github.com/Svyable/100/issues/new" target="_blank" rel="noopener noreferrer">Contribute evidence ↗</a>' +
      '<a href="?focus=' + encodeURIComponent(p.id) + '#rankings">Direct link ↗</a>';
    const article = document.createElement("details");
    article.className = "entry";
    article.id = "problem-" + p.id;
    article.innerHTML =
      '<summary aria-label="Expand ' + escapeHTML(p.name) + '">' +
      '<span class="entry-index"><span class="ordinal">' + p.rank + '</span><span class="entry-id">' + escapeHTML(p.id) + '</span></span>' +
      '<span class="entry-info"><span class="entry-name">' + escapeHTML(p.name) + '</span><span class="entry-field">' + escapeHTML(p.field) + '</span></span>' +
      '<span class="entry-score" aria-label="Score ' + p.score + ' out of 100"><strong>' + p.score + '</strong><span class="small-bar" aria-hidden="true"><i style="width:' + p.score + '%"></i></span></span>' +
      '<span><span class="status-pill status-' + status + '">' + statusName(p) + '</span></span>' +
      '<span class="entry-chevron" aria-hidden="true">+</span></summary>' +
      '<div class="entry-detail"><div><span class="detail-label">THE QUESTION</span><p class="detail-question">' + escapeHTML(p.question) + '</p>' +
      '<span class="detail-label">FIRST RESEARCH ATTACK</span><p class="detail-attack">' + escapeHTML(p.first_attack) + '</p>' +
      '<div class="detail-links">' + detailLinks + '</div></div>' +
      '<div><span class="detail-label">EDITORIAL SCORE BREAKDOWN</span><div class="detail-metrics">' +
      metric("Impact",p.impact) + metric("Attackability",p.attackability) +
      metric("Verifiability",p.verifiability) + metric("Spillover",p.spillover) +
      '</div><p class="detail-note"><strong>Evidence:</strong> ' + escapeHTML(statusName(p)) + '. ' +
      date + 'Evidence status does not certify that the full conjecture remains open today.</p>' +
      (campaignIds.has(p.id) ? '<p class="detail-note">This candidate is covered by an initial research dossier.</p>' : '') +
      '</div></div>';
    return article;
  }
  function compare(a,b) {
    if (state.sort === "name") return a.name.localeCompare(b.name);
    if (state.sort !== "rank") {
      const d = Number(b[state.sort]) - Number(a[state.sort]);
      if (d) return d;
    }
    return a.rank - b.rank;
  }
  function render() {
    const query = state.search.toLocaleLowerCase().trim();
    state.filtered = state.all.filter((p) =>
      (!state.field || p.field === state.field) &&
      (!state.status || p.evidence_state === state.status) &&
      (!query || [p.id,p.name,p.field,p.question,p.first_attack].some((value) => String(value ?? "").toLocaleLowerCase().includes(query)))
    ).sort(compare);
    const list = $("problem-list");
    const fragment = document.createDocumentFragment();
    for (const p of state.filtered.slice(0,state.limit)) fragment.appendChild(item(p));
    list.replaceChildren(fragment);
    if (!state.filtered.length) {
      const div = document.createElement("p");
      div.className = "empty-state";
      div.textContent = "No matches. Try another field or clear the filters.";
      list.appendChild(div);
    }
    $("results-count").textContent = 'Showing ' + Math.min(state.limit,state.filtered.length) + ' of ' +
      state.filtered.length + ' matching questions';
    $("load-more").hidden = state.filtered.length <= state.limit;
  }
  function filterChanged() {
    state.search = $("search-problems").value;
    state.field = $("filter-field").value;
    state.status = $("filter-status").value;
    state.sort = $("sort-problems").value;
    state.limit = 20;
    render();
  }
  async function start() {
    try {
      const res = await fetch("./data/portfolio.json", {cache:"no-store"});
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      if (!data || !Array.isArray(data.problems) || data.problems.length !== 100)
        throw new Error("Invalid 100-problem snapshot");
      state.all = data.problems;
      const fields = [...new Set(state.all.map(p => p.field))].sort();
      for (const field of fields) {
        const option = document.createElement("option");
        option.value = field; option.textContent = field;
        $("filter-field").appendChild(option);
      }
      $("stat-total").textContent = data.problems.length;
      $("stat-official").textContent = data.problems.filter(p => p.evidence_state === "official_open").length;
      $("stat-claims").textContent = data.problems.filter(p => p.evidence_state === "claim_needs_review").length;
      $("snapshot-date").textContent = "Snapshot source-review date: " + (data.source_review_as_of || "varies") + ".";
      for (const id of ["search-problems","filter-field","filter-status","sort-problems"]) {
        $(id).addEventListener(id === "search-problems" ? "input" : "change", filterChanged);
      }
      $("reset-filters").addEventListener("click", () => {
        $("search-problems").value = ""; $("filter-field").value = "";
        $("filter-status").value = ""; $("sort-problems").value = "rank";
        filterChanged(); $("search-problems").focus();
      });
      $("load-more").addEventListener("click", () => {state.limit += 20; render();});
      const focus = new URLSearchParams(location.search).get("focus");
      if (focus && state.all.some(p => p.id === focus)) {
        state.limit = 100;
        render();
        const el = $("problem-" + focus);
        if (el) {
          el.open = true;
          requestAnimationFrame(() => el.scrollIntoView({block:"center",behavior:"auto"}));
        }
      } else { render(); }
    } catch (error) {
      const panel = document.createElement("div");
      panel.className = "empty-state";
      panel.textContent = "The rankings snapshot could not be loaded. View the source registry on GitHub or try refreshing the page.";
      $("problem-list").replaceChildren(panel);
      $("results-count").textContent = "Registry unavailable";
      console.error("Unable to load portfolio",error);
    }
  }
  start();
})();
