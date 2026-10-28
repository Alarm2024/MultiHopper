"""CLI for read-only route exploration."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from multihopper_explorer.jupiter import load_quote_fixture
from multihopper_explorer.routes import RouteCandidate, explore_token_pair, route_from_jupiter_quote
from multihopper_explorer.tx_size import SizeLabel, assess_jupiter_quote_tx_size


def _route_to_json(
    route: RouteCandidate,
    verdict_label: SizeLabel,
    verdict_detail: dict[str, Any],
) -> dict[str, Any]:
    return {
        "hopCount": route.hop_count,
        "source": route.source,
        "pathMints": route.path_mints,
        "legs": [
            {"inputMint": leg.input_mint, "outputMint": leg.output_mint, "label": leg.label}
            for leg in route.legs
        ],
        "notes": route.notes,
        "txSize": verdict_detail,
        "sizeLabel": verdict_label.value,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only multi-hop route explorer (public quotes + tx size preflight)",
    )
    parser.add_argument("--input-mint", help="Source token mint")
    parser.add_argument("--output-mint", help="Destination token mint")
    parser.add_argument("--amount-raw", default="1000000", help="Input amount in base units")
    parser.add_argument("--hop-counts", default="2,3", help="Comma-separated hop counts to list")
    parser.add_argument("--fixture", help="Path to recorded Jupiter quote JSON (offline mode)")
    parser.add_argument(
        "--no-live-swap-build",
        action="store_true",
        help="Do not call Jupiter /swap (tx size will be UNKNOWN unless fixture embeds tx)",
    )
    parser.add_argument(
        "--no-composite",
        action="store_true",
        help="Skip composite intermediate enumeration (live mode only)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    hop_counts = {int(x.strip()) for x in args.hop_counts.split(",") if x.strip()}

    if args.fixture:
        quote = load_quote_fixture(args.fixture)
        routes = [route_from_jupiter_quote(quote)]
        routes = [r for r in routes if r.hop_count in hop_counts]
    else:
        if not args.input_mint or not args.output_mint:
            parser.error("--input-mint and --output-mint are required without --fixture")
        routes = explore_token_pair(
            input_mint=args.input_mint,
            output_mint=args.output_mint,
            amount_raw=args.amount_raw,
            hop_counts=hop_counts,
            include_composite=not args.no_composite,
        )

    rows: list[dict[str, Any]] = []
    for route in routes:
        quote_for_size = route.quote or {}
        verdict = assess_jupiter_quote_tx_size(
            quote_for_size,
            build_swap=not args.no_live_swap_build,
        )
        detail = {
            "bytes": verdict.byte_length,
            "limitBytes": verdict.limit_bytes,
            "detail": verdict.detail,
        }
        rows.append(_route_to_json(route, verdict.label, detail))

    if args.json:
        print(json.dumps({"routes": rows}, indent=2))
    else:
        if not rows:
            print("No routes matched the requested hop counts.")
        for row in rows:
            path = " -> ".join(m[:8] for m in row["pathMints"])
            print(
                f"[{row['sizeLabel']}] {row['hopCount']}-hop ({row['source']}) {path} "
                f"bytes={row['txSize']['bytes']!s}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
