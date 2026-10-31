## Mathematical or site change

**Candidate IDs affected:**

**What changed, and why?**

**Primary sources and checked-on dates (where applicable):**

**Scope of claims:** State whether this is a new theorem, independently
reproduced known result, partial bound, experiment, or unverified proposal.

## Verification

- [ ] Registry source remains authoritative; generated ranking + Pages snapshot updated
- [ ] `python3 scripts/rank.py --check`
- [ ] `python3 scripts/build_site.py --check`
- [ ] `python3 scripts/research.py --check` and `python3 scripts/lab.py --check`
- [ ] New or changed probes: independent checker plus tamper tests in `tests/test_lab.py`
- [ ] `node --check docs/assets/app.js`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] If mathematical claims changed, checked exact theorem scope against primary source

Do not mark a universal conjecture resolved based solely on a preprint,
AI announcement, or finite computational test.
