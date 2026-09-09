"""DEGADISx: a Python reimplementation of EPA DEGADIS 2.1.

DEGADISx is deliberately a *legacy-model* package. It exposes the original
DEGADIS 2.1 modelling route and its documented numerical conventions; it does
not include the separate DEGALI liquid-hydrogen research extensions.
"""

__version__ = "0.1.1"

from .run import (
    Receptor,
    SourceResult,
    TransientOutput,
    run_jet,
    run_jet_to_ground,
    run_source,
    run_steady,
    run_transient,
)

__all__ = [
    "__version__",
    "Receptor", "SourceResult", "TransientOutput",
    "run_source", "run_steady", "run_transient", "run_jet",
    "run_jet_to_ground",
]
