"""Store ("tienda") use-case package.

Exposes what the use-case owns — its directory and its tools — and nothing
else. Wiring is the caller's: ``build_agent(load_usecase(USECASE_ROOT),
build_registry(config))``. The core does not resolve use-cases by name; a
library that knows where its callers live is not business-agnostic
(platform-ADR-001).
"""

from pathlib import Path

from .tools import build_registry

USECASE_ROOT = Path(__file__).resolve().parent

__all__ = ["USECASE_ROOT", "build_registry"]
