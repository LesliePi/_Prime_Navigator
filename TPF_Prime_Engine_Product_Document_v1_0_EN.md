# TPF Prime Engine — Technical Product Document

**Version:** 1.0
**Author:** László Tatai — BarefootRealism Labs
**ORCID:** 0009-0007-5153-6306
**Zenodo:** https://doi.org/10.5281/zenodo.19698943
**Date:** June 2026
**Code license:** Business Source License 1.1 (non-commercial use free; converts to Apache 2.0 on 2030-06-17)
**Documentation license:** CC BY-NC 4.0

---

## 1. One-sentence summary

The TPF Prime Engine is a deterministic prime generation and certification system
that produces primes which are **provably prime**, **provably strong**
(Pollard p−1 resistant), and **measurably free of structural bias**, with each
property independently verifiable by any third party without access to the
generator.

---

## 2. What it is — and what it is not

**What it is:** a prime generation and certification toolkit. Primes are not
produced by random search; they are *constructed*, and each prime carries a
Pocklington–Lehmer certificate that establishes primality as a theorem, not as the
output of a probabilistic test. An open-source browser-based dashboard
re-verifies the certificates and measures the information-theoretic cleanliness of
the output independently of the generator.

**What it is not:** this is not new cryptography. Every building block is
well-established — the Pocklington–Lehmer theorem, Maurer's recursive prime
generation algorithm (1995), the Hardy–Littlewood singular series, Shannon
entropy. The value of the engine lies not in a new primitive but in the way these
known elements are arranged into a **single, measurable, bilaterally verifiable
pipeline**. The system does not replace standard public-key infrastructure and
does not rely on any secret algorithm; its security, where relevant, rests
exclusively on input entropy and mathematical structure (Kerckhoffs's principle).

---

## 3. Components

### 3.1 StrongPrimeGen — fast, certified strong prime

Constructs a prime of the form `N − 1 = 2^a · Q_R0 · r · t`, where `r` is a
large prime (by default ≈ N/2 bits). The complete factorization of N−1 is known,
enabling a Pocklington–Lehmer proof; the large factor `r` in p−1 provides
resistance to Pollard's p−1 factoring attack. Parameters:

- `bits` — target bit length
- `R0` — small-prime immunity bound; also controls the residue fingerprint
  (`R0 = 0` → zero fingerprint; larger `R0` → faster generation at the cost of a
  detectable residue pattern for all primes p ≤ R0)
- `r_bits` — bit length of the large prime factor in p−1 (strength)
- `safe` — Gordon-style two-level strength (r−1 also has a large prime factor)
- `force_3` — off by default; when on, introduces +1 bit of mod-3 leakage

The primality of the large factor `r` is confirmed by Miller–Rabin in this
variant; for full deterministic rigor, see 3.2.

### 3.2 ProvablePrimeGen — fully recursive provable prime (Maurer)

Constructs `p = 2·R·q + 1` where `q` is a smaller, **recursively certified**
prime. The certificate is a tree descending to trivially verifiable small primes
(≤ 2²⁰). No probabilistic test is used as evidence at any level. The same `q`
serves simultaneously as the Pocklington witness base **and** as the large prime
factor of p−1 — delivering full formal rigor and Pollard p−1 resistance together.
`R` is chosen randomly, so the output carries no residue fingerprint.

### 3.3 TPF Entropy Lab — open-source verification dashboard

A single self-contained HTML file with no external dependencies. Given a
certified prime bundle, it:

1. **re-verifies** every certificate independently (flat Pocklington or recursive
   Maurer-tree format, using BigInt arithmetic in the browser);
2. **measures** residue fingerprint leakage in bits, per modulus, with
   finite-sample bias correction;
3. **measures** sequence entropy (K_prim / bigram mutual information) with a
   z-score against a shuffle baseline;
4. **issues** a standalone measurement certificate with its own SHA-256 hash.

The dashboard is operationally a **Kerckhoffs compliance meter**: it quantifies
what, if anything, knowledge of the construction gives an adversary.

---

## 4. Properties and guarantees

| Property | How it is achieved | How it is verified |
|---|---|---|
| **Proved primality** | Known N−1 factorization → Pocklington–Lehmer theorem | Certificate recomputation (modular arithmetic only); for ProvablePrimeGen, full tree to small primes |
| **Strength (Pollard p−1)** | Large prime factor r ≈ N/2 bits in p−1 | r is prime + r \| (N−1) + bit length check |
| **Fingerprint freedom** | Random cofactor, `R0 = 0` | Residue entropy and sequence MI measured by dashboard |
| **Reproducibility** | Seed-controlled generation | Identical seed → identical output |

---

## 5. Measured performance

All figures are from reference runs on a single laptop (CPython). Every claim
is annotated with the batch from which it derives.

**StrongPrimeGen (clean mode, R0 = 0):**

| Bit length | Time / prime | p−1 large factor |
|---|---|---|
| 512 | ~0.03–0.08 s | ~248 bits |
| 1024 | ~0.05–0.3 s | ~504 bits |
| 1024 (safe) | ~3–4.5 s | ~504 bits |

Verified batches (100 primes, and 30/10 primes at larger sizes): 1024, 2048,
3096, 4096, 8192 bits — complete N−1 factorization confirmed for every prime,
r/N ≈ 49–50%, residue leakage < 0.5 bits on 100-prime batches, sequence-MI
z-score within ±0.6 (no detectable serial structure).

**Note on small batches:** at 4–16 primes, finite-sample noise can produce
false positive fingerprint readings (observed at 9216-bit, 4-prime batch).
Reliable measurement requires ≥ 30 primes; 100 is recommended.

**ProvablePrimeGen (Maurer recursion):**

| Bit length | Time / prime | Recursion depth | Proved large factor |
|---|---|---|---|
| 512 | ~0.1 s | 5 | 257 bits |
| 2048 | ~6 s | 7 | 1025 bits |

At larger bit lengths (4096–8192), Maurer recursion is substantially slower
(order of minutes) due to nested prime searches. The two generators therefore
have distinct roles: **StrongPrimeGen for speed, ProvablePrimeGen for full
formal rigor.**

---

## 6. Two independent verification paths

The system's core design principle is that any output can be confirmed by two
independent methods:

1. **Certificate path (deterministic):** recompute the Pocklington–Lehmer proof.
   A prime cannot be forged; the certificate alone is sufficient.
2. **Information-theoretic path (statistical):** the dashboard measures whether
   the output is structurally distinguishable from random primes.

On all reference batches, both paths agreed — this is what makes the results
defensible, as opposed to any single, non-reproducible claim.

---

## 7. Security scope and honest caveats

- **The construction is relevant only when used appropriately.** As a shared
  secret, the prime's internal structure is immaterial; as a public-key parameter
  (RSA modulus, DH prime), it matters — hence the importance of fingerprint-free
  (`R0 = 0`) mode and the strength guarantee.
- **p−1 strength is guaranteed; p+1 (Williams p+1 attack) is not enforced.**
  For a random prime this is practically never a concern, but full two-sided
  strength (Gordon-complete mode) requires an additional step (see Section 9,
  Roadmap).
- **Standards compliance.** The engine is a generation method; deployment in a
  certified environment (FIPS 186-5, Common Criteria) requires a formal
  conformance assessment. The certificates are added value, not a replacement for
  standard cryptographic infrastructure.
- **Fingerprint freedom is measured, not assumed.** The dashboard reports leakage
  in bits; for `R0 = 0` mode this is ~0, at the level of statistical noise.

---

## 8. Use cases (where this genuinely fits)

- **Cryptographic test vectors and benchmarking:** reproducible, certified primes
  with known structure.
- **Research and education:** provable prime generation, prime structure analysis,
  entropy measurement methodology.
- **Auditable prime supply:** where the property "every prime is proved and the
  certificate is transferable to an independent party" carries value.
- **Open verification tool:** the dashboard can independently assess any
  compatible prime bundle, regardless of its source.

---

## 9. Output format and roadmap

**Output:** certified JSON bundle (metadata + primes with certificates +
content SHA-256 hash). The dashboard handles both certificate formats (flat
Pocklington and recursive Maurer tree).

**Roadmap:**

- Optional p+1 strength enforcement (two-sided, Gordon-complete mode)
- Large-bitlength ProvablePrimeGen acceleration (parallel embedded search)
- Additional dashboard panels (L-Zero correlation, modulus depth) on clean-mode
  batches
- Formal conformance documentation for a specific target standard

---

## 10. Licensing

**Source code** (TPF_StrongPrimeGen, TPF_ProvablePrimeGen, TPF_Entropy_Lab,
prime_verifier, and all associated `.py` and `.html` files) is released under the
**Business Source License 1.1**:
- Non-commercial use (research, audit, education, internal evaluation) is free.
- Commercial use requires a separate agreement with the Licensor.
- On **2030-06-17**, the license converts automatically to **Apache License 2.0**,
  at which point the code becomes fully open source.

**Documentation** (this document and all `.md` and `.pdf` files in the
repository) is released under **CC BY-NC 4.0**.

For commercial licensing inquiries, contact: László Tatai — BarefootRealism Labs

---

## 11. Provenance and reproducibility

All components run on a single laptop using open tools (CPython, browser
JavaScript). Reference measurements are reproducible with the published seeds.
The generator and the dashboard are independently verifiable; every numerical
claim in this document derives from the reference runs noted in Section 5.

**Components:**
`TPF_StrongPrimeGen_v1_2.py` · `TPF_ProvablePrimeGen_v1_0.py` ·
`TPF_Entropy_Lab_v1_1.html` · `prime_verifier.py` (independent verifier)

**Zenodo DOI:** https://doi.org/10.5281/zenodo.19698943
**ORCID:** 0009-0007-5153-6306

---

*BarefootRealism Labs — László Tatai, 2026.
This work is free for non-commercial use; the goal is a reproducible, defensible result.*
