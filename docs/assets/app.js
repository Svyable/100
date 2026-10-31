"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const evidenceNames = Object.freeze({
    official_open: "Officially open",
    verified_open: "Specialist verified",
    needs_review: "Needs review",
    claim_needs_review: "Claim under review"
  });
  const modalityNames = Object.freeze({
    finite_refutable: "Finitely refutable",
    finite_parameter: "Finite parameter",
    existence_family: "Existence family",
    asymptotic: "Asymptotic",
    structural: "Structural"
  });
  let campaignIds = new Set();
  let verifiedIds = new Set();
  const state = {
    all: [], filtered: [], limit: 20, sort: "dispatch",
    search: "", field: "", status: "", modality: ""
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
      '<span class="entry-index"><span class="ordinal">' + p.dispatch_rank +
      '</span><span class="entry-id">' + escapeHTML(p.id) + '</span></span>' +
      '<span class="entry-info"><span class="entry-name">' + escapeHTML(p.name) +
      '</span><span class="entry-field">' + escapeHTML(p.field) + '</span></span>' +
      '<span class="entry-score" aria-label="Dispatch score ' + p.dispatch_score +
      ': editorial ' + p.score + ', readiness plus ' + p.readiness +
      ', action bonus ' + p.action_bonus + '">' +
      '<strong>' + p.dispatch_score + '</strong><span class="small-bar" aria-hidden="true">' +
      '<i style="width:' + Math.min(100, Math.round(p.dispatch_score * 100 / 140)) +
      '%"></i></span></span>' +
      '<span><span class="status-pill status-' + knownStatus + '">' + evidenceName(p) +
      '</span></span><span class="entry-chevron" aria-hidden="true">+</span></summary>' +
      '<div class="entry-detail"><div><span class="detail-label">THE OPEN QUESTION</span>' +
      '<p class="detail-question">' + escapeHTML(p.question) + '</p>' +
      '<span class="detail-label">DO THIS NEXT</span>' +
      '<p class="detail-attack">' + escapeHTML(p.dispatch_next) + '</p>' +
      '<span class="detail-label">CURRENT FIRST ATTACK</span>' +
      '<p class="detail-attack">' + escapeHTML(p.first_attack) + '</p>' +
      '<div class="detail-links">' + links + '</div></div>' +
      '<div><span class="detail-label">PRIORITY DECOMPOSITION</span>' +
      '<p class="detail-note"><span class="action-pill">' + escapeHTML(p.action_label) +
      '</span></p>' +
      '<p class="detail-note"><strong>Dispatch rank:</strong> #' + p.dispatch_rank +
      ' · <strong>Shape:</strong> ' + escapeHTML(p.method_title) +
      ' (<code>' + escapeHTML(p.method_id) + '</code>)</p>' +
      '<p class="detail-note">' + escapeHTML(p.dispatch_why) + '</p>' +
      '<p class="detail-note"><strong>Editorial rank:</strong> #' + p.rank +
      ' · <strong>Readiness rank:</strong> #' + p.execution_rank + '</p>' +
      '<p class="detail-note"><strong>Editorial score:</strong> ' + p.score +
      ' · <strong>Readiness:</strong> +' + p.readiness +
      ' · <strong>Action bonus:</strong> ' + (p.action_bonus > 0 ? '+' : '') + p.action_bonus +
      ' · <strong>Dispatch score:</strong> ' + p.dispatch_score +
      ' · <strong>Execution index:</strong> ' + p.execution_score + '</p>' +
      '<div class="detail-metrics">' +
      metric("Impact",p.impact) + metric("Attackability",p.attackability) +
      metric("Verifiability",p.verifiability) + metric("Spillover",p.spillover) +
      '</div><p class="detail-note"><strong>Computation:</strong> ' +
      escapeHTML(modalityNames[p.modality] || "Unclassified") +
      (verifiedIds.has(p.id) ? ' · exact verifier in the probe lab' : '') + '.</p>' +
      '<p class="detail-note"><strong>Evidence:</strong> ' +
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
    if (state.sort === "dispatch") return a.dispatch_rank - b.dispatch_rank;
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
      (!state.modality || p.modality === state.modality) &&
      (!query || [p.id,p.name,p.field,p.question,p.first_attack,p.action,
        p.action_label,p.method_id,p.method_title,p.dispatch_next].some(
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
    state.modality = $("filter-modality").value;
    state.sort = $("sort-problems").value;
    state.limit = 20;
    renderProblems();
  }
  function renderCampaigns(data) {
    const root = $("campaign-grid");
    const active = new Map(data.problems.map(p => [p.id,p]));
    const campaigns = data.campaigns
      .filter(c => active.has(c.problem_id))
      .sort((a,b) => active.get(a.problem_id).dispatch_rank -
                      active.get(b.problem_id).dispatch_rank);
    const fragment = document.createDocumentFragment();
    for (const [i,c] of campaigns.entries()) {
      const p = active.get(c.problem_id);
      const card = document.createElement("article");
      card.className = "campaign-card" + (i === 0 ? " campaign-feature" : "") +
        (campaigns.length > 2 && i === campaigns.length - 1 && campaigns.length % 2 ? " campaign-wide" : "");
      const dossier = repoFile(c.dossier);
      card.innerHTML =
        '<div class="campaign-top"><span>CAMPAIGN ' +
        String(i+1).padStart(2,"0") + ' / ' + escapeHTML(c.method) +
        '</span><span class="campaign-mark">↗</span></div>' +
        '<span class="campaign-code">' + escapeHTML(c.problem_id) +
        ' · DISPATCH #' + p.dispatch_rank + '</span>' +
        '<h3>' + escapeHTML(p.name) + '</h3>' +
        '<p>' + escapeHTML(c.first_proof_obligation) + '</p>' +
        '<div class="campaign-tags"><span>' + escapeHTML(p.field) + '</span>' +
        '<span>' + escapeHTML(c.stage.replaceAll("_"," ")) + '</span></div>' +
        (dossier ? '<a href="' + escapeHTML(dossier) +
          '" target="_blank" rel="noopener noreferrer">Read campaign ↗</a>' : '');
      fragment.appendChild(card);
    }
    if (!campaigns.length) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No active research campaigns currently defined.";
      fragment.appendChild(empty);
    }
    root.replaceChildren(fragment);
  }
  function renderQueue(data) {
    const root = $("execution-queue");
    const fragment = document.createDocumentFragment();
    for (const c of data.execution_queue) {
      const card = document.createElement("article");
      card.className = "execution-card";
      const dossierUrl = repoFile(c.dossier);
      card.innerHTML =
        '<div class="execution-card-top"><span>DISPATCH #' + c.dispatch_rank +
        ' · ' + escapeHTML(c.problem_id) + '</span>' +
        '<span class="execution-score">' + escapeHTML(c.action_label) + '</span></div>' +
        '<h3>' + escapeHTML(c.name) + '</h3>' +
        '<span class="step-label">FIRST PROOF OBLIGATION</span>' +
        '<p>' + escapeHTML(c.first_proof_obligation) + '</p>' +
        '<span class="step-label">RECOMMENDED STEP</span>' +
        '<p>' + escapeHTML(c.next_experiment) + '</p>' +
        (c.recorded_experiment && c.recorded_experiment !== c.next_experiment ?
          '<span class="step-label">NOT THE CURRENT RECOMMENDATION</span><p>' +
          escapeHTML(c.recorded_experiment) + '</p>' : '') +
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
  function renderLab(data) {
    const lab = data.lab;
    const names = new Map(data.problems.map(p => [p.id, p.name]));
    $("lab-stat-covered").textContent = String(lab.covered_problems.length);
    $("lab-stat-computable").textContent =
      lab.computable_problems.filter(id => lab.covered_problems.includes(id)).length +
      "/" + lab.computable_problems.length;
    $("lab-stat-probes").textContent = String(lab.probes.length);
    $("lab-stat-engines").textContent = String(lab.engines.length);
    const probeRoot = document.createDocumentFragment();
    for (const probe of lab.probes) {
      const run = probe.runs.deep || probe.runs.smoke;
      const card = document.createElement("article");
      card.className = "milestone-card";
      const artifact = repoFile(probe.artifact);
      card.innerHTML = '<span class="milestone-type">' + escapeHTML(probe.problem_id) +
        ' · ' + (run && run.holds ? "VERIFIED FINITE RANGE" : "NEEDS ATTENTION") + '</span>' +
        '<h4>' + escapeHTML(probe.name) + '</h4>' +
        '<p>' + escapeHTML(run ? run.scope : "Not yet run.") + '</p>' +
        '<p class="probe-frontier">' + escapeHTML(probe.frontier) + '</p>' +
        '<div class="probe-engines">' + probe.engines.map(e => '<span>' + escapeHTML(e) + '</span>').join("") + '</div>' +
        '<code>' + escapeHTML(probe.command) + '</code>' +
        (artifact ? '<a href="' + escapeHTML(artifact) +
          '" target="_blank" rel="noopener noreferrer">Inspect search and checker ↗</a>' : '');
      probeRoot.appendChild(card);
    }
    $("lab-probe-list").replaceChildren(probeRoot);
    const engineRoot = document.createDocumentFragment();
    for (const engine of lab.engines) {
      const row = document.createElement("div");
      row.className = "lab-row";
      row.innerHTML = '<div><h4>' + escapeHTML(engine.name) + '</h4><code>' + escapeHTML(engine.id) + '</code></div>' +
        '<p>' + escapeHTML(engine.use) + '</p>' +
        '<div class="chips">' + engine.problems.map(id =>
          '<span title="' + escapeHTML(names.get(id) || id) + '">' + escapeHTML(id) + '</span>').join("") + '</div>';
      engineRoot.appendChild(row);
    }
    $("lab-engine-list").replaceChildren(engineRoot);
    const roadRoot = document.createDocumentFragment();
    for (const entry of lab.roadmap) {
      const row = document.createElement("div");
      row.className = "lab-row";
      row.innerHTML = '<div><h4>' + escapeHTML(entry.problem_id) + ' · ' + escapeHTML(entry.name) + '</h4>' +
        '<code>' + escapeHTML(entry.engine) + '</code></div>' +
        '<p>' + escapeHTML(entry.first_probe) + '</p><div class="chips"><span>ENGINE TO BUILD</span></div>';
      roadRoot.appendChild(row);
    }
    if (!lab.roadmap.length) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "Every computable problem has an exact probe.";
      roadRoot.appendChild(empty);
    }
    $("lab-roadmap").replaceChildren(roadRoot);
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
  function renderRoadmap(data) {
    const rm = data.roadmap;
    const names = new Map(data.problems.map(p => [p.id, p.name]));
    const metrics = document.createDocumentFragment();
    for (const m of rm.metrics) {
      const el = document.createElement("div");
      el.className = "roadmap-metric";
      const pct = m.target ? Math.min(100, Math.round(100 * m.value / m.target)) : 0;
      el.innerHTML = '<strong>' + m.value + (m.target !== null ? '<small> / ' + m.target + '</small>' : '') +
        '</strong><span>' + escapeHTML(m.label) + '</span>' +
        (m.target !== null ? '<div class="meter" role="img" aria-label="' + pct + '% of target"><i style="width:' + pct + '%"></i></div>'
                           : '<em class="roadmap-note">No target: review only</em>');
      metrics.appendChild(el);
    }
    $("roadmap-metrics").replaceChildren(metrics);
    const trackName = new Map(rm.tracks.map(t => [t.id, t.name]));
    let active = "";
    const titles = {shipped:"Shipped", now:"Now", next:"Next", later:"Later"};
    function board() {
      const frag = document.createDocumentFragment();
      for (const h of Object.keys(rm.horizons)) {
        const col = document.createElement("div");
        col.className = "roadmap-col roadmap-" + h;
        const items = rm.items.filter(i => i.horizon === h && (!active || i.track === active));
        col.innerHTML = '<div class="roadmap-col-head"><b>' + titles[h] + '</b><span>' + items.length +
          '</span></div><p class="roadmap-col-note">' + escapeHTML(rm.horizons[h]) + '</p>';
        for (const it of items) {
          const card = document.createElement("article");
          card.className = "roadmap-card";
          const url = repoFile(it.evidence);
          const probs = it.problems.slice(0, 5).map(p =>
            '<a href="?focus=' + escapeHTML(p) + '#rankings" title="' + escapeHTML(names.get(p) || p) + '">' + escapeHTML(p) + '</a>').join("");
          card.innerHTML = '<span class="roadmap-card-top">' + escapeHTML(it.id) + ' · ' +
            escapeHTML(trackName.get(it.track)) + '</span><h4>' + escapeHTML(it.title) + '</h4>' +
            '<p>' + escapeHTML(it.outcome) + '</p>' +
            (it.exit ? '<p class="roadmap-exit"><b>Done when</b> ' + escapeHTML(it.exit) + '</p>' : '') +
            (probs ? '<div class="chips">' + probs + (it.problems.length > 5 ? '<span>+' + (it.problems.length - 5) + '</span>' : '') + '</div>' : '') +
            (url ? '<a class="roadmap-evidence" href="' + escapeHTML(url) + '" target="_blank" rel="noopener noreferrer">Evidence ↗</a>' : '');
          col.appendChild(card);
        }
        frag.appendChild(col);
      }
      $("roadmap-board").replaceChildren(frag);
    }
    const filters = $("roadmap-tracks");
    for (const t of [{id:"", name:"All tracks"}, ...rm.tracks]) {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = t.name;
      b.setAttribute("aria-pressed", String(t.id === active));
      if (t.goal) b.title = t.goal;
      b.addEventListener("click", () => {
        active = t.id;
        for (const x of filters.children) x.setAttribute("aria-pressed", String(x === b));
        board();
      });
      filters.appendChild(b);
    }
    board();
  }
  function renderApproach(data) {
    const root = $("approach-jobs");
    if (!root) return;
    const fragment = document.createDocumentFragment();
    data.approach.jobs.slice(0, 8).forEach((job, i) => {
      const card = document.createElement("article");
      card.className = "execution-card";
      const ids = job.problem_ids.map(id =>
        '<a href="?focus=' + encodeURIComponent(id) + '#rankings">' + escapeHTML(id) + '</a>'
      ).join(" ");
      card.innerHTML =
        '<div class="execution-card-top"><span>JOB ' + String(i + 1).padStart(2, "0") +
        '</span><span class="execution-score">' + escapeHTML(job.action_label) + '</span></div>' +
        '<h3>' + escapeHTML(job.method_title) + '</h3>' +
        '<p class="approach-note">' + ids + '</p>' +
        '<p>' + escapeHTML(job.summary) + '</p>';
      fragment.appendChild(card);
    });
    root.replaceChildren(fragment);
  }
  async function start() {
    try {
      const response = await fetch("./data/portfolio.json", {cache:"no-store"});
      if (!response.ok) throw new Error("HTTP " + response.status);
      const data = await response.json();
      if (!data || !Array.isArray(data.problems) || data.problems.length !== 100 ||
          !Array.isArray(data.execution_queue) || !Array.isArray(data.solved) ||
          !Array.isArray(data.milestones) || !data.lab ||
          !Array.isArray(data.lab.probes) ||
          !data.roadmap || !Array.isArray(data.roadmap.items) ||
          !data.approach || !Array.isArray(data.approach.jobs)) throw new Error("Malformed portfolio snapshot");
      state.all = data.problems;
      campaignIds = new Set(data.campaigns.map(c => c.problem_id));
      verifiedIds = new Set(data.lab.covered_problems);
      for (const field of [...new Set(state.all.map(p => p.field))].sort()) {
        const opt = document.createElement("option");
        opt.value = field;
        opt.textContent = field;
        $("filter-field").appendChild(opt);
      }
      $("stat-total").textContent = String(data.problems.length);
      $("stat-campaigns").textContent = String(data.summary.campaigns);
      $("status-claim-count").textContent = String(data.status_counts.claim_needs_review || 0);
      $("snapshot-date").textContent = "Latest recorded source intake: " +
        (data.source_review_as_of || "varies") + ".";
      for (const id of ["search-problems","filter-field","filter-status","filter-modality","sort-problems"]) {
        $(id).addEventListener(id === "search-problems" ? "input" : "change", filterChanged);
      }
      $("reset-filters").addEventListener("click", () => {
        $("search-problems").value = ""; $("filter-field").value = "";
        $("filter-status").value = ""; $("filter-modality").value = "";
        $("sort-problems").value = "dispatch";
        filterChanged(); $("search-problems").focus();
      });
      $("load-more").addEventListener("click", () => {
        state.limit += 20; renderProblems();
      });
      renderCampaigns(data);
      renderApproach(data);
      renderLab(data);
      renderQueue(data);
      renderRoadmap(data);
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
      $("campaign-grid").textContent = "Campaigns unavailable";
      $("lab-probe-list").textContent = "Probe lab unavailable";
      $("execution-queue").textContent = "Proof queue unavailable";
      const jobs = $("approach-jobs");
      if (jobs) jobs.textContent = "Cohort jobs unavailable";
      $("roadmap-board").textContent = "Roadmap unavailable";
      $("solved-list").textContent = "Solved archive unavailable";
      $("milestone-list").textContent = "Verification milestones unavailable";
      console.error("Portfolio failed to load",error);
    }
  }
  start();
})();
