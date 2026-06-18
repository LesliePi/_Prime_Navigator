# Zenodo Deposit Metadata — TPF Prime Engine v1.0

> Ezt a fájlt töltsd be a Zenodo felületén mezőnként.
> A deposit típusa: **Software**

---

## Alapmezők

**Title:**
```
TPF Prime Engine: Deterministic, Auditable, Measurably Clean Prime Generation and Certification
```

**Authors:**
```
Tatai, László
  Affiliation: BarefootRealism Labs
  ORCID: 0009-0007-5153-6306
```

**Description (angolul — copy-paste a Zenodo abstract mezőbe):**
```
The TPF Prime Engine is a prime generation and certification toolkit built
from well-established components: the Pocklington–Lehmer theorem, Maurer's
recursive prime generation algorithm (1995), Hardy–Littlewood singular series,
and Shannon entropy. Every generated prime carries a certificate that establishes
primality as a theorem, not as the result of a probabilistic test. An
independent, self-contained browser-based dashboard (TPF Entropy Lab) re-verifies
those certificates and measures the information-theoretic cleanliness of the
output — without access to the generator.

Components:
- TPF_StrongPrimeGen_v1_2.py: fast certified strong prime (Pocklington–Lehmer,
  flat certificate; p−1 has a large prime factor ≈ bits/2 for Pollard p−1
  resistance)
- TPF_ProvablePrimeGen_v1_1.py: fully recursive provable prime (Maurer tree
  descending to trivially verifiable small primes; includes --blum flag for
  strong Blum prime generation, p ≡ 3 mod 4, suitable for BBS PRNG and
  Rabin encryption)
- TPF_Entropy_Lab_v1_2.html: self-contained browser dashboard — Pocklington
  and Maurer-tree re-verification, residue fingerprint measurement (including
  mod 4), sequence entropy (K_prim / bigram MI), downloadable measurement
  certificate with SHA-256
- prime_verifier.py: standalone independent Python verifier (no generator
  dependency)

This is not new cryptography. The value lies in the arrangement of known
elements into a single, measurable, bilaterally verifiable pipeline.
Security rests on input entropy and mathematical structure (Kerckhoffs's
principle), never on a secret algorithm.

Licensing: source code under Business Source License 1.1 (non-commercial
use free; converts to Apache 2.0 on 2030-06-17). Documentation under
CC BY-NC 4.0.
```

---

## Verzió és dátum

**Version:** `1.0`

**Publication date:** `2026-06-17`

---

## Licenc

**License:** `Other (Open)`

> Megjegyzés a Zenodo felületén: a Zenodo nem listázza a BUSL 1.1-et saját
> licencopcióként. Válaszd az "Other (Open)" opciót, és a leírásban és a
> LICENSE fájlban egyértelmű a BUSL 1.1 → Apache 2.0 feltétel.

---

## Kulcsszavak (Keywords)

```
prime generation
Pocklington-Lehmer
Maurer algorithm
certified primes
strong primes
Blum primes
Shannon entropy
cryptography
number theory
provable primality
Pollard p-1 resistance
information-theoretic fingerprint
```

---

## Kapcsolódó azonosítók (Related Identifiers)

| Relation | Identifier | Resource type |
|---|---|---|
| `isNewVersionOf` | `10.5281/zenodo.19698943` | Software (PrimSpace v3.0 — előző deposit) |

> Ha új rekordként töltöd fel (nem új verzióként), használd:
> `isDerivedFrom` helyett `references` kapcsolatot.

---

## Feltöltendő fájl

```
tpf_prime_engine_v1_0.zip
```

Tartalom: README.md · LICENSE · CHANGELOG.md ·
TPF_StrongPrimeGen_v1_2.py · TPF_ProvablePrimeGen_v1_1.py ·
prime_verifier.py · TPF_Entropy_Lab_v1_2.html ·
TPF_Prime_Engine_Product_Document_v1_0_EN.md

---

## GitHub README badge (a DOI megkapása után)

A Zenodo deposit után a DOI megváltozhat (ha új rekord, nem új verzió).
Az új DOI-t helyettesítsd be a README.md badge sorába:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

---

*BarefootRealism Labs — László Tatai, 2026*
