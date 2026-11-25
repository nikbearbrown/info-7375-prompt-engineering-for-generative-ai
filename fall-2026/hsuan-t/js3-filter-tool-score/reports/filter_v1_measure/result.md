# FILTER v1 measurements — `evidence/raw/2026-11-08T234257Z/`, 2046 postings

## W1 — substring match for rule 3

Postings cut at rule 3 by v1 that substring matching would pass: **937** of 2046.

| résumé keyword | JDs where it appears only inside another word |
|---|---|
| AWS | 1231 |
| Rust | 1210 |
| Java | 175 |
| SQL | 28 |
| Redis | 2 |
| Helm | 1 |

## L1 — city names and abbreviations in `profile.locations`

Pass rules 1a + 1b but cut at rule 2 under v1: **54**.

Rule 2 cut → pass when adding ['ny', 'sea', 'sf', 'nyc', 'seattle', 'san francisco', 'new york']: **7**.

| board | passes title rules | title | location |
|---|---|---|---|
| stripe | True | Backend Engineer, Developer SDKs | Toronto, NY, SEA, SF; Canada Locations |
| cloudflare | False | Named Sales Director, PacNW (Seattle) | Hybrid; Seattle, WA |
| cloudflare | False | Principal Engineer | Hybrid; Seattle, WA |
| cloudflare | False | Senior Account Executive, SLED (PacNW) | Distributed; Seattle, WA |
| cloudflare | False | Senior Customer Engineer, Named - Seattle | Distributed; Seattle, WA |
| cloudflare | False | Senior Digital Native Named Account Executive - Seattle | Distributed; Seattle, WA |
| cloudflare | False | Senior Territory Account Executive, Seattle | Hybrid; Seattle, WA |
