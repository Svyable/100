"use strict";
(() => {
  const byId = id => document.getElementById(id);
  const escapeHTML = value => String(value ?? "").replace(/[&<>"']/g, ch =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  const state = {all:[],found:[],limit:24};
  const names = {formalize:"Needs formalization",prior_art_review:"Prior-art review needed"};
  const fieldText = item => [item.id,item.title,item.statement,item.domain,item.consequence,
    item.first_attack,...item.spillovers].join(" ").toLocaleLowerCase();
  function renderCard(c) {
    const card = document.createElement("article");
    const promotion = c.promoted_to;
    card.className = "next-card" + (promotion ? " next-card-promoted" : "");
    card.id = "candidate-" + c.id;
    const title = escapeHTML(c.title), id = escapeHTML(c.id);
    const lanes = c.spillovers.map(s => "<span>" + escapeHTML(s) + "</span>").join("");
    const issue = "https://github.com/Svyable/100/issues/new?title=" +
      encodeURIComponent("Next 100 review: " + c.id);
    card.innerHTML =
      '<div class="next-card-head"><span class="next-card-id">' + id + '</span>' +
      '<div class="next-card-title"><h3>' + title + '</h3><p>' + escapeHTML(c.domain) +
      ' · ' + escapeHTML(names[c.stage] || "Unvetted") + '</p></div>' +
      '<div class="next-card-score"><strong>' + c.score + '</strong><small>DISCOVERY INDEX</small></div></div>' +
      '<p>' + escapeHTML(c.statement) + '</p><div class="next-lanes">' + lanes + '</div>' +
      '<details><summary>Why this matters / first test / evidence limits</summary>' +
      '<div class="next-card-detail"><div><b>IF ESTABLISHED</b><p>' +
      escapeHTML(c.consequence) + '</p><b>REVIEW STATE</b><p>Unvetted hypothesis. Not certified open, novel, or true.' +
      (promotion ? ' Promoted to active slot ' + escapeHTML(promotion) + '.' : '') +
      '</p></div><div><b>FIRST ATTACK</b><p>' + escapeHTML(c.first_attack) +
      '</p><b>EDITORIAL METRICS (1–5)</b><p>Impact ' + c.scores.impact +
      ' · Tractability ' + c.scores.tractability + ' · Verifiability ' + c.scores.verifiability +
      ' · Transfer ' + c.scores.transfer + '</p><a href="' + issue +
      '" target="_blank" rel="noopener noreferrer">Submit review ↗</a>' +
      '<a href="?focus=' + encodeURIComponent(c.id) + '#reservoir">Direct link ↗</a>' +
      (promotion ? '<a href="../?focus=' + encodeURIComponent(promotion) +
      '#rankings">Active entry ↗</a>' : '') + '</div></div></details>';
    return card;
  }
  function filtered() {
    const search = byId("next-search").value.trim().toLocaleLowerCase();
    const domain = byId("next-domain").value, stage = byId("next-stage").value;
    const status = byId("next-status").value, sort = byId("next-sort").value;
    let rows = state.all.filter(p => (!search || fieldText(p).includes(search)) &&
      (!domain || p.domain === domain) && (!stage || p.stage === stage) &&
      (status === "all" || (status === "promoted" ? !!p.promoted_to : !p.promoted_to)));
    const scoreSort = key => (a,b) => b.scores[key]-a.scores[key] ||
      a.discovery_rank-b.discovery_rank;
    if (sort === "tractability" || sort === "impact") rows.sort(scoreSort(sort));
    else if (sort === "name") rows.sort((a,b) => a.title.localeCompare(b.title));
    else if (sort === "id") rows.sort((a,b) => a.id.localeCompare(b.id));
    state.found = rows;
  }
  function render() {
    const list = byId("next-list");
    list.replaceChildren();
    for (const item of state.found.slice(0,state.limit)) list.appendChild(renderCard(item));
    if (!state.found.length) {
      const none = document.createElement("p");
      none.className = "next-empty";
      none.textContent = "No hypotheses match. Try clearing one or more filters.";
      list.appendChild(none);
    }
    byId("next-results").textContent = state.found.length +
      " of " + state.all.length + " hypotheses · " +
      Math.min(state.found.length,state.limit) + " displayed";
    byId("next-more").hidden = state.limit >= state.found.length;
  }
  function change() {state.limit=24;filtered();render();}
  function focusCandidate(id) {
    if (!/^N[0-9]{4,}$/.test(id) || !state.all.some(p=>p.id===id)) return;
    byId("next-status").value="all";
    byId("next-search").value=id;
    byId("next-domain").value="";
    byId("next-stage").value="";
    change();
    const el=byId("candidate-"+id);
    if(el) {el.querySelector("details").open=true;el.scrollIntoView({block:"center"});}
  }
  async function start() {
    try {
      const response=await fetch("../data/next.json",{cache:"no-cache"});
      if(!response.ok) throw Error("Snapshot unavailable: "+response.status);
      const data=await response.json();
      if(!Array.isArray(data.candidates)) throw Error("Invalid snapshot");
      state.all=data.candidates;
      byId("hero-count").textContent=data.count.toLocaleString();
      byId("stat-available").textContent=data.available_count.toLocaleString();
      byId("stat-domains").textContent=data.domains.length.toLocaleString();
      byId("stat-promoted").textContent=data.promoted_count.toLocaleString();
      for(const domain of data.domains) {
        const opt=document.createElement("option");
        opt.value=domain;opt.textContent=domain;byId("next-domain").appendChild(opt);
      }
      for(const id of ["next-search","next-domain","next-stage","next-status","next-sort"])
        byId(id).addEventListener(id==="next-search"?"input":"change",change);
      byId("next-reset").addEventListener("click",()=>{
        byId("next-search").value="";byId("next-domain").value="";
        byId("next-stage").value="";byId("next-status").value="available";
        byId("next-sort").value="priority";change();byId("next-search").focus();
      });
      byId("next-more").addEventListener("click",()=>{state.limit+=24;render();});
      change();
      focusCandidate(new URLSearchParams(location.search).get("focus") || "");
    } catch(error) {
      byId("next-list").textContent="Unable to load the reservoir; inspect the canonical records on GitHub.";
      byId("next-results").textContent="Snapshot unavailable";
      console.error(error);
    }
  }
  start();
})();
