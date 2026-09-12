"""Shared source-state ledger and DEGADISx input adapter.

The ledger is a transport format, not an additional dispersion closure.  It
keeps the source stage explicit so a two-phase LH2 state is not silently
treated as a gas-only DEGADIS source.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from .io.inp import SourceTable


@dataclass(frozen=True)
class SourceState:
    time_s: float
    h2_rate_kg_s: float
    h2_mass_fraction: float
    temperature_K: float
    density_kg_m3: float
    area_m2: float
    velocity_m_s: float = 0.0
    liquid_fraction: float = 0.0
    height_m: float = 0.0
    bearing_deg: float = 0.0


@dataclass(frozen=True)
class SourceLedger:
    substance: str
    stage: str
    states: tuple[SourceState, ...]
    duration_s: float
    observation_operator: str = "not specified"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.substance.strip() or not self.stage.strip():
            raise ValueError("substance and stage must not be empty")
        if not self.states or self.duration_s <= 0.0:
            raise ValueError("states must be non-empty and duration_s must be > 0")
        times = [s.time_s for s in self.states]
        if any(t <= 0.0 for t in times) or any(b <= a for a, b in zip(times, times[1:])):
            raise ValueError("states must have strictly increasing positive time_s")
        for s in self.states:
            if s.time_s > self.duration_s or s.h2_rate_kg_s < 0.0:
                raise ValueError("state time/rate is outside the declared source window")
            if not 0.0 <= s.h2_mass_fraction <= 1.0:
                raise ValueError("h2_mass_fraction must be in [0, 1]")
            if not 0.0 <= s.liquid_fraction <= 1.0:
                raise ValueError("liquid_fraction must be in [0, 1]")
            if s.area_m2 <= 0.0 or s.density_kg_m3 <= 0.0:
                raise ValueError("area and density must be positive")

    def to_dict(self) -> dict[str, Any]:
        return {"substance": self.substance, "stage": self.stage,
                "duration_s": self.duration_s,
                "observation_operator": self.observation_operator,
                "metadata": dict(self.metadata),
                "states": [asdict(s) for s in self.states]}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourceLedger":
        return cls(str(data["substance"]), str(data["stage"]),
                   tuple(SourceState(**row) for row in data["states"]),
                   float(data["duration_s"]),
                   str(data.get("observation_operator", "not specified")),
                   dict(data.get("metadata", {})))

    def write_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def read_json(cls, path: str | Path) -> "SourceLedger":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def to_source_table(self) -> SourceTable:
        """Convert a resolved gas/pool handoff to DEGADIS source rows.

        ``h2_rate_kg_s`` is the contaminant (H2) rate.  DEGADIS ``ET`` is the
        total source rate, so the conversion is explicit and reversible.  A
        remaining liquid fraction is rejected because the ground-layer route
        needs an upstream evaporation/flash handoff.
        """
        if self.stage not in {"gas_handoff", "pool", "near_field_handoff"}:
            raise ValueError("ledger stage is not a DEGADIS ground-source handoff")
        if any(s.liquid_fraction > 1e-12 for s in self.states):
            raise ValueError("resolve liquid fraction before creating a gas source table")
        time = np.asarray([s.time_s for s in self.states], dtype=float)
        frac = np.asarray([s.h2_mass_fraction for s in self.states], dtype=float)
        if np.any(frac <= 0.0):
            raise ValueError("h2_mass_fraction must be > 0 for DEGADIS source rows")
        h2_rate = np.asarray([s.h2_rate_kg_s for s in self.states], dtype=float)
        total_rate = h2_rate / frac
        radius = np.asarray([math.sqrt(s.area_m2 / math.pi) for s in self.states])
        temp = np.asarray([s.temperature_K for s in self.states], dtype=float)
        active_time = time if time[-1] >= self.duration_s else np.append(time, self.duration_s)
        if len(active_time) > len(time):
            total_rate = np.append(total_rate, total_rate[-1])
            frac = np.append(frac, frac[-1])
            radius = np.append(radius, radius[-1])
            temp = np.append(temp, temp[-1])
        final = float(active_time[-1])
        return SourceTable(
            time=np.concatenate([active_time, [final + 1.0, final + 2.0]]),
            rate=np.concatenate([total_rate, [0.0, 0.0]]),
            radius=np.concatenate([radius, [radius[-1], radius[-1]]]),
            wc=np.concatenate([frac, [frac[-1], frac[-1]]]),
            temp=np.concatenate([temp, [temp[-1], temp[-1]]]),
            fracv=np.zeros(len(active_time) + 2),
            enthalpy=np.zeros(len(active_time) + 2),
            rho=np.zeros(len(active_time) + 2),
        )

    def to_directed_jet_initial_conditions(
        self, plume: Any, *, state_index: int = -1, wind_speed_m_s: float,
        theta0_rad: float = 0.0, mass_balance_tolerance: float = 0.02,
    ) -> np.ndarray:
        """Create one explicit initial state for the existing JETPLU driver.

        This is an input adapter, not a new JETPLU closure.  It passes a
        resolved, single-phase source plane to
        :meth:`degadisx.core.jetplume.JetPlume.initial_conditions_directed`,
        after checking the declared source-plane mass balance.  The caller
        then supplies the returned state directly to ``plume.run(y0, ...)``.

        The JETPLU equations remain two-dimensional in the wind--vertical
        plane.  A source bearing, horizontal yaw, or cross-axis wind must
        therefore be resolved upstream; this adapter must not be used to
        claim a three-dimensional fixed-receptor field.
        """
        if self.stage not in {"gas_handoff", "near_field_handoff"}:
            raise ValueError("ledger stage is not a directed gas-jet handoff")
        if wind_speed_m_s <= 0.0:
            raise ValueError("wind_speed_m_s must be positive")
        if not -math.pi / 2.0 <= theta0_rad <= math.pi / 2.0:
            raise ValueError("theta0_rad must be between vertically downward and upward")
        if not 0.0 <= mass_balance_tolerance < 1.0:
            raise ValueError("mass_balance_tolerance must be in [0, 1)")
        try:
            state = self.states[state_index]
        except IndexError as exc:
            raise ValueError("state_index is outside the source ledger") from exc
        if state.liquid_fraction > 1e-12:
            raise ValueError("resolve liquid fraction before creating a directed jet state")
        if state.h2_rate_kg_s <= 0.0 or state.h2_mass_fraction <= 0.0:
            raise ValueError("directed jet state requires positive H2 rate and mass fraction")
        if state.velocity_m_s <= 0.0:
            raise ValueError("directed jet state requires a declared positive velocity")
        total_rate = state.h2_rate_kg_s / state.h2_mass_fraction
        declared_rate = state.density_kg_m3 * state.area_m2 * state.velocity_m_s
        residual = abs(declared_rate - total_rate) / total_rate
        if residual > mass_balance_tolerance:
            raise ValueError(
                "directed jet source-plane mass residual "
                f"{residual:.3%} exceeds {mass_balance_tolerance:.3%}"
            )
        diameter = math.sqrt(4.0 * state.area_m2 / math.pi)
        return plume.initial_conditions_directed(
            erate=state.h2_rate_kg_s,
            diajet=diameter,
            elejet=state.height_m,
            ua=wind_speed_m_s,
            theta0=theta0_rad,
            rho_exit=state.density_kg_m3,
            concentration=state.h2_mass_fraction,
        )


__all__ = ["SourceState", "SourceLedger"]
