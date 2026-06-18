# -*- coding: utf-8 -*-
"""
================================================================================
TPF_ProvablePrimeGen_v1_1.py
Rekurzív BIZONYÍTOTT erős prím — teljes Pocklington-tanúsítvány-fa (Maurer)
BarefootRealism Labs | László Tatai | 2026
================================================================================

VÁLTOZÁSNAPLÓ
-------------
v1_1 (2026-06): az R = rng.randrange(lo, hi+1) | 1 kifejezésből eltávolítva a
  | 1 kényszer, amely determinisztikusan p ≡ 3 (mod 4) ujjlenyomatot okozott.
  A Pocklington-bizonyíték érintetlen: 2q | (p-1) páros R esetén is teljesül.
  A halott if R < lo: R += 2 sor szintén törölve.

A FELISMERÉS
------------
A StrongPrimeGen a nagy r faktort véletlenül választotta, és primalitását
Miller–Rabin (valószínűségi) adta — ez volt az egyetlen elméleti rés.
Megoldás: r-t magát is KONSTRUÁLJUK rekurzívan. Ha

    p = 2·R·q + 1,   q kisebb, REKURZÍVAN bizonyított prím,

akkor q | (p−1), és ha 2q > √p, a Pocklington–Lehmer-tétel determinisztikusan
bizonyítja p prímségét. A rekurzió lemegy a triviálisan ellenőrizhető kis
prímekig (≤ 2^20, trial-division-ekvivalens). Ez Maurer algoritmusa (1995).

KÉT LEGYET EGY CSAPÁSRA:
  • q egyszerre a Pocklington-tanú ALAPJA és a p−1 NAGY PRÍMFAKTORA
    → a bizonyíték rekurzív ÉS a Pollard p−1 erősség automatikus (q ~ bits/2).
  • R véletlen → nincs maradék-ujjlenyomat (tiszta, mint a clean mód).

A tanúsítvány egy FA: minden szinten {p, R, q, tanú, q_cert}, a levél trial.
A verify_provable a fát a gyökértől a levelekig ellenőrzi, csak moduláris
aritmetikával — semmilyen valószínűségi lépésre nem támaszkodik a nagy
prímeknél.

KIMENET: certifikált JSON-bundle, ugyanazzal a sémával, mint a StrongPrimeGen
(N, strength, certificate-tree), így a meglévő Entropy Lab is méri.
================================================================================
"""

import argparse
import hashlib
import json
import math
import random
import time

from sympy import isprime   # CSAK a bázis-eset (≤ 2^20) ellenőrzéséhez

BASE_BITS = 20              # e fölött rekurzió, alatta trial-bizonyíték


