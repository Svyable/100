# Evidence-first paper production

Upstream inspiration: [PaperOrchestra, pinned revision d9bae997](https://github.com/google-research/paper-orchestra/tree/d9bae997e793a015ed38bb1605be9eb58c00284f), [paper](https://arxiv.org/abs/2604.05018), [CLI](https://github.com/google-research/paper-orchestra/blob/d9bae997e793a015ed38bb1605be9eb58c00284f/paper_writing_cli.py). Apache-2.0 upstream; this adapter is independently implemented, not vendored. PaperOrchestra transforms raw research materials into manuscripts; it is not a proof checker or the Cogentic discovery harness.

## Operating sequence

1. Scout: pin literature, exact target and novelty boundary. Claim the scope before work.
2. Prover and adversary: separate hypotheses, proof attempts, falsifiers and raw logs; exchange only scope-bound evidence. Use the existing router and proof obligation DAG rather than creating a parallel task queue.
3. Checker: exact replay, Lean theorem/axiom audit, adversarial controls, measured costs; independent reviewer is a different author. Preserve negative and timeout outcomes. CI success is not mathematical acceptance.
4. Publication adapter: export the selected outcome and committed evidence at one full Git commit. By default only structurally independently accepted records are exportable; an explicit draft opt-in permits pending, gap or falsifier outcomes. Every export remains a draft, even if the underlying record is accepted.
5. Writing: specialized outline, literature, sections, figures and refinement agents. Use a pinned model and cutoff, preserve raw prompts and responses, and turn plotting off by default. Plots must be generated from archived data with exact units, seeds and scripts. Never fabricate citations, performance or novelty.
6. Publication audit: trace every claim to a source or theorem, check hypotheses and references, regenerate figures, compile LaTeX in a restricted environment without shell escape, independently review final text and archive its digest. No automatic submission or solved-ledger update. A paper can be scientifically invalid despite a checked underlying lemma.

## Reproduce the handoff

From a full Project 100 checkout (example uses the merged RH/GRH source audit, not an accepted theorem):

    python3 scripts/paper_orchestra_export.py \
      --commit 5703a54e036edefc1b38335f078da706f337fa0a \
      --work-id X-GRH-2026-SCOPE \
      --evidence docs/GRH_2026_SCOPE.md \
      --evidence data/grh_dependency_audit.json \
      --output /tmp/p100-grh-materials --allow-draft

The export contains idea_sparse.md, experimental_log.md and manifest.json. It reads committed blobs, not dirty working files, rejects symlinks, unsafe paths and overwrites, and records SHA-256 digests. The caller chooses evidence paths: their mathematical relevance to the work ID is not authenticated. Review metadata checks are structural only; do not equate them with authenticated expert review. Text can contain hostile instructions, so use a sandboxed writer without privileged tools; never pass credentials or confidential material.

With a separately installed, pinned PaperOrchestra checkout, configured model credentials and approved budget, run its CLI manually (not executed in this PR):

    python paper_writing_cli.py \
      --raw_materials_dir /tmp/p100-grh-materials \
      --latex_template_dir templates/iclr2025 \
      --output_dir /tmp/p100-grh-paper \
      --research_cutoff 2026-11 \
      --use_plotting false

Select an actually available template and pinned writer/reflection model in the installed release. No external service is invoked by the adapter.

## Competitive measurement

Keep the existing 36-cell proof-exchange preregistration unchanged (issue #55). A separate publication experiment should freeze identical evidence packets, cutoff, templates, model versions and total token/dollar/time budgets, compare a single-writer baseline, PaperOrchestra upstream and evidence-gated Project 100 workflow. Blind reviewers score source fidelity, theorem scope, citation accuracy, reproducibility and review time; report unsupported claims and all failed runs. Do not claim a performance advantage from fixtures or paper volume. Primary scientific metric remains independently accepted, novelty-audited results per total resource, with publication quality a separate metric. Google and OpenAI have not been beaten until measured under comparable conditions.

## Author-side validation

Claim [#407](https://github.com/Svyable/100/issues/407). Seven isolated Python unittest cases passed (0.315 s); exact tested Git blob IDs be616e27d22c61edf0960ef080eb343a70544914 and 26cdebfd121aff655fb17bea6be3d78ba79bdd1a. Full repository checkout failed DNS; full regeneration and outcome ledger integration still pending. No manuscript, model trial, independent review or new mathematical result produced.

## ScientistTwo-inspired integrity loop (2026-11-25)

Source: [ScientistTwo project](https://scientist-two.github.io/) and [preprint](https://arxiv.org/abs/2609.19644). The empirical benchmark gains and simulated review ratings are not mathematical proof or publication acceptance. Use inexpensive exact falsifiers first, then preregister larger instances and budgets, isolate the contribution of each hypothesis or computational shortcut, and require new evidence for substantive objections. Freeze scope before running; preserve failed screens, cost, and counterexamples. Compare matched-budget arms under the existing benchmark rather than alter the frozen experiment.

For the publication handoff, rerun the export command with `--verify` appended. This independently reconstructs the packet bytes from the caller-selected commit, work ID and evidence paths, rejects changed, missing, extra or symlinked files, and applies the canonical outcomes validator (including normalized reviewer identity, review dates and novelty prerequisites). This is a mechanical data integrity gate only: the four scientific audit axes remain separate: exact replay of reported numbers, hypothesis/specification fidelity, source existence and relevance, and manuscript-to-proof/code correspondence. Route any failure back to the prover or experimenter; do not clear it by rewriting the manuscript or lowering the gate. Independent review and novelty review remain unchanged. No ScientistTwo model execution or benchmark superiority is claimed.
