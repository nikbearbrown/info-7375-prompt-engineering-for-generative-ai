# False-friend candidates (mechanical; generated 2026-11-25)

**Open this only after you have filled `audit/audit-sheet.csv`.** Nothing here is a finding. A candidate is a match that *may* be for the wrong reason. The false friend is named by Aravind, from a posting judged by hand.

"Intro" means text before the first role heading (/what you(?:'|’)ll do|responsibilities|about the role|in this role|the opportunity|what you will do/i); in this snapshot that is usually the company's "About us" text. Spec v1.0.0.

## 1. Corpus: topic terms that match only in the company intro

| board | term | postings matching | of | match only in intro |
|---|---|---|---|---|
| gh-airbnb | payments | 30 | 203 | 5 |
| gh-airbnb | fintech | 7 | 203 | 0 |
| gh-airbnb | data | 148 | 203 | 3 |
| gh-airbnb | e-commerce | 9 | 203 | 0 |
| gh-airbnb | ecommerce | 1 | 203 | 0 |
| gh-airbnb | mobile | 5 | 203 | 0 |
| gh-stripe | payments | 746 | 776 | 349 |
| gh-stripe | fintech | 166 | 776 | 2 |
| gh-stripe | data | 403 | 776 | 32 |
| gh-stripe | e-commerce | 27 | 776 | 0 |
| gh-stripe | ecommerce | 16 | 776 | 3 |
| gh-stripe | mobile | 23 | 776 | 3 |
| lv-spotify | payments | 3 | 85 | 0 |
| lv-spotify | data | 71 | 85 | 0 |
| lv-spotify | e-commerce | 1 | 85 | 0 |
| lv-spotify | mobile | 14 | 85 | 10 |

## 2. Audit rows: each match that might be for the wrong reason

### A001 (gh-stripe) Security Engineer, New Grad
- decision **reject**, score 0.225; strata: random_reject
- topic **payments** matched only in the intro: …est enterprises to the most ambitious startups - use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…
- title junior override by **New Grad** in "Security Engineer, New Grad"

### A003 (gh-stripe) Account Executive, SMB Hunter
- decision **reject**, score 0.05; strata: random_reject
- topic **payments** matched only in the intro: …est enterprises to the most ambitious startups - use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A006 (gh-stripe) Specialist Solutions Architect, Billing
- decision **reject**, score 0.3; strata: random_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A007 (gh-stripe) Sales Manager, Product - Issuing & Treasury
- decision **reject**, score 0.3; strata: random_reject
- location matched alias **sf -> San Francisco** in "NYC, SF"

### A008 (gh-stripe) Product Support Operations Associate, Weekend Shift
- decision **reject**, score 0.175; strata: random_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…
- title junior override by **Associate** in "Product Support Operations Associate, Weekend Shift"

### A009 (gh-stripe) Managing Editor, Stripe Press
- decision **reject**, score 0.175; strata: random_reject
- topic **payments** matched only in the intro: …est enterprises to the most ambitious startups - use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A016 (gh-stripe) Corporate Security Infrastructure Project Manager, EMEA
- decision **reject**, score 0.05; strata: random_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A017 (gh-stripe) Software Engineer, Internal Identity
- decision **reject**, score 0.3; strata: random_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A022 (gh-stripe) Product Manager, Connect Growth & Monetization
- decision **cannot_tell**, score 0.875; strata: cannot_tell, closest_call
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…
- topic **ecommerce** matched only in the intro: …ect is Stripe’s leading product for marketplaces, on-demand services, ecommerce site builders, invoicing platforms, professional SaaS products, fundr…

### A026 (gh-stripe) Lifecycle Marketing Manager, Capital
- decision **reject**, score 0.35; strata: random_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A027 (gh-stripe) Technical Program Manager, Extensibility
- decision **reject**, score 0.75; strata: closest_call
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…
- topic **data** matched only in the intro: …alculations, invoice logic, proration). Custom Objects — User-defined data models (e.g., Shipments, Locations, Warranties, Entitlements) with fi…

### A028 (gh-stripe) Workplace Design Coordinator
- decision **reject**, score 0.3; strata: random_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…
- location matched alias **sf -> San Francisco** in "SF, NYC, SEA, TOR"

### A032 (gh-stripe) Staff Product Manager,  Startup Products
- decision **reject**, score 0.55; strata: random_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A033 (gh-stripe) SOX Business Controls Specialist
- decision **reject**, score 0.35; strata: random_reject
- location matched alias **sf -> San Francisco** in "SEA, SF"

### A034 (gh-stripe) Head of Specialist Solutions Architecture, Revenue Suite (AMER)
- decision **reject**, score 0.3; strata: random_reject
- location matched alias **sf -> San Francisco** in "SF"

### A040 (gh-stripe) Backend Engineer, UI Platform
- decision **reject**, score 0.35; strata: random_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A043 (gh-stripe) Specialist Solutions Architect, Fraud & Risk (Asia-Pacific)
- decision **reject**, score 0.1; strata: random_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A044 (gh-stripe) Technical Program Manager, Extensibility Platform
- decision **reject**, score 0.75; strata: closest_call
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…
- topic **data** matched only in the intro: …alculations, invoice logic, proration). Custom Objects — User-defined data models (e.g., Shipments, Locations, Warranties, Entitlements) with fi…

