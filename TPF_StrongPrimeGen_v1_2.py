# -*- coding: utf-8 -*-
"""
================================================================================
TPF_StrongPrimeGen_v1_0.py
Paraméterezhető, certifikált ERŐS prímgenerátor
BarefootRealism Labs | László Tatai | 2026
================================================================================

A FELISMERÉS
------------
A Pocklington–Lehmer-tételhez csak az kell, hogy N−1 faktorizált F része
F > √N legyen. F-nek NEM kell csupa kis prímnek lennie. Ha beteszünk EGY
nagy prímet (r) N−1 faktorai közé:

    N − 1 = 2^a · 3 · Q_R0 · r · t       (Q_R0 = primorial(5..R0))

akkor:
  • a teljes faktorizáció ISMERT → Pocklington determinisztikus bizonyíték,
  • p−1 tartalmaz egy NAGY prímtényezőt (r) → Pollard p−1 reménytelen → ERŐS,
  • R0 szabályozza a sebesség↔ujjlenyomat kompromisszumot (lásd lent).

EZ ORVOSOLJA a sima-p−1 gyengeséget, amit a TPF_Immunity_PrimeGen örökölt
(ott N−1 csupa kis prím volt → Pollard p−1 célpont).

PARAMÉTEREK
-----------
bits      : a prím célbitmérete
R0        : kis-immunitás korlát (Q = primorial(5..R0)); SEBESSÉG vs UJJLENYOMAT
            - R0 nagy (pl. 199): gyorsabb generálás, de minden r′≤R0 kvadratikus
              maradék mod N (Jacobi-ujjlenyomat, ROCA-szerű, detektálható)
            - R0 = 0: nincs ujjlenyomat (minden kis prímre Jacobi ~50%), lassabb
            MÉRT: az ujjlenyomat pontosan R0-ig terjed, fölötte ~50%.
r_bits    : a p−1-beli nagy prímfaktor mérete (alapból ~bits/2 → maximális
            Pollard p−1 ellenállás). r_bits ≥ 2·B kell a B-simasági korláthoz.
safe      : ha True, r is "erős" (r−1-nek is van nagy prímfaktora) — Gordon-szerű
            kétszintű erősség (lassabb).
seed      : reprodukálhatóság (None → rendszer-entrópia)

TANÚSÍTVÁNY
-----------
Minden prím önállóan ellenőrizhető rekordot kap (verify_strong_certificate):
N−1 teljes faktorlistája, faktoronkénti Pocklington-tanúk, és a p−1 nagy
prímfaktorának mérete (erősség-attribútum).

FÜGG: sympy
================================================================================
"""

import argparse
import json
import math
import random
import time

from sympy import isprime, primerange, randprime


# ══════════════════════════════════════════════════════════════════════════════
# Segédek
# ══════════════════════════════════════════════════════════════════════════════

_SMALL = [int(p) for p in primerange(2, 1 << 12)]   # t faktorizációhoz (≤ 4096)

def _factor_small_t(t):
    """t teljes faktorizációja (t kicsi). dict{prím:kitevő} vagy None."""
    fs = {}
    for q in _SMALL:
        if q * q > t:
            break
        while t % q == 0:
            fs[q] = fs.get(q, 0) + 1
            t //= q
    if t > 1:
        if not isprime(t):
            return None
        fs[t] = fs.get(t, 0) + 1
    return fs

def _find_witness(N, Nm1, q, rng, rand_tries=128):
    """Pocklington-tanú q | N−1-hez. Kis bázisok, majd véletlen nagyok."""
    cofac = Nm1 // q
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
        if a >= N:
            continue
        if pow(a, Nm1, N) == 1 and math.gcd(pow(a, cofac, N) - 1, N) == 1:
            return a
    for _ in range(rand_tries):
        a = rng.randrange(2, N - 1)
        if pow(a, Nm1, N) == 1 and math.gcd(pow(a, cofac, N) - 1, N) == 1:
            return a
    return None

def _strong_prime_r(r_bits, rng, safe=False):
    """Nagy prím r. Ha safe: r−1-nek is legyen nagy prímfaktora (Gordon-szerű)."""
    if not safe:
        return int(randprime(1 << (r_bits - 1), 1 << r_bits))
    # safe: r = 2·s·u + 1, ahol s nagy prím (~r_bits/2)
    s_bits = r_bits // 2
    while True:
        s = int(randprime(1 << (s_bits - 1), 1 << s_bits))
        # r = 2·k·s + 1 formában keresünk prímet
        base = 2 * s
        k = rng.getrandbits(max(1, r_bits - base.bit_length())) | 1
        r = base * k + 1
        if r.bit_length() == r_bits and isprime(r):
            return r