# ══════════════════════════════════════════════════════════════════════════════
def _mr(n, rng, rounds=24):
    """Miller–Rabin — ELŐSZŰRŐ a jelöltekre (a bizonyíték a Pocklington-fa)."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2; s += 1
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
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


def make_provable(bits, rng):
    """Rekurzív bizonyított prím. Visszaad: (p, cert_tree)."""
    if bits <= BASE_BITS:
        while True:
            p = rng.randrange(1 << (bits - 1), 1 << bits) | 1
            if isprime(p):                              # kis szám: trial-division-ekvivalens
                return p, {'N': str(p), 'bits': p.bit_length(),
                           'method': 'trial', 'q_cert': None}
    q_bits = bits // 2 + 1                              # q > √p biztosításához
    q, q_cert = make_provable(q_bits, rng)
    # R-t pontosan akkora tartományból, hogy p = 2Rq+1 PONTOSAN `bits` bites legyen
    lo = ((1 << (bits - 1)) + 2 * q - 1) // (2 * q)     # ceil(2^(bits-1)/(2q))
    hi = ((1 << bits) - 2) // (2 * q)                   # floor((2^bits-2)/(2q))
    if hi <= lo:
        raise RuntimeError(f"bits={bits}: üres R-tartomány")
    for _ in range(200000):
        R = rng.randrange(lo, hi + 1)   # nincs |1: R páros is lehet → p mod 4 egyenletesen {1,3}
        p = 2 * R * q + 1
        if p.bit_length() != bits:
            continue
        if (2 * q) * (2 * q) <= p:                      # Pocklington: F=2q > √p
            continue
        if not _mr(p, rng):
            continue
        pm1 = p - 1
        for _ in range(96):                            # tanú: a^(p-1)=1 és gcd-feltételek
            a = rng.randrange(2, p - 1)
            if pow(a, pm1, p) != 1:
                continue
            if math.gcd(pow(a, pm1 // 2, p) - 1, p) != 1:
                continue
            if math.gcd(pow(a, pm1 // q, p) - 1, p) != 1:
                continue
            return p, {'N': str(p), 'bits': p.bit_length(), 'method': 'maurer',
                       'R': str(R), 'q': str(q), 'witness': str(a), 'q_cert': q_cert}
    raise RuntimeError(f"bits={bits}: nem talált p-t")


# ══════════════════════════════════════════════════════════════════════════════
def verify_provable(cert, rng=None):
    """A tanúsítvány-FA rekurzív ellenőrzése. Csak moduláris aritmetika + bázis-trial.
    NEM támaszkodik a generátorra és nagy prímeknél valószínűségi tesztre sem."""
    if rng is None:
        rng = random.Random(0xC0FFEE)
    N = int(cert['N'])
    if cert['method'] == 'trial':
        return N < (1 << (BASE_BITS + 2)) and isprime(N)
    q = int(cert['q'])
    if not verify_provable(cert['q_cert'], rng):
        return False
    if int(cert['q_cert']['N']) != q:
        return False
    pm1 = N - 1
    if pm1 % q != 0 or pm1 % 2 != 0:
        return False
    if (2 * q) * (2 * q) <= N:                          # F = 2q > √N
        return False
    a = int(cert['witness'])
    if pow(a, pm1, N) != 1:
        return False
    if math.gcd(pow(a, pm1 // 2, N) - 1, N) != 1:
        return False
    if math.gcd(pow(a, pm1 // q, N) - 1, N) != 1:
        return False
    return True


def cert_depth(cert):
    d = 0
    c = cert
    while c and c.get('q_cert'):
        c = c['q_cert']; d += 1
    return d


def largest_proven_factor_bits(cert):
    """A p−1 legnagyobb BIZONYÍTOTT prímfaktora = q (a fa első szintje)."""
    if cert['method'] == 'trial':
        return int(cert['N']).bit_length()
    return int(cert['q']).bit_length()


# ══════════════════════════════════════════════════════════════════════════════
class ProvablePrimeGen:
    def __init__(self, bits=512, seed=None):
        self.bits = bits
        self.seed = seed
        self.rng = random.Random(seed)

    def generate(self):
        t0 = time.time()
        p, tree = make_provable(self.bits, self.rng)
        secs = time.time() - t0
        qbits = largest_proven_factor_bits(tree)
        return {
            'N': str(p),
            'bits': p.bit_length(),
            'strength': {
                'p_minus_1_largest_prime_bits': qbits,
                'r': tree.get('q'),                    # a nagy faktor (kompat. a StrongPrimeGen sémával)
                'pollard_p1_resistant': True,
                'fully_recursive_certificate': True,
            },
            'fingerprint': {
                'R0': 0, 'force_3': False, 'residue_leak_bits': 0.0,
                'note': 'R veletlen → nincs maradek-ujjlenyomat; minden faktor rekurzivan bizonyitott',
            },
            'construction': {'form': '2*R*q + 1 (Maurer-rekurziv)', 'seed': self.seed,
                             'recursion_depth': cert_depth(tree)},
            'certificate': tree,                       # TELJES tanúsítvány-FA
            'proved': True,
            'stats': {'seconds': round(secs, 3), 'recursion_depth': cert_depth(tree)},
        }


def build_certified_bundle(records, params):
    canon = json.dumps(records, sort_keys=True, separators=(',', ':'))
    return {
        'meta': {
            'generator': 'TPF_ProvablePrimeGen_v1_0',
            'author': 'Laszlo Tatai | BarefootRealism Labs',
            'orcid': '0009-0007-5153-6306',
            'zenodo': 'https://doi.org/10.5281/zenodo.19698943',
            'generated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'params': params, 'count': len(records),
        },
        'primes': records,
        'certification': {
            'scheme': 'Maurer recursive Pocklington-Lehmer tree; SHA256 content hash',
            'content_sha256': hashlib.sha256(canon.encode()).hexdigest(),
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser(description="Rekurzív bizonyított erős prímgenerátor (Maurer)")
    ap.add_argument('--bits', type=int, default=512)
    ap.add_argument('--count', type=int, default=3)
    ap.add_argument('--seed', type=int, default=None)
    ap.add_argument('--out', type=str, default=None)
    ap.add_argument('--blum', action='store_true',
                    help="csak Blum-prímeket gyűjt (p ≡ 3 mod 4); ~2x lassabb, "
                         "de minden prím erős Blum-prím (BBS / Rabin-hoz)")
    args = ap.parse_args()

    gen = ProvablePrimeGen(bits=args.bits, seed=args.seed)
    blum_note = " | BLUM MÓD (p ≡ 3 mod 4)" if args.blum else ""
    print(f"bits={args.bits} | Maurer-rekurzív, teljes Pocklington-fa | seed={args.seed}{blum_note}\n")
    recs = []
    generated = 0
    while len(recs) < args.count:
        rec = gen.generate()
        generated += 1
        p = int(rec['N'])
        if args.blum and p % 4 != 3:
            continue
        if args.blum:
            rec['blum_prime'] = True
        ok = verify_provable(rec['certificate'])
        recs.append(rec)
        s = rec['strength']; st = rec['stats']
        blum_tag = " | Blum ✓" if args.blum else ""
        print(f"#{len(recs)}: {rec['bits']} bit | {st['seconds']}s | mélység {st['recursion_depth']} | "
              f"p−1 bizonyított nagy faktor: {s['p_minus_1_largest_prime_bits']} bit | "
              f"FA-ellenőrzés: {'ÉRVÉNYES ✓' if ok else 'HIBÁS ✗'}{blum_tag}")
        print(f"     N = {rec['N'][:46]}...{rec['N'][-12:]}")
    if args.blum:
        print(f"\nBlum-szűrés: {args.count} Blum-prím, {generated} generálva (~{generated/args.count:.1f}x arány)")

    if args.out:
        params = {'bits': args.bits, 'method': 'maurer-recursive', 'seed': args.seed}
        bundle = build_certified_bundle(recs, params)
        with open(args.out, 'w') as f:
            json.dump(bundle, f, indent=2)
        print(f"\nCertifikalt JSON mentve: {args.out}")
        print(f"  tartalom-hash: {bundle['certification']['content_sha256'][:24]}...")


if __name__ == '__main__':
    main()
