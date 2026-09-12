import numpy as np

from degadisx.source_ledger import SourceLedger, SourceState


def test_ledger_maps_h2_rate_to_total_degadis_rate():
    ledger = SourceLedger(
        substance="hydrogen", stage="gas_handoff", duration_s=30.0,
        states=(SourceState(10.0, 0.2, 0.5, 300.0, 1.0, 1.0),),
    )
    table = ledger.to_source_table()
    assert np.isclose(table.rate[0], 0.4)
    assert np.isclose(table.wc[0], 0.5)
    assert np.isclose(table.radius[0], (1.0 / np.pi) ** 0.5)


def test_ledger_rejects_unresolved_liquid():
    ledger = SourceLedger(
        substance="hydrogen", stage="gas_handoff", duration_s=30.0,
        states=(SourceState(10.0, 0.2, 0.5, 80.0, 1.0, 1.0, liquid_fraction=0.1),),
    )
    try:
        ledger.to_source_table()
    except ValueError as exc:
        assert "liquid" in str(exc)
    else:
        raise AssertionError("unresolved liquid state was accepted")