# ══════════════════════════════════════════════════════════════════════════════
# Generátor
# ══════════════════════════════════════════════════════════════════════════════

class StrongPrimeGen:
    def __init__(self, bits=512, R0=0, r_bits=None, safe=False, seed=None,
                 force_3=False):
        self.bits = bits
        self.R0 = R0
        self.safe = safe
        self.force_3 = force_3   # ha False: nincs mod-3 szivargas (tiszta ujjlenyomat)
        self.seed = seed
        self.rng = random.Random(seed)
        self.Qf = [int(p) for p in primerange(5, R0 + 1)] if R0 >= 5 else []
        self.Q = 1
        for p in self.Qf:
            self.Q *= p
        # a nagy faktor mérete: alapból ~bits/2 (maximális p−1 erősség)
        self.r_bits = r_bits if r_bits else max(16, bits // 2 - self.Q.bit_length() // 2 - 8)

    def generate(self, max_tries=5_000_000):
        t0 = time.time()
        r = _strong_prime_r(self.r_bits, self.rng, safe=self.safe)
        three = 3 if self.force_3 else 1
        base = 2 * three * (self.Q if self.Q > 1 else 1) * r
        a = self.bits - base.bit_length() - 18
        if a < 1:
            # r túl nagy a célbitmérethez → csökkentsük
            raise ValueError(f"r_bits={self.r_bits} túl nagy bits={self.bits}-hez. "
                             f"Csökkentsd r_bits-et vagy növeld bits-et.")
        C = base * (1 << a)
        tries = 0
        tt = self.rng.getrandbits(18) | 1
        while tries < max_tries:
            tt += 2
            tries += 1
            fs_t = _factor_small_t(tt)
            if fs_t is None:
                continue
            N = C * tt + 1
            if not isprime(N):           # gyors előszűrő (BPSW)
                continue
            # N−1 teljes faktorizációja: {2:a+1, 3:1, r:1} ∪ Qf ∪ fs_t
            fac = {2: a + 1, r: 1}
            if self.force_3:
                fac[3] = fac.get(3, 0) + 1
            for q in self.Qf:
                fac[q] = fac.get(q, 0) + 1
            for q, e in fs_t.items():
                fac[q] = fac.get(q, 0) + e
            Nm1 = N - 1
            witnesses = {}
            ok = True
            for q in sorted(fac):
                w = _find_witness(N, Nm1, q, self.rng)
                if w is None:
                    ok = False
                    break
                witnesses[q] = w
            if not ok:
                continue
            return self._record(N, r, fac, witnesses, tries, time.time() - t0)
        raise RuntimeError(f"Nem talált prímet {max_tries} jelölt alatt.")

    def _residue_leak_bits(self):
        import math as _m
        leak = 1.0 if self.force_3 else 0.0   # mod 3 = 1 ha force_3
        for p in self.Qf:                      # minden p<=R0: N mod p = 1 kenyszeritve
            leak += _m.log2(p - 1)
        return leak

    def _record(self, N, r, fac, witnesses, tries, secs):
        return {
            'N': str(N),
            'bits': N.bit_length(),
            'strength': {
                'p_minus_1_largest_prime_bits': r.bit_length(),
                'r': str(r),
                'pollard_p1_resistant': True,
                'safe_prime_r': self.safe,
            },
            'fingerprint': {
                'R0': self.R0,
                'force_3': self.force_3,
                'jacobi_forced_QR_below': self.R0,
                'residue_leak_bits': round(self._residue_leak_bits(), 3),
                'note': ('minden prim p<=R0: N mod p = 1 (maradek-ujjlenyomat, ~log2(p-1) bit/p). '
                         'force_3 eseten +1 bit (mod 3=1). R0=0 es force_3=False eseten ~0 bit.'),
            },
            'construction': {'form': ('2^a * 3 * Q_R0 * r * t + 1' if self.force_3
                                       else '2^a * Q_R0 * r * t + 1'),
                             'r_bits': self.r_bits, 'seed': self.seed},
            'certificate': {
                'factors': {str(q): e for q, e in sorted(fac.items())},
                'witnesses': {str(q): str(a) for q, a in sorted(witnesses.items())},
            },
            'proved': True,
            'stats': {'candidates': tries, 'seconds': round(secs, 3)},
        }


# ══════════════════════════════════════════════════════════════════════════════
# Független ellenőrzés
# ══════════════════════════════════════════════════════════════════════════════

def verify_strong_certificate(rec):
    """A rekordból igazolja: (1) N prím (Pocklington), (2) p−1 nagy prímfaktora.
    Csak moduláris aritmetika + a nagy faktor primalitása."""
    N = int(rec['N'])
    if N < 2:
        return False
    Nm1 = N - 1
    factors = {int(q): int(e) for q, e in rec['certificate']['factors'].items()}
    F = 1
    for q, e in factors.items():
        F *= q ** e
    if F != Nm1 or F * F <= N:           # Pocklington-feltétel
        return False
    for q in factors:
        a = int(rec['certificate']['witnesses'][str(q)])
        if pow(a, Nm1, N) != 1:
            return False
        if math.gcd(pow(a, Nm1 // q, N) - 1, N) != 1:
            return False
    # a deklarált nagy faktor tényleg prím, osztja p−1-et, és elég nagy?
    r = int(rec['strength']['r'])
    if Nm1 % r != 0 or not isprime(r):
        return False
    if r.bit_length() != rec['strength']['p_minus_1_largest_prime_bits']:
        return False
    # a kis faktorok primalitása
    for q in factors:
        if q.bit_length() <= 40 and not isprime(q):
            return False
    return True


def build_certified_bundle(records, params):
    """A generált prímeket certifikált JSON-bundle-be csomagolja:
    metaadat + tartalom-hash (integritás) + Pocklington-tanúsítványok."""
    import hashlib, time
    primes_canon = json.dumps(records, sort_keys=True, separators=(',', ':'))
    content_hash = hashlib.sha256(primes_canon.encode()).hexdigest()
    bundle = {
        'meta': {
            'generator': 'TPF_StrongPrimeGen_v1_0',
            'author': 'Laszlo Tatai | BarefootRealism Labs',
            'orcid': '0009-0007-5153-6306',
            'zenodo': 'https://doi.org/10.5281/zenodo.19698943',
            'generated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'params': params,
            'count': len(records),
        },
        'primes': records,
        'certification': {
            'scheme': 'Pocklington-Lehmer per-prime; SHA256 content hash for integrity',
            'content_sha256': content_hash,
        },
    }
    return bundle


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="Certifikált erős-prím generátor (paraméterezhető)")
    ap.add_argument('--bits', type=int, default=512)
    ap.add_argument('--R0', type=int, default=0,
                    help="kis-immunitás korlát; 0 = nincs Jacobi-ujjlenyomat")
    ap.add_argument('--r-bits', type=int, default=None,
                    help="p-1 nagy prímfaktorának mérete (alap: ~bits/2)")
    ap.add_argument('--safe', action='store_true', help="r is erős (Gordon-szerű)")
    ap.add_argument('--force-3', action='store_true',
                    help="3 betétele N-1-be (mod-3 szivárgás; alapból KI = tiszta)")
    ap.add_argument('--count', type=int, default=3)
    ap.add_argument('--seed', type=int, default=None)
    ap.add_argument('--out', type=str, default=None)
    args = ap.parse_args()

    gen = StrongPrimeGen(bits=args.bits, R0=args.R0, r_bits=args.r_bits,
                         safe=args.safe, seed=args.seed, force_3=args.force_3)
    print(f"bits={args.bits} | R0={args.R0} | force_3={args.force_3} | "
          f"maradek-szivargas≈{gen._residue_leak_bits():.2f} bit | "
          f"r_bits≈{gen.r_bits} | safe={args.safe}\n")

    recs = []
    for i in range(args.count):
        rec = gen.generate()
        ok = verify_strong_certificate(rec)
        recs.append(rec)
        s = rec['strength']; st = rec['stats']
        print(f"#{i+1}: {rec['bits']} bit | {st['candidates']} jelölt, {st['seconds']}s | "
              f"p−1 nagy faktor: {s['p_minus_1_largest_prime_bits']} bit | "
              f"tanúsítvány: {'ÉRVÉNYES ✓' if ok else 'HIBÁS ✗'}")
        print(f"     N = {rec['N'][:46]}...{rec['N'][-12:]}")

    if args.out:
        params = {'bits': args.bits, 'R0': args.R0, 'r_bits': gen.r_bits,
                  'safe': args.safe, 'force_3': args.force_3,
                  'residue_leak_bits': round(gen._residue_leak_bits(), 3)}
        bundle = build_certified_bundle(recs, params)
        with open(args.out, 'w') as f:
            json.dump(bundle, f, indent=2)
        print(f"\nCertifikalt JSON mentve: {args.out}")
        print(f"  tartalom-hash: {bundle['certification']['content_sha256'][:24]}...")


if __name__ == '__main__':
    main()
