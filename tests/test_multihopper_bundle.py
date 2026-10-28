import json
from pathlib import Path

from multihopper_explorer.tx_size import SizeLabel, assess_multihopper_prepared_bundle

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "multihopper"


def test_prepared_small_bundle_fits():
    prepared = json.loads((FIXTURES / "prepared_small.json").read_text(encoding="utf-8"))
    verdict = assess_multihopper_prepared_bundle(prepared)
    assert verdict.label == SizeLabel.FITS
