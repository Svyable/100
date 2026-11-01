"""Structure mines: certified tables read off existing certificates.

A mine is not a new theorem. It records an exact finite table and an
independent checker recomputes that table by a different route. Probes stay
the verifiers of the finite statements; mines are what those certificates are for.
"""
from importlib import import_module

MINES = {
    "goldbach_growth": "goldbach_growth",
    "straus_patterns": "straus_patterns",
    "deck_invariants": "deck_invariants",
    "poset_balance": "poset_balance",
    "frankl_orbits": "frankl_orbits",
}


def load(mine_id):
    module = import_module(f"{__name__}.{MINES[mine_id]}")
    if module.MINE["id"] != mine_id:
        raise ValueError(f"mine registry mismatch for {mine_id}")
    return module


def artifact(mine_id):
    return f"scripts/mines/{MINES[mine_id]}.py"


def command(mine_id):
    return f"python3 scripts/mine.py --mine {mine_id}"


def all_mines():
    return [load(mine_id) for mine_id in MINES]
