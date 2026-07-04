"""Dynamic analysis interface implementation.

This placeholder does not execute untrusted code. In production, run code inside
an isolated sandbox with resource limits, test cases, compiler hardening, and
sanitizers.
"""



from typing import List

from .interfaces import DynamicAnalyzer
from .models import DiagnosticRequest, EvidenceInstance


class NoOpDynamicAnalyzer(DynamicAnalyzer):
    """Safe default dynamic analyzer that emits no runtime evidence."""

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        return []
