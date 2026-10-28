"""Shared constants."""

# Solana serialized transaction packet limit (legacy wire format).
SOLANA_TX_PACKET_LIMIT_BYTES = 1232

# Default public Jupiter quote/swap base URL (no API key required for quotes).
DEFAULT_JUPITER_BASE_URL = "https://lite-api.jup.ag/swap/v1"

# Well-known intermediates for composite 2-/3-hop discovery (mint addresses).
DEFAULT_INTERMEDIATE_MINTS = (
    "So11111111111111111111111111111111111111112",  # SOL / wSOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
)
