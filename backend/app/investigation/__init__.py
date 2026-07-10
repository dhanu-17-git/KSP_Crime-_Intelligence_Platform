"""Investigation engine package.

This package contains business-agnostic intelligence orchestration primitives.
Business modules will feed normalized inputs into these interfaces later.
"""

from app.investigation.engine import InvestigationEngine

__all__ = ["InvestigationEngine"]
