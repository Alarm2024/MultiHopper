# MultiHopper Build & Route — project brief

This document summarizes the **Superteam Earn** listing and MultiHopper campaign rules for **Alarm2024/MultiHopper**. It is not legal advice. Where sources disagree or omit detail, this repo marks **UNKNOWN** rather than guessing.

## Official sources

| Source | URL |
|--------|-----|
| Superteam Earn listing | https://superteam.fun/earn/listing/multihopper-build-and-route-challenge-up-to-dollar50000-revenue-share-1/ |
| Campaign page | https://business.multihopper.com/build-and-route/ |
| Machine-readable campaign facts | https://business.multihopper.com/llms.txt |
| MultiHopper OpenAPI | https://multihopper.com/openapi.json |
| Developer docs | https://dev-docs.multihopper.com/ |

## What must be built (campaign)

Per the Earn listing and campaign materials, entrants must:

1. **Ship a working Solana product** that **integrates MultiHopper** and complete **production onboarding** (partner / integration setup — exact steps are on MultiHopper developer docs).
2. **Do not submit** on Earn until MultiHopper is integrated in the product being judged.
3. Generate at least **$100,000 qualifying production volume** per product during the **common measurement window**, through the **MultiHopper-integrated product** (not a different app in your stack).
4. **Only production (mainnet) volume counts**; devnet volume does not qualify.
5. Pass **functionality, security, and genuine-usage** review.
6. **Rank** by verified, fee-adjusted transaction volume; **product quality and repeat usage** break ties.

Qualifying volume (from Earn): collected MultiHopper percentage fees ÷ **0.0025**, with exclusions (failed, refunded, free, devnet, circular, prize-farming, etc.). See the listing for the full rule set.

### What to submit (Earn)

- Live product URL and short demo video  
- Problem description and MultiHopper integration explanation  
- Repository or review access and technical documentation  
- Registered integration identifier and verifiable transaction evidence  
- Qualifying-volume summary, genuine customer / use-case evidence, contact details  
- Traction metrics and growth stats (sensitive evidence may be private to reviewers)  
- **All entries must be submitted on Superteam Earn**

### Product ideas (non-exhaustive)

The listing suggests privacy-oriented sends, launch distribution, migration tools, swaps with hooks, agent treasuries, stablecoin payments, OTC settlement, treasury automation, agent commerce, creator payouts, etc. Integrators use the standard API, programmable routes, and/or Multi-Send as needed.

## Deadline (Africa/Cairo)

| Milestone | Date (from published materials) | Cairo note |
|-----------|----------------------------------|------------|
| Campaign measurement window | **21 Oct 2026 → 30 Nov 2026** | End date **30 November 2026**; **exact UTC start/cutoff timestamps** were still being aligned on the campaign site as of Oct 2026 → **UNKNOWN** for hour-level Cairo deadline |
| Winner announcement (Earn UI) | **28 Dec 2026** (sponsor-scheduled) | **28 December 2026** — time of day **UNKNOWN** |
| Winner announcement (organizer note) | **14 Dec 2026** mentioned on business site | Conflicts with Earn → **UNKNOWN** until aligned |

Use **30 Nov 2026 (Africa/Cairo)** as the planning deadline for campaign volume and submission readiness; confirm exact cutoff on Earn before final submission.

## Judging and prizes

- **Guaranteed prize pool:** **$5,000 USDC** (Earn UI); pool can grow toward **$50,000** based on **aggregate qualifying campaign volume** (see listing formulas).
- **Integration revenue:** **0.25%** of the entrant’s own **full-fee** volume (separate from prizes; partner terms apply).
- **Prize eligibility:** **$100k+** qualifying production volume per product (Oct 2026 clarification on business site).
- **Draft / alignment notes:** Earn and business pages have had **conflicting** wording on fixed vs proportional prize splits and conditions (e.g. $2M aggregate gate for the initial $5k). Treat **Earn + latest organizer clarification** as authoritative when they diverge; details not yet aligned → **UNKNOWN**.

This repository’s **route explorer scaffold** is **read-only** (quotes + transaction size estimates). It is **not** a finished Earn submission and **does not** integrate production MultiHopper transfers by itself.

## Eligibility and KYC

- **Geography / team:** Listing describes a **global** Superteam Earn bounty; specific country restrictions → **UNKNOWN** (check Earn at submission time).
- **KYC / identity:** Superteam Earn payouts typically require identity verification for winners; **exact KYC steps for this listing** → **UNKNOWN** here — follow Earn checkout / payout prompts when submitting.
- **Integration onboarding:** Production use requires MultiHopper **partner onboarding** and agreed **revenue-sharing** terms (see business developers page).

## What this repo implements (scaffold)

Read-only **multi-hop route explorer** (ideas aligned with a planned `route-lens`-style tool):

- For a **token pair**, list **2-hop** and **3-hop** swap routes using **public Jupiter quote APIs** (and optional composite paths via configured intermediates).
- **Estimate serialized transaction size** against Solana’s **1232-byte** packet limit using Jupiter’s unsigned swap transaction build (dry preflight — no wallet, no signing, no sending).
- Label each route **`FITS`**, **`TOO BIG`**, or **`UNKNOWN`**.
- **Tests** use **recorded quote fixtures**; CI does not require live API keys.

## Out of scope for this scaffold

- No wallets, keys, signing, broadcasting, or live trading claims  
- No profit, guarantee, audit, or “launched” claims  
- No production MultiHopper API integration (requires integrator credentials)

## Remaining work toward 30 Nov 2026

See root [README.md](../README.md) and the draft PR description for the checklist (integration, mainnet volume, Earn submission, demo, docs).
