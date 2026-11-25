"""Exact finite consistency checks of OpenAI's stated rectangular exponent.

Source: openai/math@3344da59991ed94f9ba711217b29c1d760badfa6,
lean/docs/107.md. This is not a proof replay or a performance benchmark.
Run: python3 scripts/m084_omega94_audit.py
"""
from fractions import Fraction as Q
from itertools import permutations, product


def exponent(a, b, c):
    x, y, z = sorted(map(Q, (a, b, c)), reverse=True)
    if z <= 0:
        raise ValueError("positive weights required")
    return x + y + max(Q(0), (x + y) * z - x * y) ** 2 / (4 * x * y * z)


def require(condition, label):
    if not condition:
        raise ValueError(label)


def check(f):
    require(f(1, 1, 1) == Q(9, 4), "square")
    require(f(1, 1, Q(1, 2)) == 2, "dual boundary")
    for t in (Q(i, 16) for i in range(1, 17)):
        want = Q(2) if t <= Q(1, 2) else 2 + (2*t-1)**2/(4*t)
        require(f(1, 1, t) == want, "dual slice")
        require((f(1, 1, t) == 2) == (t <= Q(1, 2)), "dual plateau")
    count = 0
    for a, b, c in product(range(1, 7), repeat=3):
        v = f(a, b, c)
        require(max(a+b, b+c, c+a, Q(3, 4)*(a+b+c)) <= v <= a+b+c,
                "paper lower bound or naive upper bound")
        for weights in permutations((a, b, c)):
            require(f(*weights) == v, "permutation")
        for s in (Q(1, 3), Q(3, 2), Q(5)):
            require(f(s*a, s*b, s*c) == s*v, "homogeneity")
        count += 1
    return count


def main():
    count = check(exponent)
    mutants = {
        "wrong square coefficient": lambda a,b,c: 2*exponent(a,b,c)-sum(sorted((a,b,c))[-2:]),
        "missing plateau": lambda a,b,c: exponent(a,b,c)+Q(1,100) if min(a,b,c)<Q(1,2) else exponent(a,b,c),
        "asymmetric": lambda a,b,c: exponent(a,b,c)+Q(1,100) if a<b else exponent(a,b,c),
        "nonhomogeneous": lambda a,b,c: exponent(a,b,c)+Q(1,100) if max(a,b,c)>6 else exponent(a,b,c),
    }
    for name, mutant in mutants.items():
        try:
            check(mutant)
        except ValueError as exc:
            print(f"rejected {name}: {exc}")
        else:
            raise RuntimeError(f"surviving mutant: {name}")
    print(f"PASS: {count} ordered positive triples, 16 dual samples, {len(mutants)}/{len(mutants)} mutants rejected")


if __name__ == "__main__":
    main()
