"""Mock LLM client — a Claude stand-in for offline/deterministic runs.

Mimics the tiny slice of the official OpenAI client the pipeline uses
(`.responses.create(...).output_text`). Detection is fully rule-based, so a
canned JSON response is enough to exercise the whole pipeline without a network
call. Enable in the API with USE_MOCK_LLM=true.
"""


class _MockResp:
    def __init__(self, text):
        self.output_text = text


class _MockResponses:
    def create(self, model=None, instructions="", input="", **_):
        instr = instructions or ""
        # Merged path: schema hint carries BOTH sections, so answer both at once.
        if "semantic_notes" in instr and "why_wrong" in instr:
            return _MockResp('{"semantic_notes": [], "diagnosis": "[mock] see rule-based diagnosis", '
                             '"why_wrong": "[mock]", "consequence": "[mock]", '
                             '"next_repair_step": "[mock]", "repair_actions": []}')
        if "semantic_notes" in instr:
            return _MockResp('{"semantic_notes": []}')
        if "why_wrong" in instr:
            return _MockResp('{"diagnosis": "[mock] see rule-based diagnosis", '
                             '"why_wrong": "[mock]", "consequence": "[mock]", '
                             '"next_repair_step": "[mock]", "repair_actions": []}')
        # LLM-only path: a mock cannot actually diagnose, so it abstains.
        return _MockResp('{"has_bug": false, "bug_type": null, '
                         '"diagnosis": "[mock LLM] no diagnosis", "next_step": "[mock]"}')


class MockLLMClient:
    def __init__(self):
        self.responses = _MockResponses()
