"""stonk-sage: multi-agent equity research committee.

Public facade. Downstream code should import from `stonk_sage` (not from
submodules) wherever possible so the package surface stays small and stable.
"""

from stonk_sage.contracts import (
    CIOMemo,
    CommitteeInput,
    CommitteeResult,
    DevilsAdvocateCritique,
    MarketSnapshot,
    RiskAssessment,
    Thesis,
)

__version__ = "0.0.1"

__all__ = [
    "CIOMemo",
    "CommitteeInput",
    "CommitteeResult",
    "DevilsAdvocateCritique",
    "MarketSnapshot",
    "RiskAssessment",
    "Thesis",
    "__version__",
]
