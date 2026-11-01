# Fleet packets — omni-directional agent dispatch

Machine-readable claimable slots for many parallel agents without multiplying
unsupported theorems.

```sh
python3 scripts/scale.py --budget 100 --json        # stdout packets
python3 scripts/scale.py --write                    # SCALE.md + docs/api/packets.json
python3 scripts/work.py --next 5                    # human-readable top of queue
python3 scripts/analogues.py --check                # structural finite analogues
python3 scripts/benchmark.py --check                # empty A/B/C/D trial ledger OK
```

## Packet contract

Each packet in `docs/api/packets.json` carries:

- `id`, `kind`, `problems`, `deliverable`, `acceptance`, `boundary`, `falsifier`
- `roles`: recommended `scout` / `adversary` / `checker` split inside **one** claim
- `scope_sha256`: the work-queue claim digest (`python3 scripts/work.py --id <id>`); put it in the claim. scripts/router.py admits only this value
- `packet_sha256`: the packet identity including the role plan; changing roles or the deliverable changes it
- claim URLs for `.github/ISSUE_TEMPLATE/claim.yml`

A packet is **not** a theorem, a readiness change, or permission to edit
`data/solved.json`.

## Omni-directional lanes

| Lane | Ledger / tool | Scale move |
|---|---|---|
| Acceptance frontier | `data/proof_obligations.json` | Discharge only with independent reviews |
| Formal comparators | `data/formalization.json` + Lean | Add statements; kernel fidelity ≠ novelty |
| Exact lab | `scripts/lab.py` | Replay published certificates; no dominated ranges |
| Structural analogues | `data/structural_analogues.json` | Finite stand-ins for structural IDs |
| Intake | `NEXT_100.md` / `scripts/next.py` | Batches of 50–100 differentiated hypotheses |
| Measurement | `benchmarks/PROTOCOL.md` | 36-cell prereg; zero trials until run for real |

## Rules

1. Claim `[Claim] <id>` before starting (`AGENTS.md`).
2. Prefer obligation and Lean packets over mass comparators when both are free.
3. Adversary output is stored unsummarized; checker is not the scout.
4. Regenerate with `python3 scripts/regen.py` before shipping.
