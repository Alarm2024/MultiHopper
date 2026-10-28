"""Discover 2-hop and 3-hop routes from public quote APIs."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from multihopper_explorer.constants import DEFAULT_INTERMEDIATE_MINTS
from multihopper_explorer.jupiter import fetch_quote


@dataclass
class RouteLeg:
    input_mint: str
    output_mint: str
    label: str | None = None


@dataclass
class RouteCandidate:
    hop_count: int
    source: str
    legs: list[RouteLeg] = field(default_factory=list)
    quote: dict[str, Any] | None = None
    notes: str | None = None

    @property
    def path_mints(self) -> list[str]:
        if not self.legs:
            return []
        mints = [self.legs[0].input_mint]
        for leg in self.legs:
            mints.append(leg.output_mint)
        return mints


def _legs_from_jupiter_route_plan(quote: dict[str, Any]) -> list[RouteLeg]:
    legs: list[RouteLeg] = []
    for step in quote.get("routePlan") or []:
        if not isinstance(step, dict):
            continue
        info = step.get("swapInfo") or {}
        if not isinstance(info, dict):
            continue
        in_m = info.get("inputMint")
        out_m = info.get("outputMint")
        if not isinstance(in_m, str) or not isinstance(out_m, str):
            continue
        legs.append(
            RouteLeg(
                input_mint=in_m,
                output_mint=out_m,
                label=info.get("label") if isinstance(info.get("label"), str) else None,
            )
        )
    return legs


def route_from_jupiter_quote(quote: dict[str, Any], *, source: str = "jupiter") -> RouteCandidate:
    legs = _legs_from_jupiter_route_plan(quote)
    return RouteCandidate(
        hop_count=len(legs),
        source=source,
        legs=legs,
        quote=quote,
    )


def discover_jupiter_routes(
    quote: dict[str, Any],
    *,
    hop_counts: Iterable[int] = (2, 3),
) -> list[RouteCandidate]:
    """Extract routes whose Jupiter ``routePlan`` length matches requested hop counts."""
    wanted = set(hop_counts)
    primary = route_from_jupiter_quote(quote)
    found: list[RouteCandidate] = []
    if primary.hop_count in wanted:
        found.append(primary)

    for alt in quote.get("otherRoutePlans") or []:
        if not isinstance(alt, list):
            continue
        synthetic = {**quote, "routePlan": alt}
        candidate = route_from_jupiter_quote(synthetic, source="jupiter.otherRoutePlans")
        paths = [r.path_mints for r in found]
        if candidate.hop_count in wanted and candidate.path_mints not in paths:
            found.append(candidate)
    return found


def discover_composite_routes(
    *,
    input_mint: str,
    output_mint: str,
    amount_raw: str,
    hop_counts: Iterable[int] = (2, 3),
    intermediates: Iterable[str] = DEFAULT_INTERMEDIATE_MINTS,
    slippage_bps: int = 50,
    base_url: str | None = None,
    fetcher=fetch_quote,
) -> list[RouteCandidate]:
    """
    Enumerate 2- and 3-hop composite swap paths A→I→B and A→I1→I2→B using quote legs.

    Each composite path uses two or three sequential quotes; amounts chain using the prior
    ``outAmount``. This is an exploration heuristic, not a guarantee of executable routes.
    """
    wanted = set(hop_counts)
    results: list[RouteCandidate] = []
    ints = [m for m in intermediates if m not in (input_mint, output_mint)]

    fetch_kwargs: dict[str, Any] = {"slippage_bps": slippage_bps}
    if base_url:
        fetch_kwargs["base_url"] = base_url

    if 2 in wanted:
        for mid in ints:
            try:
                q1 = fetcher(
                    input_mint=input_mint,
                    output_mint=mid,
                    amount_raw=amount_raw,
                    **fetch_kwargs,
                )
                q2 = fetcher(
                    input_mint=mid,
                    output_mint=output_mint,
                    amount_raw=str(q1.get("outAmount", amount_raw)),
                    **fetch_kwargs,
                )
            except Exception:
                continue
            legs = _legs_from_jupiter_route_plan(q1) + _legs_from_jupiter_route_plan(q2)
            cand = RouteCandidate(
                hop_count=len(legs),
                source="jupiter.composite",
                legs=legs,
                quote=q2,
                notes=f"composite via {mid}",
            )
            if cand.hop_count == 2 and cand.path_mints not in [r.path_mints for r in results]:
                results.append(cand)

    if 3 in wanted:
        for mid1 in ints:
            for mid2 in ints:
                if mid1 == mid2:
                    continue
                try:
                    q1 = fetcher(
                        input_mint=input_mint,
                        output_mint=mid1,
                        amount_raw=amount_raw,
                        **fetch_kwargs,
                    )
                    q2 = fetcher(
                        input_mint=mid1,
                        output_mint=mid2,
                        amount_raw=str(q1.get("outAmount", amount_raw)),
                        **fetch_kwargs,
                    )
                    q3 = fetcher(
                        input_mint=mid2,
                        output_mint=output_mint,
                        amount_raw=str(q2.get("outAmount", amount_raw)),
                        **fetch_kwargs,
                    )
                except Exception:
                    continue
                legs = (
                    _legs_from_jupiter_route_plan(q1)
                    + _legs_from_jupiter_route_plan(q2)
                    + _legs_from_jupiter_route_plan(q3)
                )
                cand = RouteCandidate(
                    hop_count=len(legs),
                    source="jupiter.composite",
                    legs=legs,
                    quote=q3,
                    notes=f"composite via {mid1} then {mid2}",
                )
                if cand.hop_count == 3 and cand.path_mints not in [r.path_mints for r in results]:
                    results.append(cand)
    return results


def explore_token_pair(
    *,
    input_mint: str,
    output_mint: str,
    amount_raw: str,
    hop_counts: Iterable[int] = (2, 3),
    include_composite: bool = True,
    slippage_bps: int = 50,
    base_url: str | None = None,
) -> list[RouteCandidate]:
    """Fetch a primary Jupiter quote and merge direct + composite hop-filtered routes."""
    fetch_kwargs: dict[str, Any] = {"slippage_bps": slippage_bps}
    if base_url:
        fetch_kwargs["base_url"] = base_url

    quote = fetch_quote(
        input_mint=input_mint,
        output_mint=output_mint,
        amount_raw=amount_raw,
        **fetch_kwargs,
    )
    routes = discover_jupiter_routes(quote, hop_counts=hop_counts)
    if include_composite:
        routes.extend(
            discover_composite_routes(
                input_mint=input_mint,
                output_mint=output_mint,
                amount_raw=amount_raw,
                hop_counts=hop_counts,
                slippage_bps=slippage_bps,
                base_url=base_url,
            )
        )
    # De-dupe by path
    unique: list[RouteCandidate] = []
    seen: set[tuple[str, ...]] = set()
    for r in routes:
        key = tuple(r.path_mints)
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    return unique
