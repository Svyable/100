/* Evidence-first, progressively enhanced research frontier and agent handoff.
 * Only reads the committed static site /api/work.json. Does not modify evidence. */
(function () {
  "use strict";

  const safeId = id => typeof id === "string" && /^[A-Za-z0-9][A-Za-z0-9-]*$/.test(id);
  const list = value => Array.isArray(value) ? value : [];
  const clean = value => typeof value === "string" ? value.trim() : "";

  function formatPacket(item) {
    if (!item || !safeId(item.id) || !clean(item.scope_sha256)) {
      throw new Error("Work item lacks a stable id or scope digest");
    }
    const lines = [
      "# 100 / Bounded research handoff",
      "",
      "Work item: " + item.id,
      "Title: " + clean(item.title),
      "Kind: " + clean(item.kind),
      "Dispatch status: " + clean(item.status),
      "Problems: " + list(item.problems).join(", "),
      "Scope SHA-256: " + item.scope_sha256,
      "Source ledger: " + clean(item.source),
      "",
      "## Before starting",
      "Check for an existing [Claim] issue. Do not start a duplicate claim.",
      clean(item.existing_claims_url),
      "If no open claim exists, use: " + clean(item.open_claim_url),
      "Treat the scope digest as an identity guard, not as proof.",
      ""
    ];
    if (item.status !== "runnable") {
      lines.push("NOT READY TO DISPATCH: this item is " + clean(item.status) +
        ". Resolve its prerequisites or external block before doing the deliverable.", "");
    }
    const fields = [
      ["Deliverable", item.deliverable],
      ["Mathematical context", item.context],
      ["Prior-art and scope boundary", item.boundary],
      ["Falsifier", item.falsifier]
    ];
    for (const pair of fields) {
      if (clean(pair[1])) lines.push("## " + pair[0], clean(pair[1]), "");
    }
    lines.push("## Acceptance criteria");
    for (const requirement of list(item.acceptance)) lines.push("- " + clean(requirement));
    if (!list(item.acceptance).length) lines.push("- Follow the canonical work-item acceptance contract.");
    lines.push("", "## Dependencies");
    if (list(item.depends_on).length) {
      for (const dependency of item.depends_on) lines.push("- " + clean(dependency));
    } else {
      lines.push("- No dependency IDs recorded in this work item.");
    }
    lines.push("",
      "## Evidence and integrity rules",
      "- Read AGENTS.md and the linked primary sources before editing.",
      "- Preserve exact inputs, source revision, tool versions, resource costs, failures and negative results.",
      "- Search for a counterexample and compare exact theorem scope, assumptions and quantifiers.",
      "- A finite replay is not a universal theorem; a Lean pass validates an encoding, not its fidelity or novelty.",
      "- Do not self-certify an independent review. Record the reviewer and verifiable evidence separately.",
      "- Do not mark a problem Solved on an agent claim, solver result, preprint or finite check.",
      "- Keep changes within the claimed deliverable; record outcome and agent-hours in data/outcomes.json.",
      "- Regenerate derived files; do not hand-edit generated docs/ or verified ledgers.",
      "",
      "## Final verification and handoff",
      "python3 scripts/work.py --id " + item.id,
      "python3 scripts/regen.py",
      "python3 scripts/regen.py --check",
      "python3 -m unittest discover -s tests -v",
      "Report the exact checks that ran (or could not run), the remaining gap, and the claim/PR URL.",
      "No result is independently accepted until the separate review gate passes."
    );
    return lines.join("\n") + "\n";
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { formatPacket, safeId };
  }
  if (typeof document === "undefined") return;

  const root = document.documentElement.dataset.root || "./";
  const select = selector => document.querySelector(selector);
  const all = selector => Array.from(document.querySelectorAll(selector));
  const el = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const anchor = (label, href) => {
    const a = el("a", "", label);
    a.href = href;
    return a;
  };

  let queuePromise;
  function getQueue() {
    if (!queuePromise) {
      queuePromise = fetch(root + "api/work.json", { credentials: "same-origin" })
        .then(response => {
          if (!response.ok) throw new Error("Work queue unavailable (" + response.status + ")");
          return response.json();
        })
        .then(doc => {
          if (!doc || !Array.isArray(doc.items)) throw new Error("Invalid work queue");
          return doc.items;
        })
        .catch(error => {
          queuePromise = null; // Allow an explicit retry if the first request failed.
          throw error;
        });
    }
    return queuePromise;
  }

  const problemMatch = location.pathname.match(/\/problems\/(M\d{3})\/?$/);
  if (problemMatch && select(".problem-grid") && select("#work")) {
    const problemId = problemMatch[1];
    const workSection = select("#work");
    const records = all("#work .work-item");
    const runnable = records.filter(node => node.classList.contains("work-runnable"));
    const waiting = records.filter(node => !node.classList.contains("work-runnable"));
    const reviews = runnable.filter(node => /^V-/.test(node.querySelector(".work-id")?.textContent || ""));
    const obligations = runnable.filter(node => /^O-/.test(node.querySelector(".work-id")?.textContent || ""));
    const reproduced = all("#milestones .milestones > li").length;
    const hasLean = !!select("#formal");

    const section = el("section", "dossier-block proof-frontier");
    section.id = "proof-frontier";
    section.append(el("p", "detail-label", "RESEARCH FRONTIER / EVIDENCE BEFORE CLAIMS"));
    section.append(el("h2", "", "What stands between this question and a proof?"));
    section.append(el("p", "muted",
      "This map summarizes committed evidence and claimable work, not a predicted path to a theorem. A verified finite benchmark does not establish the unrestricted claim."));
    const cards = el("div", "frontier-stages");
    const stages = [
      {
        title: "Formalization", state: hasLean ? "Recorded" : "Not yet recorded",
        detail: hasLean ? "A Lean comparator exists; its mathematical fidelity still requires review." :
          "The registered question remains the reference until a Lean comparator is added.",
        href: hasLean ? "#formal" : "#provenance", link: hasLean ? "Inspect statement" : "Inspect scope"
      },
      {
        title: "Reproduced evidence", state: reproduced + " local milestones",
        detail: "Published benchmarks and independently checked finite cases are not new unrestricted theorems.",
        href: reproduced ? "#milestones" : "#campaign", link: reproduced ? "Inspect milestones" : "Inspect campaign"
      },
      {
        title: "Open proof work", state: obligations.length + " runnable obligations",
        detail: runnable.length + " total runnable items, including " + reviews.length +
          " independent review tasks; " + waiting.length + " currently not runnable.",
        href: "#work", link: "Inspect work queue"
      },
      {
        title: "Acceptance gate", state: "Independent review required",
        detail: "Exact statement scope, reproducibility, novelty and external reviews are checked separately before any full-resolution claim.",
        href: root + "ledger/", link: "Read Solved standard"
      }
    ];
    for (const step of stages) {
      const card = el("div", "frontier-stage");
      card.append(el("h3", "", step.title), el("strong", "frontier-state", step.state),
        el("p", "", step.detail), anchor(step.link, step.href));
      cards.append(card);
    }
    section.append(cards);

    const details = el("details", "frontier-dependencies");
    const summary = el("summary", "", "Inspect recorded dependencies and claimable review tasks");
    const result = el("div", "frontier-dependency-results");
    details.append(summary, result);
    let loaded = false;
    details.addEventListener("toggle", async () => {
      if (!details.open || loaded) return;
      result.replaceChildren(el("p", "muted", "Loading the committed dependency ledger…"));
      try {
        const tasks = (await getQueue()).filter(item =>
          list(item.problems).includes(problemId) &&
          ["obligation", "lean", "review"].includes(item.kind));
        const byId = new Map(tasks.map(item => [item.id, item]));
        const graph = el("ul", "frontier-dependency-list");
        for (const task of tasks) {
          if (!safeId(task.id)) continue;
          const li = el("li", "frontier-dependency-item");
          li.append(anchor(task.id + " · " + clean(task.title),
            root + "work/" + encodeURIComponent(task.id) + "/"));
          li.append(el("span", "frontier-state", clean(task.status).replace(/_/g, " ")));
          const deps = list(task.depends_on).filter(safeId);
          if (deps.length) {
            const part = el("p", "muted");
            part.append("Requires: ");
            deps.forEach((id, i) => {
              if (i) part.append(", ");
              part.append(anchor(id, root + "work/" + encodeURIComponent(id) + "/"));
              if (!byId.has(id)) part.append(" (outside this problem view)");
            });
            li.append(part);
          }
          graph.append(li);
        }
        result.replaceChildren();
        result.append(el("p", "muted",
          "Only recorded dependency edges are shown; a missing edge does not certify mathematical independence."));
        if (graph.children.length) result.append(graph);
        else result.append(el("p", "", "No active proof, Lean or review task in the current queue."));
        loaded = true;
      } catch (error) {
        result.replaceChildren(el("p", "muted",
          "Could not load the dependency ledger. The existing work list remains available."));
        result.append(anchor("Open the machine-readable work queue", root + "api/work.json"));
      }
    });
    section.append(details);
    workSection.before(section);
    const toc = select(".toc ol");
    if (toc) {
      const li = el("li");
      li.append(anchor("Proof frontier", "#proof-frontier"));
      const workLink = toc.querySelector('a[href="#work"]');
      if (workLink && workLink.parentElement) workLink.parentElement.before(li);
      else toc.append(li);
    }
  }

  const workMatch = location.pathname.match(/\/work\/([A-Za-z0-9-]+)\/?$/);
  const workDetail = select(".work-detail");
  if (workMatch && workDetail && safeId(workMatch[1])) {
    const taskId = workMatch[1];
    const block = el("section", "dossier-block agent-handoff");
    block.append(el("h2", "", "Agent-ready handoff"));
    block.append(el("p", "muted",
      "Copy a source-bound, bounded task contract for an AI research agent. This prepares instructions; it does not run an agent, verify a theorem or create a GitHub claim."));
    const details = el("details", "agent-packet");
    const summary = el("summary", "", "Open work packet");
    const slot = el("div", "agent-packet-body");
    details.append(summary, slot);
    let ready = false;
    details.addEventListener("toggle", async () => {
      if (!details.open || ready) return;
      slot.replaceChildren(el("p", "muted", "Reading the canonical work queue…"));
      try {
        const task = (await getQueue()).find(item => item.id === taskId);
        if (!task) throw new Error("Work item not found");
        const packet = formatPacket(task);
        const status = el("p", "agent-packet-status",
          task.status === "runnable" ?
            "Runnable in the committed queue — check GitHub claims before beginning." :
            "Not runnable (" + clean(task.status).replace(/_/g, " ") + "). Resolve the block before dispatch.");
        const label = el("label", "detail-label", "HANDOFF TEXT / SELECT OR COPY");
        const textarea = el("textarea", "agent-packet-text");
        textarea.id = "agent-packet-text";
        textarea.readOnly = true;
        textarea.rows = 14;
        textarea.value = packet;
        label.htmlFor = textarea.id;
        const copyButton = el("button", "button button-outline", "Copy Markdown packet");
        copyButton.type = "button";
        const feedback = el("span", "muted agent-packet-feedback");
        feedback.setAttribute("role", "status");
        copyButton.addEventListener("click", async () => {
          try {
            await navigator.clipboard.writeText(packet);
            feedback.textContent = "Copied. Review the scope and claim status before using.";
          } catch (error) {
            textarea.focus();
            textarea.select();
            feedback.textContent = "Select the text and copy manually.";
          }
        });
        slot.replaceChildren(status, label, textarea, copyButton, feedback);
        ready = true;
      } catch (error) {
        slot.replaceChildren(el("p", "muted", "Could not load this work packet."));
        slot.append(anchor("Read the canonical work queue", root + "api/work.json"));
      }
    });
    block.append(details);
    const claimSection = all(".work-detail > section").find(section =>
      section.querySelector("h2")?.textContent.trim() === "Claim it");
    if (claimSection) claimSection.before(block);
    else workDetail.append(block);
  }
})();
