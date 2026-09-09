import pytest


pytest.importorskip("lh2poolx")

from lh2poolx import LH2Release, evaluate_pool_source
from degadisx.lh2pool import source_table_from_lh2pool


def test_adapter_builds_a_terminated_ground_source_table():
    terms = [
        evaluate_pool_source(LH2Release(0.1055, 1.0), elapsed_s=30.0),
        evaluate_pool_source(LH2Release(0.1055, 1.0), elapsed_s=60.0),
    ]
    table = source_table_from_lh2pool(terms, duration_s=120.0)
    assert table.tend == pytest.approx(120.0)
    assert table.rate[-2] == table.rate[-1] == 0.0
    assert table.radius_at(30.0) == pytest.approx(terms[0].radius_m)


def test_adapter_refuses_confined_terms():
    term = evaluate_pool_source(LH2Release(9.5, 0.1, max_radius_m=0.5),
                                elapsed_s=30.0)
    with pytest.raises(ValueError, match="inventory"):
        source_table_from_lh2pool([term], duration_s=60.0)
