"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { formatPacket, safeId } = require("../docs/assets/frontier.js");

const task = {
  id: "O-M075-01",
  kind: "obligation",
  title: "Review exact S5 orbit invariant",
  status: "runnable",
  problems: ["M075"],
  scope_sha256: "d".repeat(64),
  source: "data/proof_obligations.json",
  existing_claims_url: "https://github.com/Svyable/100/issues?q=claim",
  open_claim_url: "https://github.com/Svyable/100/issues/new",
  deliverable: "Verify the canonical orbit separation.",
  context: "Finite families over five elements.",
  boundary: "n=4 is known mathematics, not a new theorem.",
  falsifier: "Two inequivalent families get the same code.",
  acceptance: ["Independent review", "Reproduce exact result"],
  depends_on: ["L002"]
};

test("packet preserves exact scope, dependencies and evidence guards", () => {
  const packet = formatPacket(task);
  assert.match(packet, /O-M075-01/);
  assert.match(packet, /Scope SHA-256: d{64}/);
  assert.match(packet, /Verify the canonical orbit separation/);
  assert.match(packet, /Independent review/);
  assert.match(packet, /L002/);
  assert.match(packet, /Do not self-certify an independent review/);
  assert.match(packet, /finite replay is not a universal theorem/);
  assert.match(packet, /do not hand-edit generated docs\//i);
  assert.match(packet, /data\/outcomes\.json/);
  assert.match(packet, /Check for an existing \[Claim\] issue/);
  assert.doesNotMatch(packet, /NOT READY TO DISPATCH/);
});

test("nonrunnable items must not be presented as dispatchable", () => {
  const packet = formatPacket({
    ...task, id: "O-M075-02", status: "waiting_on_dependencies"
  });
  assert.match(packet, /NOT READY TO DISPATCH/);
  assert.match(packet, /Resolve its prerequisites/);
});

test("packet refuses missing identity and unsafe work item ids", () => {
  assert.equal(safeId("O-M075-01"), true);
  assert.equal(safeId("../secrets"), false);
  assert.equal(safeId("https://example.org"), false);
  assert.throws(() => formatPacket({ ...task, id: "../../bad" }), /stable id/);
  assert.throws(() => formatPacket({ ...task, scope_sha256: "" }), /scope digest/);
});

test("source data gaps remain explicitly unknown", () => {
  const packet = formatPacket({ ...task, depends_on: [], acceptance: [] });
  assert.match(packet, /No dependency IDs recorded in this work item/);
  assert.match(packet, /canonical work-item acceptance contract/);
  assert.doesNotMatch(packet, /All obligations discharged/);
});
