"""Read-only multi-hop route explorer (quotes + tx size preflight)."""

from multihopper_explorer.constants import SOLANA_TX_PACKET_LIMIT_BYTES
from multihopper_explorer.routes import RouteCandidate, discover_jupiter_routes
from multihopper_explorer.tx_size import SizeVerdict, assess_jupiter_quote_tx_size

__all__ = [
    "SOLANA_TX_PACKET_LIMIT_BYTES",
    "RouteCandidate",
    "SizeVerdict",
    "assess_jupiter_quote_tx_size",
    "discover_jupiter_routes",
]

__version__ = "0.1.0"
