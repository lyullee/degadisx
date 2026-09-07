"""Fail the public build if excluded source/data artefacts are introduced."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {".pdf", ".xls", ".xlsx", ".csv", ".dbf", ".exe", ".out"}
FORBIDDEN_PARTS = {"reference", "tmp", "tmp_probe"}


def test_public_tree_has_no_controlled_material():
    offenders = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or any(part in FORBIDDEN_PARTS for part in rel.parts):
            offenders.append(rel.as_posix())
    assert not offenders, "controlled or non-public files present: " + ", ".join(offenders)


if __name__ == "__main__":
    test_public_tree_has_no_controlled_material()
