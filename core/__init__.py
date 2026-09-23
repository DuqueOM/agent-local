# GENERATED from DuqueOM/ml-platform libs/llm-core by scripts/export_llm_core.py.
# Do not edit here: core/EXPORTED_FROM.json pins the source commit and every
# file's hash, and tests/test_core_is_exported.py fails on drift. Change
# ml-platform, then re-export (platform-ADR-010).
"""Agent core — a business-agnostic, multi-tier local LLM agent library.

Tier routing, a deterministic policy gate whose rules are versioned data, a
fail-closed tool capability contract, cross-tier verification, decision
telemetry and per-tier circuit breakers.

This package is exported from ``libs/llm-core`` in DuqueOM/ml-platform, which
is authoritative for it (platform-ADR-010). ``core/EXPORTED_FROM.json`` records
the source commit and a hash of every file; send changes to ml-platform.

Wiring is the caller's: load a use-case from its directory, build its tool
registry, and hand both over — ``build_agent(load_usecase(root), registry)``.
The library does not resolve use-cases by name, because a library that knows
where its callers live is not business-agnostic.
"""

from __future__ import annotations

from .agent import Agent
from .config import UsecaseConfig, load_usecase
from .tools import ToolRegistry

__version__ = "0.7.0"

__all__ = ["Agent", "ToolRegistry", "UsecaseConfig", "build_agent", "load_usecase"]


def build_agent(config: UsecaseConfig, registry: ToolRegistry) -> Agent:
    """Wire an agent from a loaded configuration and the caller's tools.

    Replaces the source repository's `load_agent(name)`, which resolved
    `usecases.<name>` through `importlib` and therefore required this library
    to know that projects exist and where. The inversion is small and the
    boundary it restores is not: a tool registry is domain content, and domain
    content belongs to the project.

    Args:
        config: From :func:`load_usecase`, given the use-case directory.
        registry: The project's tools, already registered.

    Returns:
        A ready :class:`Agent`.
    """
    return Agent(config, registry)