### A045 (gh-stripe) Backend Engineer, Link
- decision **reject**, score 0.3; strata: random_reject
- location matched alias **sf -> San Francisco** in "NYC, Sea, SF, Tor"

### A052 (gh-stripe) Technical Program Manager, Money-as-a-Service
- decision **reject**, score 0.75; strata: closest_call
- topic **payments** matched only in the intro: …est enterprises to the most ambitious startups - use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A054 (gh-stripe) Firmware Engineer
- decision **reject**, score 0.35; strata: random_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A056 (gh-stripe) Security GRC Program Manager, Third Party Risk
- decision **reject**, score 0.225; strata: pm_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A057 (gh-stripe) Head of Product Sales, Payouts
- decision **reject**, score 0.35; strata: pm_reject
- location matched alias **sf -> San Francisco** in "SF, NYC"

### A059 (gh-stripe) Product Designer, Design Systems
- decision **reject**, score 0.35; strata: pm_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A063 (gh-stripe) Backend/API Engineer, Money as a Service (Product)
- decision **reject**, score 0.05; strata: pm_reject
- topic **payments** matched only in the intro: …est enterprises to the most ambitious startups - use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A064 (gh-stripe) Product Design Intern
- decision **reject**, score 0.425; strata: pm_reject
- title junior override by **Intern** in "Product Design Intern"

### A065 (gh-stripe) Product Manager, Sandboxes
- decision **reject**, score 0.7; strata: pm_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A066 (gh-stripe) Staff Product Manager, Agentic Commerce
- decision **reject**, score 0.55; strata: pm_reject
- topic **payments** matched only in the intro: …rgest enterprises to the most ambitious startups—use Stripe to accept payments, grow their revenue, and accelerate new business opportunities. Our m…

### A067 (gh-stripe) Account Executive, Product Sales, Metronome
- decision **reject**, score 0.1; strata: pm_reject
- topic **data** matched only in the intro: …office finance automation across billing, tax, revenue reporting, and data. What you’ll do As a Metronome Account Executive at Stripe, you'll us…

### A068 (gh-stripe) Account Executive, Product - Link
- decision **reject**, score 0.3; strata: pm_reject
- location matched alias **sf -> San Francisco** in "NYC, SF"

### A069 (gh-stripe) Account Executive, Product Sales, Metronome
- decision **reject**, score 0.1; strata: pm_reject
- topic **data** matched only in the intro: …office finance automation across billing, tax, revenue reporting, and data. What you’ll do As a Billing Account Executive at Stripe, you'll use …

### A070 (gh-stripe) Program Manager, Card Network Office (Card Networks)
- decision **reject**, score 0.5; strata: pm_reject
- experience E=0 from a sentence that does not mention product/program: "5+ years of experience in the payments industry, with significant expertise in working with card networks and understanding card network rules and compliance activities."

