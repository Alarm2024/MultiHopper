import base64

from multihopper_explorer.constants import SOLANA_TX_PACKET_LIMIT_BYTES
from multihopper_explorer.tx_size import (
    SizeLabel,
    assess_jupiter_quote_tx_size,
    assess_multihopper_prepared_bundle,
    assess_serialized_tx_base64,
    classify_byte_length,
)


def test_classify_fits_and_too_big():
    assert classify_byte_length(1232) == SizeLabel.FITS
    assert classify_byte_length(1233) == SizeLabel.TOO_BIG


def test_assess_serialized_tx_none_is_unknown():
    verdict = assess_serialized_tx_base64(None)
    assert verdict.label == SizeLabel.UNKNOWN
    assert verdict.byte_length is None


def test_fixture_swap_transaction_fits():
    # 900 bytes of zeros → valid base64 payload, well under limit
    payload = base64.b64encode(b"\x00" * 900).decode()
    quote = {"_fixtureSwapTransactionBase64": payload}
    verdict = assess_jupiter_quote_tx_size(quote, build_swap=False)
    assert verdict.label == SizeLabel.FITS
    assert verdict.byte_length == 900


def test_multihopper_bundle_worst_tx():
    big = base64.b64encode(b"x" * (SOLANA_TX_PACKET_LIMIT_BYTES + 1)).decode()
    small = base64.b64encode(b"y" * 100).decode()
    prepared = {
        "routeInitTxs": [{"base64": small}],
        "keeperFundingTx": big,
    }
    verdict = assess_multihopper_prepared_bundle(prepared)
    assert verdict.label == SizeLabel.TOO_BIG
    assert verdict.byte_length == SOLANA_TX_PACKET_LIMIT_BYTES + 1


def test_multihopper_empty_bundle_unknown():
    verdict = assess_multihopper_prepared_bundle({})
    assert verdict.label == SizeLabel.UNKNOWN
