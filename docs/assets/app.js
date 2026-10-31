"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const evidenceNames = Object.freeze({
    official_open: "Officially open",
    verified_open: "Specialist verified",
    needs_review: "Needs review",
    claim_needs_review: "Claim under review"
  });
  const campaignIds = new Set(["M074","M075","M088","M092","M095"]);
  const state = {
    all: [], filtered: [], limit: 20, sort: "execution",
    search: "", field: "", status: ""
  };
  const escapeHTML = s => String(s ?? "").replace(/[&<>"']/g,
    ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  const safeExternal = value => {
    if (typeof value !== "string") return null;
    try {
      const url = new URL(value);
      return url.protocol === "https:" ? url.href : null;
    } catch { return null; }
  };
  const repoFile = path => {
    if (typeof path !== "string" || !/^[a-zA-Z0-9_.\/-]+$/.test(path) ||
        path.split("/").includes("..") || path.startsWith("/")) return null;
    return "https://github.com/Svyable/100/blob/main/" + path;
  };
  const evidenceName = p => evidenceNames[p.evidence_state] || "Status unknown";
  const metric = (label, value) =>
    '<div class="detail-metric"><span>' + escapeHTML(label) + '</span>' +
    '<div class="meter"><i style="width:' + Number(value)*20 + '%"></i></div>' +
    '<b>' + Number(value) + '/5</b></div>';

  function problemRow(p) {
    const knownStatus = Object.hasOwn(evidenceNames, p.evidence_state) ?
      p.evidence_state : "needs_review";
    const source = safeExternal(p.source_url);
    const description = p.checked_on ? "Source intake: " + escapeHTML(p.checked_on) + ". " :
      "Exact source status not yet audited. ";
    const links = (source ?
      '<a href="' + escapeHTML(source) + '" target="_blank" rel="noopener noreferrer">Source / starting reference ↗</a>' : "") +
      '<a href="https://github.com/Svyable/100/issues/new" target="_blank" rel="noopener noreferrer">Submit evidence ↗</a>' +
      '<a href="?focus=' + encodeURIComponent(p.id) + '#rankings">Direct link ↗</a>';
    const entry = document.createElement("details");
    entry.className = "entry";
    entry.id = "problem-" + p.id;
    entry.innerHTML =
      '<summary aria-label="Expand ' + escapeHTML(p.name) + '">' +
      '<span class="entry-index"><span class="ordinal">' + p.execution_rank +
      '</span><span class="entry-id">' + escapeHTML(p.id) + '</span></span>' +
      '<span class="entry-info"><span class="entry-name">' + escapeHTML(p.name) +
      '</span><span class="entry-field">' + escapeHTML(p.field) + '</span></span>' +
      '<span class="entry-score" aria-label="Execution index ' + p.execution_score +
      ': editorial ' + p.score + ', readiness plus ' + p.readiness + '">' +
      '<strong>' + p.execution_score + '</strong><span class="small-bar" aria-hidden="true">' +
      '<i style="width:' + Math.min(100,p.execution_score) + '%"></i></span></span>' +
      '<span><span class="status-pill status-' + knownStatus + '">' + evidenceName(p) +
      '</span></span><span class="entry-chevron" aria-hidden="true">+</span></summary>' +
      '<div class="entry-detail"><div><span class="detail-label">THE OPEN QUESTION</span>' +
      '<p class="detail-question">' + escapeHTML(p.question) + '</p>' +
      '<span class="detail-label">CURRENT FIRST ATTACK</span>' +
      '<p class="detail-attack">' + escapeHTML(p.first_attack) + '</p>' +
      '<div class="detail-links">' + links + '</div></div>' +
      '<div><span class="detail-label">PRIORITY DECOMPOSITION</span>' +
      '<p class="detail-note"><strong>Execution rank:</strong> #' + p.execution_rank +
      ' · <strong>Editorial rank:</strong> #' + p.rank + '</p>' +
      '<p class="detail-note"><strong>Editorial score:</strong> ' + p.score +
      ' · <strong>Readiness:</strong> +' + p.readiness +
      ' · <strong>Execution index:</strong> ' + p.execution_score + '</p>' +
      '<div class="detail-metrics">' +
      metric("Impact",p.impact) + metric("Attackability",p.attackability) +
      metric("Verifiability",p.verifiability) + metric("Spillover",p.spillover) +
      '</div><p class="detail-note"><strong>Evidence:</strong> ' +
      escapeHTML(evidenceName(p)) + '. ' + description +
      'This classification is not a universal proof-status certification.</p>' +
      (campaignIds.has(p.id) ?
        '<p class="detail-note"><strong>Proof campaign:</strong> ' +
        escapeHTML(p.campaign_stage || "specified") +
        ' · ' + p.milestone_count + ' recorded evidence milestones.</p>' : '') +
      '</div></div>';
    return entry;
  }

  function compare(a,b) {
    if (state.sort === "name") return a.name.localeCompare(b.name);
    if (state.sort === "execution") return a.execution_rank - b.execution_rank;
    if (state.sort === "rank") return a.rank - b.rank;
    const difference = Number(b[state.sort]) - Number(a[state.sort]);
    return difference || a.execution_rank - b.execution_rank;
  }
  function renderProblems() {
    const query = state.search.trim().toLocaleLowerCase();
    state.filtered = state.all.filter(p =>
      (!state.field || p.field === state.field) &&
      (!state.status || p.evidence_state === state.status) &&
      (!query || [p.id,p.name,p.field,p.question,p.first_attack].some(
        value => String(value ?? "").toLocaleLowerCase().includes(query)))
    ).sort(compare);
    const fragment = document.createDocumentFragment();
    for (const p of state.filtered.slice(0,state.limit)) fragment.appendChild(problemRow(p));
    if (!state.filtered.length) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No matches. Change your search or clear the filters.";
      fragment.appendChild(empty);
    }
    $("problem-list").replaceChildren(fragment);
    $("results-count").textContent = "Showing " + Math.min(state.limit,state.filtered.length) +
      " of " + state.filtered.length + " matching questions";
    $("load-more").hidden = state.filtered.length <= state.limit;
  }
  function filterChanged() {
    state.search = $("search-problems").value;
    state.field = $("filter-field").value;
    state.status = $("filter-status").value;
    state.sort = $("sort-problems").value;
    state.limit = 20;
    renderProblems();
  }
  function renderQueue(data) {
    const root = $("execution-queue");
    const fragment = document.createDocumentFragment();
    for (const c of data.execution_queue) {
      const card = document.createElement("article");
      card.className = "execution-card";
      const dossierUrl = repoFile(c.dossier);
      card.innerHTML =
        '<div class="execution-card-top"><span>ATTACK #' + c.execution_rank +
        ' · ' + escapeHTML(c.problem_id) + '</span>' +
        '<span class="execution-score">INDEX ' + c.execution_score + '</span></div>' +
        '<h3>' + escapeHTML(c.name) + '</h3>' +
        '<span class="step-label">FIRST PROOF OBLIGATION</span>' +
        '<p>' + escapeHTML(c.first_proof_obligation) + '</p>' +
        '<span class="step-label">NEXT EXECUTABLE STEP</span>' +
        '<p>' + escapeHTML(c.next_experiment) + '</p>' +
        (dossierUrl ? '<a href="' + escapeHTML(dossierUrl) +
         '" target="_blank" rel="noopener noreferrer">Research dossier ↗</a>' : '');
      fragment.appendChild(card);
    }
    if (!data.execution_queue.length) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No proof campaigns have been defined yet.";
      fragment.appendChild(empty);
    }
    root.replaceChildren(fragment);
  }
  function renderSolved(data) {
    const root = $("solved-list");
    const fragment = document.createDocumentFragment();
    if (data.solved.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-archive";
      empty.innerHTML = '<span class="empty-archive-number">0</span>' +
        '<div><h3>No full conjecture resolved by this project yet.</h3>' +
        '<p>That empty ledger is deliberate. Known small-case checks, proof announcements, ' +
        'and unreviewed manuscripts cannot be presented as accepted solutions. ' +
        'When a full proof or counterexample passes independent review, its sources ' +
        'and exact scope will appear here.</p></div>';
      fragment.appendChild(empty);
    }
    for (const s of data.solved) {
      const entry = document.createElement("article");
      entry.className = "solved-entry";
      const proofUrl = safeExternal(s.proof_url);
      const reviews = (s.independent_review_urls || []).map(safeExternal).filter(Boolean);
      entry.innerHTML =
        '<span class="detail-label">VERIFIED ' + escapeHTML(s.resolution.toUpperCase()) +
        ' · ' + escapeHTML(s.accepted_on) + '</span>' +
        '<h3>' + escapeHTML(s.name) + '</h3>' +
        '<p>' + escapeHTML(s.full_statement) + '</p>' +
        '<p>' + escapeHTML(s.verification_notes) + '</p>' +
        (proofUrl ? '<a href="' + escapeHTML(proofUrl) +
          '" target="_blank" rel="noopener noreferrer">Full proof ↗</a>' : '') +
        reviews.map((url,i) => '<a href="' + escapeHTML(url) +
          '" target="_blank" rel="noopener noreferrer">Independent review ' + (i+1) + ' ↗</a>').join("");
      fragment.appendChild(entry);
    }
    root.replaceChildren(fragment);
    $("stat-solved").textContent = String(data.solved.length);
    $("nav-solved-count").textContent = String(data.solved.length);
    $("solved-badge").textContent = String(data.solved.length) + " VERIFIED";
  }
  function renderMilestones(data) {
    const root = $("milestone-list");
    const fragment = document.createDocumentFragment();
    for (const m of data.milestones) {
      const card = document.createElement("article");
      card.className = "milestone-card";
      const artifact = repoFile(m.artifact);
      const label = m.classification === "reproduced_known" ?
        "REPRODUCED / ESTABLISHED MATHEMATICS" : "REVIEWED RESTRICTED THEOREM";
      card.innerHTML = '<span class="milestone-type">' + escapeHTML(label) +
        ' · ' + escapeHTML(m.problem_id) + '</span>' +
        '<h4>' + escapeHTML(m.title) + '</h4>' +
        '<p>' + escapeHTML(m.scope) + '</p>' +
        '<code>' + escapeHTML(m.verifier) + '</code>' +
        (artifact ? '<a href="' + escapeHTML(artifact) +
          '" target="_blank" rel="noopener noreferrer">Inspect independent checker ↗</a>' : '');
      fragment.appendChild(card);
    }
    if (data.milestones.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No reproducible verification milestones committed yet.";
      fragment.appendChild(empty);
    }
    root.replaceChildren(fragment);
    $("stat-benchmarks").textContent = String(data.summary.reproduced_known);
  }
  async function start() {
    try {
      const response = await fetch("./data/portfolio.json", {cache:"no-store"});
      if (!response.ok) throw new Error("HTTP " + response.status);
      const data = await response.json();
      if (!data || !Array.isArray(data.problems) || data.problems.length !== 100 ||
          !Array.isArray(data.execution_queue) || !Array.isArray(data.solved) ||
          !Array.isArray(data.milestones)) throw new Error("Malformed portfolio snapshot");
      state.all = data.problems;
      for (const field of [...new Set(state.all.map(p => p.field))].sort()) {
        const opt = document.createElement("option");
        opt.value = field;
        opt.textContent = field;
        $("filter-field").appendChild(opt);
      }
      $("stat-total").textContent = String(data.problems.length);
      $("stat-campaigns").textContent = String(data.summary.campaigns);
      $("snapshot-date").textContent = "Latest recorded source intake: " +
        (data.source_review_as_of || "varies") + ".";
      for (const id of ["search-problems","filter-field","filter-status","sort-problems"]) {
        $(id).addEventListener(id === "search-problems" ? "input" : "change", filterChanged);
      }
      $("reset-filters").addEventListener("click", () => {
        $("search-problems").value = ""; $("filter-field").value = "";
        $("filter-status").value = ""; $("sort-problems").value = "execution";
        filterChanged(); $("search-problems").focus();
      });
      $("load-more").addEventListener("click", () => {
        state.limit += 20; renderProblems();
      });
      renderQueue(data);
      renderSolved(data);
      renderMilestones(data);
      const focus = new URLSearchParams(location.search).get("focus");
      if (focus && state.all.some(p => p.id === focus)) {
        state.limit = 100;
        renderProblems();
        const entry = $("problem-" + focus);
        if (entry) {
          entry.open = true;
          requestAnimationFrame(() => entry.scrollIntoView({block:"center",behavior:"auto"}));
        }
      } else {
        renderProblems();
      }
    } catch (error) {
      $("problem-list").textContent = "Portfolio data could not be loaded; view the source registry on GitHub.";
      $("results-count").textContent = "Registry unavailable";
      $("execution-queue").textContent = "Proof queue unavailable";
      $("solved-list").textContent = "Solved archive unavailable";
      $("milestone-list").textContent = "Verification milestones unavailable";
      console.error("Portfolio failed to load",error);
    }
  }
  start();
})();
