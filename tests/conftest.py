"""Shared test fixtures and doubles.

Telemetry isolation: every test redirects the decision-telemetry sink to a
temporary file via ``AGENT_TELEMETRY_PATH`` so the suite never writes to the
repo's ``ops/`` directory.
"""

import pytest


class TierResolutionStub:
    """Gives a tier-client double the resolution half of the client contract.

    Since ADR-011 the controller asks the tier client to collapse a requested
    tier onto the topology that is actually configured before consulting the
    circuit breaker. A double has no topology, so it resolves every tier to
    itself — leaving existing call/tier assertions meaningful.

    Inherit this in every ``FakeTiers``; that keeps the four doubles in the
    suite from drifting away from the client contract one file at a time.
    """

    def resolve(self, tier: int) -> tuple[int, None]:
        """Identity resolution: the requested tier is the effective tier."""
        return tier, None


@pytest.fixture(autouse=True)
def _isolate_telemetry(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_TELEMETRY_PATH", str(tmp_path / "telemetry.jsonl"))


def tienda_agent():
    """A wired tienda agent — the composition ``core.load_agent("tienda")`` used to do.

    The core stopped resolving use-cases by name (platform-ADR-001), so the
    caller composes: load the config from the use-case's own directory, build
    its tools, hand both over. Tests are a caller. Mirrors the ``store_agent``
    fixture in ml-platform's ``projects/store-assistant/tests/conftest.py``.
    """
    from core import build_agent, load_usecase
    from usecases.tienda import USECASE_ROOT, build_registry

    config = load_usecase(USECASE_ROOT)
    return build_agent(config, build_registry(config))
