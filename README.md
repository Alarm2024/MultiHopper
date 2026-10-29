# MultiHopper

Read-only **multi-hop route explorer** scaffold for the [MultiHopper Build & Route](https://superteam.fun/earn/listing/multihopper-build-and-route-challenge-up-to-dollar50000-revenue-share-1/) Superteam bounty.

## What it does

- Lists **2-hop** and **3-hop** swap routes for a token pair using **public Jupiter quote APIs** (plus optional composite paths via configured intermediates).
- **Dry preflight:** builds Jupiter’s **unsigned** swap transaction and measures serialized size against Solana’s **1232-byte** packet limit.
- Labels each route **`FITS`**, **`TOO BIG`**, or **`UNKNOWN`** (no wallet, no keys, no signing, no sending).

Campaign rules, judging, Cairo deadline notes, and KYC pointers: **[docs/brief.md](docs/brief.md)**.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

Live (requires network):

```bash
multihopper-explore \
  --input-mint EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v \
  --output-mint So11111111111111111111111111111111111111112 \
  --amount-raw 1000000 \
  --json
```

Offline with recorded fixtures (CI uses this):

```bash
multihopper-explore --fixture fixtures/jupiter/usdc_sol_2hop.json --no-live-swap-build --json
```

## Tests

```bash
pytest
ruff check src tests
```

## Status

This repo is an **explorer scaffold**, not a production MultiHopper integration. Remaining Earn delivery items are listed in [docs/brief.md](docs/brief.md).

## License

MIT — see [LICENSE](LICENSE).
