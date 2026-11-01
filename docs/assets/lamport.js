/* Lamport Explorer: progressive enhancement; HTML is readable without JavaScript. */
(() => {
  "use strict";
  const groups = [...document.querySelectorAll("[data-lamport-problem]")];
  const controls = document.getElementById("lamport-controls");
  const select = document.getElementById("lamport-problem");
  const count = document.getElementById("lamport-count");
  if (!groups.length || !controls || !select || !count) return;
  controls.hidden = false;
  const SVG_NS = "http://www.w3.org/2000/svg";
  const graphs = [...document.querySelectorAll(".lamport-graph")];
  for (const graph of graphs) {
    const cards = [...graph.querySelectorAll(".lamport-node")];
    if (!cards.some(card => card.dataset.depends)) continue;
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "lamport-graph-links");
    svg.setAttribute("aria-hidden", "true");
    graph.prepend(svg);
  }

  function drawGraph(graph) {
    const svg = graph.querySelector(".lamport-graph-links");
    if (!svg || graph.closest("[hidden]")) return;
    const bounds = graph.getBoundingClientRect();
    svg.setAttribute("viewBox", "0 0 " + bounds.width + " " + bounds.height);
    svg.replaceChildren();
    const cards = new Map([...graph.querySelectorAll(".lamport-node")].map(card => [card.id, card]));
    for (const target of cards.values()) {
      for (const id of (target.dataset.depends || "").split(" ").filter(Boolean)) {
        const source = cards.get(id);
        if (!source) continue;
        const from = source.getBoundingClientRect();
        const to = target.getBoundingClientRect();
        const x1 = from.right - bounds.left + 3;
        const y1 = from.top - bounds.top + from.height / 2;
        const x2 = to.left - bounds.left - 6;
        const y2 = to.top - bounds.top + to.height / 2;
        if (x2 <= x1) continue;
        const bend = Math.max(14, (x2 - x1) * .45);
        const path = document.createElementNS(SVG_NS, "path");
        path.setAttribute("d", "M" + x1 + "," + y1 + " C" + (x1 + bend) + "," + y1 + " " + (x2 - bend) + "," + y2 + " " + x2 + "," + y2);
        svg.append(path);
        const arrow = document.createElementNS(SVG_NS, "path");
        arrow.setAttribute("d", "M" + (x2 - 6) + "," + (y2 - 4) + " L" + x2 + "," + y2 + " L" + (x2 - 6) + "," + (y2 + 4));
        svg.append(arrow);
      }
    }
  }
  let pending = false;
  function redraw() {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => {
      pending = false;
      for (const graph of graphs) drawGraph(graph);
    });
  }
  function focus(value, updateUrl) {
    const selected = groups.some(group => group.dataset.lamportProblem === value) ? value : "";
    select.value = selected;
    for (const group of groups) group.hidden = Boolean(selected && group.dataset.lamportProblem !== selected);
    count.textContent = selected ? "Showing " + selected : "Showing " + groups.length + " campaigns";
    if (updateUrl) {
      const url = new URL(window.location.href);
      if (selected) url.searchParams.set("problem", selected);
      else url.searchParams.delete("problem");
      history.replaceState(null, "", url);
    }
    redraw();
  }
  focus(new URLSearchParams(window.location.search).get("problem") || "", false);
  select.addEventListener("change", () => focus(select.value, true));
  window.addEventListener("resize", redraw);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(redraw);
  redraw();
})();
