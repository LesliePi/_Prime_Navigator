# Changelog — TPF Prime Engine

All notable changes documented here in the interest of full transparency.
The project follows a component-level versioning scheme.

---

## TPF_Entropy_Lab — v1.2 (2026-06-17)

### Fixed — Pocklington verification condition
**Previous code:** `if(F!==Nm1) return {ok:false,why:'F≠N−1'}`
**Corrected to:** `if(Nm1%F!==0n) return {ok:false,why:'F∤N−1'}`

The original check required *complete* factorization of N−1 (F = N−1 exactly).
The Pocklington–Lehmer theorem only requires F | (N−1) and F² > N — complete
factorization is sufficient but not necessary. The strict equality check would
incorrectly reject any valid, partially-factored external Pocklington certificate.
For TPF's own generators (which always produce complete factorizations) this had
no practical impact, but it was a design error in a tool positioned as a
general-purpose Pocklington verifier.

### Added — mod 4 residue measurement
`4` added to the MODULI array (between 3 and 5) so that the mod 4 distribution
of generated primes is explicitly measured. This reveals:
- StrongPrimeGen: always N ≡ 1 (mod 4) — inherent, documented (see README)
- ProvablePrimeGen v1_1+: uniform {1, 3} — as expected after the v1_1 fix

### Fixed — mod 4 baseline computation
**Previous code:** `expectedUniformH(n, Number(p)-1, Number(p))` — for p=4 this
passed k=3, modelling a uniform distribution over three classes.
**Corrected:** `coprimeClasses(p)` returns 2 for p=4 (phi(4)=2, since primes
larger than 2 can only be 1 or 3 mod 4).

Impact: with k=3, H_baseline(mod 4) ≈ 1.54 bits, producing a spurious ~0.56 bit
"leak" even for a perfectly uniform {1,3} distribution. With k=2, H_baseline ≈
0.97 bits, and the measured leak correctly rounds to 0.00 bits for a clean batch.

---

## TPF_ProvablePrimeGen — v1.1 (2026-06-17)

### Fixed — deterministic mod 4 fingerprint (|1 bug)

**Previous code (v1.0):**
```python
R = rng.randrange(lo, hi + 1) | 1
if R < lo:
    R += 2
```
**Corrected (v1.1):**
```python
R = rng.randrange(lo, hi + 1)  # R can be even or odd
```

The `| 1` forced R to always be odd. Since q is an odd prime, this made
`p = 2·R·q + 1 ≡ 3 (mod 4)` deterministically for every generated prime —
a 1-bit structural fingerprint contradicting the documented "no residue
fingerprint" property.

The fix: remove `| 1`. R is now uniformly random over [lo, hi], producing
p ≡ 1 (mod 4) when R is even and p ≡ 3 (mod 4) when R is odd — uniform {1,3}
distribution, empirically confirmed (H(mod 4) ≈ 1.00 bit on 32-prime batch).

**Mathematical safety:** removing `| 1` does not affect the Pocklington–Lehmer
proof. The proof requires 2q | (p−1) and (2q)² > p; both hold regardless of
R's parity since p−1 = 2·R·q always contains factors 2 and q.

**Dead code removed:** the `if R < lo: R += 2` guard was unreachable after
`| 1` (since `x | 1 ≥ x ≥ lo` always) and is removed.

**Not changed:** the base-case line `p = rng.randrange(...) | 1` (line 84 of
v1.0) generates *odd prime candidates* for trial division and is correct —
this is a different context and is intentionally retained.

---

## TPF_StrongPrimeGen — v1.2 (initial public release)

No changes relative to the internal development version. Documents the following
known structural property for completeness:

**StrongPrimeGen: N ≡ 1 (mod 4) always**
Construction: `N−1 = 2^a · Q · r · t` where a >> 2 (typically 100–250 bits,
used to reach the target bit length). Since 4 | 2^a, we have 4 | (N−1), so
N ≡ 1 (mod 4) for every generated prime. This is an inherent, known consequence
of the construction — not a security weakness for RSA or DH applications, where
the mod 4 residue of a prime factor is cryptographically irrelevant. Documented
in README and product document.

---

## Notes on version history

These are the first public releases. Internal development versions existed but
were not publicly distributed. The bugs documented above were identified during
pre-release review and corrected before the initial public deposit.

---

*BarefootRealism Labs — László Tatai, 2026*
