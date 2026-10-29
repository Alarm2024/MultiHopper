"""Jupiter public quote/swap HTTP client (read-only)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from multihopper_explorer.constants import DEFAULT_JUPITER_BASE_URL

# Placeholder pubkey for unsigned swap transaction builds (no signing in this tool).
DEFAULT_USER_PUBKEY = "11111111111111111111111111111111"


class JupiterError(RuntimeError):
    pass


def _request_json(
    method: str,
    url: str,
    body: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise JupiterError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise JupiterError(str(exc)) from exc
    return json.loads(raw)


def fetch_quote(
    *,
    input_mint: str,
    output_mint: str,
    amount_raw: str,
    slippage_bps: int = 50,
    base_url: str = DEFAULT_JUPITER_BASE_URL,
) -> dict[str, Any]:
    params = urllib.parse.urlencode(
        {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount_raw,
            "slippageBps": slippage_bps,
        }
    )
    url = f"{base_url.rstrip('/')}/quote?{params}"
    return _request_json("GET", url)


def build_swap_transaction_base64(
    quote: dict[str, Any],
    *,
    user_pubkey: str = DEFAULT_USER_PUBKEY,
    base_url: str = DEFAULT_JUPITER_BASE_URL,
) -> str | None:
    """Return base64 serialized unsigned versioned transaction, or None if absent."""
    url = f"{base_url.rstrip('/')}/swap"
    payload = {"quoteResponse": quote, "userPublicKey": user_pubkey}
    result = _request_json("POST", url, payload)
    swap_tx = result.get("swapTransaction")
    if swap_tx is None:
        return None
    if not isinstance(swap_tx, str):
        raise JupiterError("swapTransaction was not a string")
    return swap_tx


def load_quote_fixture(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise TypeError("fixture must be a JSON object")
    return data
