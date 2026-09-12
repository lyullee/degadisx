import pytest

import degadisx
from degadisx.core.atmosphere import ambient_density, wind_log
from degadisx.run import _require_legacy


def test_public_version_and_legacy_route():
    assert degadisx.__version__ == "0.1.3"
    _require_legacy(None)
    _require_legacy("legacy")
    with pytest.raises(ValueError, match="legacy"):
        _require_legacy("nonlegacy")


def test_atmospheric_primitives_are_finite():
    assert ambient_density(288.15, 101325.0, 0.0) > 1.0
    assert wind_log(10.0, 0.1, 0.2, 0.0) > 0.0
