import json
from pathlib import Path

from multihopper_explorer.routes import discover_jupiter_routes, route_from_jupiter_quote
from multihopper_explorer.tx_size import SizeLabel, assess_jupiter_quote_tx_size

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "jupiter"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_discover_two_hop_from_recorded_quote():
    quote = _load("usdc_sol_2hop.json")
    routes = discover_jupiter_routes(quote, hop_counts=(2,))
    assert len(routes) == 1
    assert routes[0].hop_count == 2
    assert len(routes[0].legs) == 2


def test_three_hop_synthetic_route_plan():
    quote = _load("synthetic_3hop.json")
    routes = discover_jupiter_routes(quote, hop_counts=(3,))
    assert len(routes) == 1
    assert routes[0].hop_count == 3


def test_recorded_fixture_tx_size_fits():
    quote = _load("usdc_sol_2hop.json")
    verdict = assess_jupiter_quote_tx_size(quote, build_swap=False)
    assert verdict.label == SizeLabel.FITS
    assert verdict.byte_length is not None
    assert verdict.byte_length <= 1232


def test_route_from_quote_path_mints():
    quote = _load("usdc_sol_2hop.json")
    route = route_from_jupiter_quote(quote)
    assert route.path_mints[0] == quote["inputMint"]
    assert route.path_mints[-1] == quote["outputMint"]
