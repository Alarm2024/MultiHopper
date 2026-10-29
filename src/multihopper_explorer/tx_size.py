"""Transaction size preflight against the 1232-byte Solana packet limit."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from multihopper_explorer.constants import SOLANA_TX_PACKET_LIMIT_BYTES
from multihopper_explorer.jupiter import JupiterError, build_swap_transaction_base64


class SizeLabel(StrEnum):
    FITS = "FITS"
    TOO_BIG = "TOO BIG"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class SizeVerdict:
    label: SizeLabel
    byte_length: int | None
    limit_bytes: int
    detail: str | None = None


def measure_base64_tx_bytes(tx_base64: str) -> int:
    return len(base64.b64decode(tx_base64, validate=True))


def classify_byte_length(length: int, *, limit: int = SOLANA_TX_PACKET_LIMIT_BYTES) -> SizeLabel:
    if length <= limit:
        return SizeLabel.FITS
    return SizeLabel.TOO_BIG


def assess_serialized_tx_base64(
    tx_base64: str | None,
    *,
    limit: int = SOLANA_TX_PACKET_LIMIT_BYTES,
) -> SizeVerdict:
    if not tx_base64:
        return SizeVerdict(
            label=SizeLabel.UNKNOWN,
            byte_length=None,
            limit_bytes=limit,
            detail="no serialized transaction available",
        )
    try:
        length = measure_base64_tx_bytes(tx_base64)
    except Exception as exc:
        return SizeVerdict(
            label=SizeLabel.UNKNOWN,
            byte_length=None,
            limit_bytes=limit,
            detail=f"could not decode transaction: {exc}",
        )
    return SizeVerdict(
        label=classify_byte_length(length, limit=limit),
        byte_length=length,
        limit_bytes=limit,
    )


def assess_jupiter_quote_tx_size(
    quote: dict[str, Any],
    *,
    user_pubkey: str | None = None,
    base_url: str | None = None,
    build_swap: bool = True,
) -> SizeVerdict:
    """
    Dry preflight: build Jupiter's unsigned swap transaction and measure wire size.

    When ``build_swap`` is False (e.g. offline fixtures in tests), returns UNKNOWN unless
    the quote dict already contains ``_fixtureSwapTransactionBase64``.
    """
    limit = SOLANA_TX_PACKET_LIMIT_BYTES
    fixture_tx = quote.get("_fixtureSwapTransactionBase64")
    if isinstance(fixture_tx, str):
        return assess_serialized_tx_base64(fixture_tx, limit=limit)

    if not build_swap:
        return SizeVerdict(
            label=SizeLabel.UNKNOWN,
            byte_length=None,
            limit_bytes=limit,
            detail="swap build skipped",
        )

    kwargs: dict[str, Any] = {}
    if user_pubkey:
        kwargs["user_pubkey"] = user_pubkey
    if base_url:
        kwargs["base_url"] = base_url

    try:
        tx_b64 = build_swap_transaction_base64(quote, **kwargs)
    except JupiterError as exc:
        return SizeVerdict(
            label=SizeLabel.UNKNOWN,
            byte_length=None,
            limit_bytes=limit,
            detail=str(exc),
        )

    return assess_serialized_tx_base64(tx_b64, limit=limit)


def assess_multihopper_prepared_bundle(
    prepared: dict[str, Any],
    *,
    limit: int = SOLANA_TX_PACKET_LIMIT_BYTES,
) -> SizeVerdict:
    """
    Worst-case single-transaction size in a MultiHopper /prepare bundle.

    MultiHopper routes may require several transactions; this marks TOO BIG if any
    individual serialized tx exceeds the packet limit.
    """
    candidates: list[str] = []

    route_init = prepared.get("routeInitTxs") or []
    for item in route_init:
        if isinstance(item, dict) and isinstance(item.get("base64"), str):
            candidates.append(item["base64"])

    for key in ("orchestratorInitTx", "keeperFundingTx"):
        val = prepared.get(key)
        if isinstance(val, str):
            candidates.append(val)

    for key in ("sessionInitTxs", "dispersionInitTxs"):
        for val in prepared.get(key) or []:
            if isinstance(val, str):
                candidates.append(val)

    if not candidates:
        return SizeVerdict(
            label=SizeLabel.UNKNOWN,
            byte_length=None,
            limit_bytes=limit,
            detail="no base64 transactions in bundle",
        )

    max_len = 0
    for tx in candidates:
        try:
            max_len = max(max_len, measure_base64_tx_bytes(tx))
        except Exception:
            return SizeVerdict(
                label=SizeLabel.UNKNOWN,
                byte_length=None,
                limit_bytes=limit,
                detail="invalid base64 in prepared bundle",
            )

    label = classify_byte_length(max_len, limit=limit)
    return SizeVerdict(label=label, byte_length=max_len, limit_bytes=limit)
