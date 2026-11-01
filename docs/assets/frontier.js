"use strict";
/*
 * Erdős-inspired proof frontier. Progressive enhancement over the generated
 * dossiers: the canonical sources are api/work.json and api/problems.json.
 * Never infer that a proposed obligation is proved, new, or actually open.
 * The static site remains fully usable without JavaScript or these requests.
 */
(() => {
  const root = document.documentElement.dataset.root || "./";
  const problem = document.querySelector(".problem-page .problem-main");
  const index = document.querySelector("#problem-list");
  const atlas = /\/atlas\/(?:index\.html)?$/.test(location.pathname);
  if (!problem && !index && !atlas) return;

  const node = (tag, className, value) => {
    const n = document.createElement(tag);
    if (className) n.className = className;
    if (value != null) n.textContent = String(value);
    return n;
  };
  const link = (href, text, cls) => {
    const a = node("a", cls, text);
    a.href = href;
    return a;
  };
  const local = path => root + path;
  const fetchData = async path => {
    const response = await fetch(local(path));
    if (!response.ok) throw new Error("Frontier data unavailable: " + response.status);
    return response.json();
  };
  const heading = (level, value, cls) => node(level, cls, value);
  const paragraph = (value, cls) => node("p", cls, value);
  const statusLabel = {
    runnable: "Runnable now",
    externally_blocked: "Externally blocked",
    waiting_on_dependencies: "Waiting on prerequisites"
  };
  const statusOrder = { runnable: 0, externally_blocked: 1, waiting_on_dependencies: 2 };
  const order = (a, b) => (statusOrder[a.status] ?? 9) - (statusOrder[b.status] ?? 9) ||
    (a.priority_rank || 999) - (b.priority_rank || 999) || a.id.localeCompare(b.id);
  const workHref = item => local("work/" + encodeURIComponent(item.id) + "/");
  const problemHref = item => local("problems/" + encodeURIComponent(item.id) + "/");
  const detail = (parent, label, value) => {
    if (!value) return;
    const div = node("div", "frontier-fact");
    div.append(heading("h3", label), paragraph(value));
    parent.append(div);
  };
  const appendWorkLink = (parent, item) => {
    parent.append(link(workHref(item), item.id + " · " + item.title, "frontier-link"));
  };

  function problemWorkbench(pid, work, problems, record) {
    const obligations = work.items.filter(w => w.kind === "obligation" && w.problems.includes(pid)).sort(order);
    const lead = obligations[0] || null;
    const peers = problems.problems.filter(p => p.id !== pid && p.method_id === record.method_id)
      .sort((a, b) => a.dispatch_rank - b.dispatch_rank).slice(0, 5);
    const section = node("section", "dossier-block frontier-workbench");
    section.id = "breakthrough";
    section.append(paragraph("PROOF FRONTIER / THE SMALLEST MISSING STEP", "frontier-eyebrow"));
    section.append(heading("h2", lead ? "One implication worth attacking" : "Turn this question into a testable step"));
    section.append(paragraph(
      "A research target is not an established result. The precise boundary, falsifier and review conditions matter as much as the proposed proof.",
      "muted"));

    const focus = node("div", "frontier-focus");
    if (lead) {
      const label = node("div", "frontier-status");
      label.append(node("span", "frontier-status-indicator " + lead.status, statusLabel[lead.status] || lead.status),
        node("code", "", lead.id));
      focus.append(label);
      focus.append(heading("h3", "Statement to establish (not a theorem)"));
      focus.append(paragraph(lead.context || lead.deliverable, "frontier-statement"));
      const facts = node("div", "frontier-facts");
      detail(facts, "Published / known boundary", lead.boundary);
      detail(facts, "How this could fail", lead.falsifier);
      detail(facts, "Next concrete deliverable", lead.deliverable);
      focus.append(facts);
      if (lead.depends_on && lead.depends_on.length) {
        const dependencies = node("div", "frontier-deps");
        dependencies.append(heading("h3", "Required first"));
        const ul = node("ul", "frontier-dependency-list");
        lead.depends_on.forEach(id => {
          const item = work.items.find(w => w.id === id);
          const li = node("li", "");
          if (item) {
            li.append(link(workHref(item), id), node("span", "", " · " + (statusLabel[item.status] || item.status)));
          } else {
            li.textContent = id + " · outside the active work queue; inspect the source ledger";
          }
          ul.append(li);
        });
        dependencies.append(ul);
        focus.append(dependencies);
      }
      const actions = node("div", "frontier-actions");
      actions.append(link(workHref(lead), "Inspect scope and acceptance →", "button button-dark"));
      if (lead.status === "runnable") {
        actions.append(link(lead.existing_claims_url, "Check existing claims ↗", "button button-outline"));
      }
      focus.append(actions);
    } else {
      focus.append(heading("h3", "First mathematical move"));
      focus.append(paragraph(record.campaign?.first_proof_obligation || record.dispatch_next ||
        "Specify one restricted, falsifiable claim and its independent checker before launching a search.", "frontier-statement"));
      detail(focus, "Known boundary", record.campaign?.blocker || record.dispatch_why);
      detail(focus, "Falsifier to check", record.campaign?.falsification);
      detail(focus, "Next concrete step", record.dispatch_next);
      focus.append(paragraph("No individual proof-obligation node has yet been recorded for this problem. This is a proposed first attack, not a certified missing lemma.", "muted"));
      focus.append(link(local("work/"), "Browse and claim a bounded task →", "frontier-link"));
    }
    section.append(focus);

    if (obligations.length > 1) {
      const more = node("div", "frontier-more");
      more.append(heading("h3", "Other proof obligations · " + (obligations.length - 1)));
      const ul = node("ul", "frontier-compact-list");
      obligations.slice(1).forEach(w => {
        const li = node("li", "");
        appendWorkLink(li, w);
        li.append(node("span", "frontier-small-state", statusLabel[w.status] || w.status));
        ul.append(li);
      });
      more.append(ul);
      section.append(more);
    }

    const connections = node("div", "frontier-connections");
    connections.append(heading("h3", "A reusable attack template"));
    connections.append(paragraph("Shared method: " + record.method_title +
      ". These are methodological connections, not proved implications between conjectures.", "muted"));
    if (peers.length) {
      const ul = node("ul", "frontier-peer-list");
      peers.forEach(p => {
        const li = node("li", "");
        li.append(link(problemHref(p), p.id + " · " + p.name, "frontier-link"));
        li.append(paragraph(p.dispatch_next || p.first_attack, "frontier-peer-note"));
        ul.append(li);
      });
      connections.append(ul);
    }
    connections.append(link(local("atlas/") + "#frontier-methods", "Explore other method families →", "frontier-link"));
    section.append(connections);
    problem.prepend(section);

    const toc = document.querySelector(".problem-side .toc ol");
    if (toc) {
      const li = node("li", "");
      li.append(link("#breakthrough", "Next breakthrough"));
      toc.prepend(li);
    }
  }

  function homepage(work) {
    const runnable = work.items.filter(w => w.kind === "obligation" && w.status === "runnable")
      .sort(order).slice(0, 3);
    if (!runnable.length) return;
    const target = document.querySelector(".next-band") || document.querySelector(".rankings");
    if (!target) return;
    const section = node("section", "section-block frontier-home");
    section.id = "frontier-tasks";
    section.append(paragraph("THE PROOF FRONTIER / OPEN, FALSIFIABLE WORK", "frontier-eyebrow"));
    section.append(heading("h2", "One missing implication at a time."));
    section.append(paragraph("These are proposed mathematical obligations, not accepted theorems. Each has an explicit statement, boundary and independent review gate."));
    const list = node("ol", "frontier-home-grid");
    runnable.forEach(w => {
      const item = node("li", "frontier-home-card");
      item.append(node("span", "frontier-eyebrow", w.id + " · " + w.problems.join(", ")));
      item.append(link(workHref(w), w.context || w.title, "frontier-home-title"));
      item.append(paragraph(w.deliverable, "muted"));
      list.append(item);
    });
    section.append(list, link(local("work/"), "See all claimable research tasks →", "frontier-link"));
    target.before(section);
  }

  function atlasExplorer(problems) {
    const anchor = document.querySelector(".page-head") || document.querySelector(".atlas-page") ||
      document.querySelector("main h1");
    if (!anchor) return;
    const families = new Map();
    problems.problems.forEach(p => {
      if (!p.method_id) return;
      if (!families.has(p.method_id)) families.set(p.method_id, { title: p.method_title, items: [] });
      families.get(p.method_id).items.push(p);
    });
    if (!families.size) return;
    const section = node("section", "section-block frontier-atlas");
    section.id = "frontier-methods";
    section.append(paragraph("CROSS-PROBLEM REUSE / NOT PROOF IMPLICATIONS", "frontier-eyebrow"));
    section.append(heading("h2", "Explore the shared attack shapes"));
    section.append(paragraph("Choose a research method to see the conjectures it touches. An edge means a reusable template, not that solving one conjecture proves another.", "muted"));
    const field = node("div", "frontier-picker");
    const lab = node("label", "", "Research method");
    lab.htmlFor = "frontier-family";
    const select = node("select", "");
    select.id = "frontier-family";
    Array.from(families, ([id, group]) => ({ id, ...group }))
      .sort((a, b) => b.items.length - a.items.length || a.title.localeCompare(b.title))
      .forEach(group => {
        const option = node("option", "", group.title + " · " + group.items.length + " problems");
        option.value = group.id;
        select.append(option);
      });
    field.append(lab, select);
    section.append(field);
    const body = node("div", "frontier-family-body");
    section.append(body);
    const draw = () => {
      body.replaceChildren();
      const group = families.get(select.value);
      if (!group) return;
      body.append(paragraph(group.items.length + " research targets share this template. No mathematical transfer has been certified by this grouping.", "muted"));
      const ul = node("ul", "frontier-atlas-list");
      group.items.sort((a, b) => a.dispatch_rank - b.dispatch_rank).forEach(p => {
        const li = node("li", "");
        li.append(link(problemHref(p), p.id + " · " + p.name, "frontier-link"));
        li.append(node("span", "frontier-small-state", p.evidence_state.replaceAll("_", " ")));
        ul.append(li);
      });
      body.append(ul);
    };
    select.addEventListener("change", draw);
    draw();
    const container = anchor.closest("section") || anchor;
    container.after(section);
  }

  if (problem) {
    const match = location.pathname.match(/\/problems\/(M\d{3})\/?(?:index\.html)?$/);
    if (!match) return;
    Promise.all([fetchData("api/work.json"), fetchData("api/problems.json"),
      fetchData("api/problems/" + match[1] + ".json")])
      .then(([work, problems, record]) => problemWorkbench(match[1], work, problems, record))
      .catch(() => { /* The server-rendered dossier remains available. */ });
  } else if (index) {
    fetchData("api/work.json").then(homepage).catch(() => {});
  } else if (atlas) {
    fetchData("api/problems.json").then(atlasExplorer).catch(() => {});
  }
})();
