"""Prime sieve (search side) and deterministic Miller-Rabin (check side)."""

_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)


def sieve(limit):
    """bytearray flags[i] == 1 iff i is prime, for 0 <= i <= limit."""
    flags = bytearray([1]) * (limit + 1)
    flags[0:2] = b"\x00\x00"[:min(2, limit + 1)]
    i = 2
    while i * i <= limit:
        if flags[i]:
            flags[i * i::i] = bytearray(len(range(i * i, limit + 1, i)))
        i += 1
    return flags


def is_prime(n):
    """Deterministic Miller-Rabin; proven correct for n < 3.3 * 10**24."""
    if n < 2:
        return False
    for p in _MR_BASES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in _MR_BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def odd_sieve(limit):
    """Independent odd-only sieve: returns a predicate for 0 <= n <= limit."""
    size = limit // 2 + 1
    odd = bytearray([1]) * size          # odd[i] represents 2*i + 1
    odd[0] = 0
    i = 1
    while (2 * i + 1) ** 2 <= limit:
        if odd[i]:
            step = 2 * i + 1
            start = (step * step) // 2
            odd[start::step] = bytearray(len(range(start, size, step)))
        i += 1

    def prime(n):
        if n == 2:
            return True
        if n < 2 or n % 2 == 0 or n > limit:
            return False
        return bool(odd[n // 2])
    return prime
