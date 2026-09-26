"""``core/`` is an export of ml-platform's ``libs/llm-core``, and is not edited here.

platform-ADR-010 makes ml-platform authoritative for the agent core and this
repository a one-way distribution of it. ``core/EXPORTED_FROM.json`` records the
source commit and a SHA-256 of every exported file; these tests recompute them.
A hand edit here would be silently overwritten by the next export — or, worse,
would survive it and make this copy disagree with the one the platform tests.
Either way the edit belongs in ml-platform, and this is where that becomes a red
build instead of a surprise.

The check needs nothing but this repository: no network, no checkout of
ml-platform. That is also its limit: the hashes it trusts live in the directory
it checks, so an edit that updates ``EXPORTED_FROM.json`` as well passes here
(QA-4 round twelve on ml-platform, P2-5). It catches the careless edit. The
guard that binds is CI's ``export-provenance`` job, which re-runs ml-platform's
exporter at the recorded commit and compares, taking the verdict from the source.
"""

import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest

CORE = Path(__file__).resolve().parent.parent / "core"
PROVENANCE = json.loads((CORE / "EXPORTED_FROM.json").read_text(encoding="utf-8"))


def _digest(path: Path) -> str:
    # Line endings are normalised because a Windows clone with core.autocrlf
    # checks the export out with CRLF — a change of bytes, not of content.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_every_exported_file_is_unchanged_since_the_export():
    drifted = [name for name, digest in PROVENANCE["files"].items() if _digest(CORE / name) != digest]
    assert not drifted, (
        f"core/ was edited after the export: {drifted}. core/ is generated from ml-platform's "
        "libs/llm-core (platform-ADR-010) — make the change there and re-export."
    )


def _strays(core: Path) -> list[str]:
    """Every entry under core/ the export did not produce, at any depth.

    Not only top-level ``*.py``: a ``core/policy/`` package beside the exported
    ``policy.py`` is imported instead of it, so the exported file stays
    byte-identical, correctly hashed, and never loaded (ml-platform QA-4 round
    thirteen, P2-1). A stub or a data file can change behaviour the same way.
    ``__pycache__`` is Python's own and is left alone.
    """
    expected = set(PROVENANCE["files"]) | {"EXPORTED_FROM.json"}
    found = []
    for path in sorted(core.rglob("*")):
        relative = path.relative_to(core)
        if "__pycache__" in relative.parts:
            continue
        if path.is_dir() or relative.as_posix() not in expected:
            found.append(relative.as_posix() + ("/" if path.is_dir() else ""))
    return found


def test_core_holds_nothing_the_export_did_not_produce():
    stray = _strays(CORE)
    assert not stray, f"core/ holds entries the export did not produce: {stray}"


@pytest.mark.parametrize(
    "entry",
    ["policy/__init__.py", "_private.py", "policy.pyi", "data/rules.json"],
    ids=["package", "underscore", "stub", "data"],
)
def test_the_stray_rule_sees_what_a_glob_of_py_files_missed(tmp_path, entry):
    """The shadowing package from round thirteen, and its siblings, against a copy of core/."""
    copy = tmp_path / "core"
    shutil.copytree(CORE, copy, ignore=shutil.ignore_patterns("__pycache__"))
    assert _strays(copy) == []
    target = copy / entry
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("SHADOWED = True\n", encoding="utf-8")
    assert _strays(copy), f"{entry} was not reported"


def test_the_version_is_the_distributions_own():
    """``__version__`` is agent-local's release, preserved by the export — not the library's."""
    init = (CORE / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__ = "([^"]+)"$', init, re.MULTILINE)
    assert match, "core/__init__.py has no __version__"
    assert match.group(1) == PROVENANCE["distribution_version"]


def test_the_provenance_is_a_clean_full_sha():
    """An export from uncommitted source cannot be reproduced, so it is not provenance.

    This checks the SHA's FORM only: forty hex digits, no ``-dirty`` suffix. It
    does not — cannot, without ml-platform reachable — check that the commit
    exists or is still reachable from ml-platform ``main``. A squash merge can
    orphan the commit this names while this test stays green; CI's
    ``export-provenance`` job refuses a commit that is not on ml-platform main.
    """
    commit = PROVENANCE["commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", commit), f"not a clean, full commit SHA: {commit!r}"
