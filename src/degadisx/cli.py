"""Command-line interface for the legacy DEGADIS 2.1 route."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from .run import Receptor, run_jet, run_jet_to_ground, run_steady, run_transient


def _profile_table(rows: np.ndarray, limit: int = 20) -> str:
    head = f"{'dist (m)':>10} {'mole frac':>11} {'kg/m3':>11} {'T (K)':>8} {'Sz (m)':>8} {'Sy (m)':>8}"
    step = max(1, len(rows) // limit)
    lines = [head, "-" * len(head)]
    for r in rows[::step]:
        lines.append(f"{r[0]:10.4g} {r[2]:11.4g} {r[3]:11.4g} {r[5]:8.1f} {r[7]:8.3g} {r[8]:8.3g}")
    return "\n".join(lines)


def _cmd_steady(args) -> int:
    profile, src = run_steady(args.deck, er1=args.er1, er2=args.er2)
    gas = src.case.gas
    print(f"Steady release: {gas.name}, {src.blanket.ess:.4g} kg/s [DEGADIS 2.1 legacy properties]")
    print(f"  wind-profile exponent alpha = {src.alpha:.5f}")
    print(f"  profile: {len(profile.rows)} points; transition at {profile.transition:.4g} m")
    for name, level in (("upper", gas.ulc), ("lower", gas.llc)):
        d = profile.distance_to(level)
        shown = "not reached" if np.isnan(d) else f"{d:.4g} m"
        print(f"  distance to the {name} level of concern ({level * 100:.4g} mol %): {shown}")
    print("\n" + _profile_table(profile.rows))
    return 0


def _cmd_transient(args) -> int:
    times = np.array(args.snapshot, dtype=float) if args.snapshot else None
    out = run_transient(args.deck, er1=args.er1, er2=args.er2, times=times)
    print(f"Transient release: {out.source.case.gas.name}, {len(out.field.observers)} observers, {len(out.snapshots)} snapshots")
    for snap in out.snapshots:
        print(f"t={snap.time:.4g} s; extent={snap.column('dist')[-1]:.4g} m; peak={snap.column('yc').max():.5g}")
    return 0


def _cmd_dose(args) -> int:
    out = run_transient(args.deck, er1=args.er1, er2=args.er2)
    for history in out.dose([Receptor(x=x) for x in args.at]):
        peak, time = history.peak
        print(f"x={history.receptor.x:.4g} m; peak={peak:.5g} at {time:.4g} s; dose={history.dose():.5g}")
    return 0


def _cmd_jet(args) -> int:
    if args.bridge is None:
        jet, deck = run_jet(args.deck)
        print(f"Jet release: {deck.erate:.4g} kg/s; touchdown={jet.touchdown}")
        return 0
    profile, jet, _src = run_jet_to_ground(args.deck, args.bridge, er1=args.er1, er2=args.er2)
    print(f"Jet release: touchdown at {jet.distance:.5g} m\n" + _profile_table(profile.rows))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="degadisx", description="DEGADISx — EPA DEGADIS 2.1 legacy reimplementation")
    sub = parser.add_subparsers(dest="command", required=True)
    def common(command, help_text):
        command.add_argument("deck", type=Path, help=help_text)
        command.add_argument("--er1", type=Path, help="source-model parameter file")
        command.add_argument("--er2", type=Path, help="downwind parameter file")
    steady = sub.add_parser("steady", help="steady ground-level release"); common(steady, "the .INP input deck"); steady.set_defaults(func=_cmd_steady)
    transient = sub.add_parser("transient", help="unsteady ground-level release"); common(transient, "the .INP input deck"); transient.add_argument("--snapshot", type=float, action="append"); transient.set_defaults(func=_cmd_transient)
    dose = sub.add_parser("dose", help="concentration history at fixed receptors"); common(dose, "the .INP input deck"); dose.add_argument("--at", type=float, action="append", required=True); dose.set_defaults(func=_cmd_dose)
    jet = sub.add_parser("jet", help="pressurised release"); common(jet, "the .INO jet deck"); jet.add_argument("--bridge", type=Path); jet.set_defaults(func=_cmd_jet)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, RuntimeError) as exc:
        print(f"degadisx: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
