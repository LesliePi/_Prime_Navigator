# TPF Prime Engine

**Deterministic, auditable, measurably fingerprint-free prime generation and certification**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19698943.svg)](https://doi.org/10.5281/zenodo.19698943)
[![License: BUSL-1.1](https://img.shields.io/badge/License-BUSL--1.1-blue.svg)](LICENSE)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0007--5153--6306-green)](https://orcid.org/0009-0007-5153-6306)

**Author:** László Tatai — BarefootRealism Labs
**Version:** 1.0 · June 2026

---

## What it is

A prime generation and certification toolkit built from well-established components:
Pocklington–Lehmer, Maurer's recursive algorithm (1995), Hardy–Littlewood,
and Shannon entropy. The value is not a new primitive — it is the arrangement of
these known elements into a **single, measurable, bilaterally verifiable pipeline**.

Every prime comes with a certificate that proves primality as a theorem, not as
the result of a probabilistic test. An independent browser-based dashboard
re-verifies those certificates and measures the information-theoretic cleanliness
of the output — without access to the generator.

**What it is not:** new cryptography. It does not replace standard PKI.
Security rests on input entropy and mathematical structure (Kerckhoffs's principle),
never on a secret algorithm.

---

## Components

| File | Role |
|---|---|
| `TPF_StrongPrimeGen_v1_2.py` | Fast certified strong prime (Pocklington–Lehmer, flat certificate) |
| `TPF_ProvablePrimeGen_v1_1.py` | Fully recursive provable prime (Maurer tree to trivially-verifiable small primes) |
| `TPF_Entropy_Lab_v1_2.html` | Self-contained browser dashboard: re-verifies certificates + measures fingerprint and sequence entropy |
| `prime_verifier.py` | Standalone Python verifier (independent of the generators) |

---

## Quick Start

**Dependency:** Python 3.8+, [SymPy](https://www.sympy.org/)

```bash
pip install sympy
```

**Generate and certify strong primes:**
```bash
python TPF_StrongPrimeGen_v1_2.py --bits 1024 --count 100 --R0 0 --out primes.json
```

**Generate fully provable primes (Maurer recursive):**
```bash
python TPF_ProvablePrimeGen_v1_1.py --bits 2048 --count 32 --out provable.json
```

**Verify a bundle independently (Python):**
```bash
python prime_verifier.py primes.json
```

**Measure fingerprint and entropy (browser):**
Open `TPF_Entropy_Lab_v1_2.html` in any modern browser, load the `.json` bundle.
No server, no dependencies — everything runs locally.

---

## Parameters (StrongPrimeGen)

| Parameter | Default | Meaning |
|---|---|---|
| `--bits` | 512 | Target prime bit length |
| `--R0` | 0 | Jacobi fingerprint bound (0 = no fingerprint) |
| `--r-bits` | ~bits/2 | Large prime factor size in p−1 (Pollard p−1 resistance) |
| `--safe` | off | Gordon-style two-level strength (r−1 also has large factor) |
| `--force-3` | off | Force 3 into N−1 (adds 1 bit mod-3 leakage — control use only) |
| `--seed` | random | Reproducibility seed |
| `--count` | 3 | Number of primes to generate |

---

## What is guaranteed — and what is not

| Property | Guaranteed | How verified |
|---|---|---|
| Primality | ✓ deterministic (Pocklington–Lehmer theorem) | Certificate recomputation; Maurer tree to small primes |
| Pollard p−1 resistance | ✓ large prime factor r ≈ bits/2 in p−1 | r is prime + r \| (N−1) + bit length |
| Jacobi fingerprint freedom | ✓ for R0=0 (measured, not assumed) | Dashboard residue entropy in bits |
| Williams p+1 resistance | ✗ not enforced (roadmap item) | — |
| FIPS/CC compliance | ✗ requires separate assessment | — |

**Inherent structural property of StrongPrimeGen:**
`N ≡ 1 (mod 4)` always — because `N−1 = 2^a · Q · r · t` with `a >> 2`.
This is a known, documented consequence of the construction, not a security
weakness for RSA or DH use cases. For protocols requiring Blum primes
(p ≡ 3 mod 4, e.g. Blum–Blum–Shub), this engine is not appropriate.

---

## Measured performance

All figures from a single laptop (CPython). Reproducible with the published seeds.

**StrongPrimeGen (R0=0):**

| Bits | Time/prime | p−1 large factor |
|---|---|---|
| 512 | ~0.03–0.08 s | ~248 bits |
| 1024 | ~0.05–0.3 s | ~504 bits |
| 2048 | ~0.5–2 s | ~1016 bits |

**ProvablePrimeGen (Maurer recursive):**

| Bits | Time/prime | Recursion depth | Proved large factor |
|---|---|---|---|
| 512 | ~0.1 s | 5 | 257 bits |
| 2048 | ~6 s | 7 | 1025 bits |

For large bit lengths (4096+), ProvablePrimeGen is substantially slower (minutes).
Use StrongPrimeGen for speed, ProvablePrimeGen where full formal rigor is required.

---

## Two independent verification paths

1. **Certificate path (deterministic):** recompute the Pocklington–Lehmer proof.
   A prime cannot be forged; the certificate alone is sufficient.
2. **Information-theoretic path (statistical):** the dashboard measures whether
   the output is structurally distinguishable from random primes.

On all reference batches both paths agreed — this is what makes results defensible.

---

## Licensing

**Source code** (`*.py`, `*.html`): [Business Source License 1.1](LICENSE)
- Non-commercial use (research, audit, education) is **free**
- Commercial use requires a separate agreement
- Converts automatically to **Apache License 2.0** on **2030-06-17**

**Documentation** (`*.md`, `*.pdf`): CC BY-NC 4.0

For commercial licensing: László Tatai — BarefootRealism Labs

---

## Citation

```bibtex
@software{tatai2026tpf,
  author  = {Tatai, László},
  title   = {{TPF Prime Engine}: Deterministic, Auditable, Measurably Clean
              Prime Generation and Certification},
  year    = {2026},
  doi     = {10.5281/zenodo.19698943},
  url     = {https://doi.org/10.5281/zenodo.19698943},
  orcid   = {0009-0007-5153-6306}
}
```

---

*BarefootRealism Labs — László Tatai, 2026.
Free for non-commercial use. The goal is a reproducible, defensible result.*
