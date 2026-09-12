import numpy as np

from degadisx.source_ledger import SourceLedger, SourceState


def test_ledger_maps_h2_rate_to_total_degadis_rate():
    ledger = SourceLedger(
        substance="hydrogen", stage="gas_handoff", duration_s=30.0,
        states=(SourceState(10.0, 0.2, 0.5, 300.0, 1.0, 1.0),),
    )
    table = ledger.to_source_table()
    assert np.isclose(table.rate[0], 0.4)
    assert np.isclose(table.time[0], 0.0)
    assert np.isclose(table.time[1], 10.0)
    assert np.isclose(table.rate[1], 0.4)
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


class _DirectedJetRecorder:
    def __init__(self):
        self.kwargs = None

    def initial_conditions_directed(self, **kwargs):
        self.kwargs = kwargs
        return np.arange(6, dtype=float)


def test_ledger_creates_mass_checked_directed_jet_state():
    # H2 mass rate / mass fraction = total rate = rho * area * velocity.
    ledger = SourceLedger(
        substance="hydrogen", stage="near_field_handoff", duration_s=30.0,
        states=(SourceState(10.0, 0.2, 0.5, 280.0, 2.0, 0.1,
                            velocity_m_s=2.0, height_m=0.5),),
    )
    plume = _DirectedJetRecorder()
    state = ledger.to_directed_jet_initial_conditions(
        plume, wind_speed_m_s=4.0,
    )
    assert np.array_equal(state, np.arange(6, dtype=float))
    assert plume.kwargs == {
        "erate": 0.2,
        "diajet": (4.0 * 0.1 / np.pi) ** 0.5,
        "elejet": 0.5,
        "ua": 4.0,
        "theta0": 0.0,
        "rho_exit": 2.0,
        "concentration": 0.5,
    }


def test_directed_jet_adapter_rejects_unresolved_or_unbalanced_source():
    plume = _DirectedJetRecorder()
    liquid = SourceLedger(
        substance="hydrogen", stage="gas_handoff", duration_s=30.0,
        states=(SourceState(10.0, 0.2, 0.5, 80.0, 2.0, 0.1,
                            velocity_m_s=2.0, liquid_fraction=0.1),),
    )
    try:
        liquid.to_directed_jet_initial_conditions(plume, wind_speed_m_s=4.0)
    except ValueError as exc:
        assert "liquid" in str(exc)
    else:
        raise AssertionError("unresolved liquid source was accepted")

    unbalanced = SourceLedger(
        substance="hydrogen", stage="gas_handoff", duration_s=30.0,
        states=(SourceState(10.0, 0.2, 0.5, 280.0, 2.0, 0.1,
                            velocity_m_s=1.0),),
    )
    try:
        unbalanced.to_directed_jet_initial_conditions(plume, wind_speed_m_s=4.0)
    except ValueError as exc:
        assert "residual" in str(exc)
    else:
        raise AssertionError("unbalanced source was accepted")
