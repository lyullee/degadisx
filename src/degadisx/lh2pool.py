"""Optional adapter from LH2PoolX source terms to a DEGADIS source table."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .io.inp import SourceTable


def source_table_from_lh2pool(terms: Sequence, *, duration_s: float) -> SourceTable:
    """Create a DEGADIS ground-source table from LH2PoolX time-window terms.

    ``terms`` must be sorted, unconfined LH2PoolX results.  The adapter accepts
    both a declared-release quasi-steady term and an
    ``observed_footprint_conditional_source`` term.  For the latter it
    preserves the separately declared circular-equivalent footprint and its
    calculated evaporation rate; it does not infer an impact footprint or
    solve a confined pool inventory.  The final two zero-rate rows reproduce
    the original DEGADIS source-table termination convention.
    """
    if not terms:
        raise ValueError("at least one LH2PoolX term is required")
    if duration_s <= 0.0:
        raise ValueError("duration_s must be > 0")
    times = np.asarray([term.elapsed_s for term in terms], dtype=float)
    if np.any(times <= 0.0) or np.any(np.diff(times) <= 0.0):
        raise ValueError("terms must have strictly increasing positive elapsed_s")
    if times[-1] > duration_s:
        raise ValueError("duration_s must be at least the final source time")
    permitted = {
        "quasi_steady_equilibrium",
        "observed_footprint_conditional_source",
    }
    for term in terms:
        if term.source_status not in permitted:
            raise ValueError("confined or non-equilibrium LH2PoolX terms need "
                             "an inventory model before DEGADIS")

    # DEGADIS expects the third-from-last row to be the final active source
    # time.  Preserve supplied windows, then append two zero-rate end rows.
    active_time = np.append(times, duration_s) if times[-1] < duration_s else times
    rate = np.asarray([term.evaporation_rate_kg_s for term in terms], dtype=float)
    radius = np.asarray([
        term.radius_m if hasattr(term, "radius_m")
        else term.equivalent_radius_m
        for term in terms
    ], dtype=float)
    temp = np.asarray([term.pool_temperature_K for term in terms], dtype=float)
    if len(active_time) > len(rate):
        rate = np.append(rate, rate[-1])
        radius = np.append(radius, radius[-1])
        temp = np.append(temp, temp[-1])
    final = active_time[-1]
    time = np.concatenate([active_time, [final + 1.0, final + 2.0]])
    return SourceTable(
        time=time,
        rate=np.concatenate([rate, [0.0, 0.0]]),
        radius=np.concatenate([radius, [radius[-1], radius[-1]]]),
        wc=np.ones(len(time)),
        temp=np.concatenate([temp, [temp[-1], temp[-1]]]),
        fracv=np.zeros(len(time)),
        enthalpy=np.zeros(len(time)),
        rho=np.zeros(len(time)),
    )
