# M094 — Hadamard existence frontier corrected (November 2, 2026)

**Status correction, not a new mathematical result.** The repository previously
said that order 668 was the smallest multiple of four for which no Hadamard
matrix was known. That was historically true after order 428 was settled in
2005, but it became false in August 2026.

**Primary specialist source:** Ronan Egan, Ilias S. Kotsireas, Stephen London
and Pádraig Ó Catháin, [*Recent progress in the construction of Hadamard
matrices*](https://arxiv.org/abs/2610.27175), submitted **19 October 2026**.
The authors verify the twelve matrices announced on 12 August 2026 by Alpöge,
Voinov and Reynolds-Haertle, including order **668**, by exact multiplication
of their ±1 matrices. They also construct sixteen additional orders and report
that **every multiple of four below 2000** has a known matrix. Their current
catalogue lists **95 orders ≤10,000** without known constructions; the smallest
is **2396 = 4×599** (see their introduction, Section 3 and Section 4).

**Do not confuse three boundaries.** The project’s *implementation* still
lacks a constructor at order **188**; this is not an open existence case. The
specialist literature’s smallest currently unconstructed order is **2396**.
The unrestricted Hadamard conjecture remains open, and neither the August
matrix announcement nor this October verification resolves it. These finite
existence results are not this project's discoveries or independently accepted
new work. The repository’s evidence and Solved states remain unchanged.

**Falsifier:** a contemporary primary construction or a correction to the
specialist catalogue that changes the 2396 frontier; re-audit the date and
scope before updating it again. The October 2026 source is a preprint with
explicit independently checked finite matrices, not a peer-reviewed global
conjecture proof.
