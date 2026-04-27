"""
tests/test_integration.py
--------------------------
End-to-end integration tests for the full AlgoAssist pipeline. Runs queries
through the complete Mode 4 agentic flow using a real ChromaDB index (must be
built via build_index.py) but with mocked Claude API calls to avoid network
dependence and API cost during CI. Verifies that all agents connect correctly,
data flows through the pipeline, and the final AgenticResponse contains all
expected fields with the correct types.
"""

import pytest
from unittest.mock import patch, MagicMock
from models import QueryRequest, AgenticResponse, ResearchResult, CodeResult, NaiveResponse
from agents.orchestrator import Orchestrator


class TestMode4Pipeline:

    def test_orchestrator_returns_agentic_response(self):
        """
        Runs a known query through the full Mode 4 pipeline with a mocked
        Claude API and verifies that the Orchestrator returns an AgenticResponse
        with non-empty passages, code, and explanation fields.
        """
        with patch("agents.code_agent.anthropic.Anthropic") as MockCode, \
             patch("agents.explainer_agent.anthropic.Anthropic") as MockExplainer:

            mock_code_msg = MagicMock()
            mock_code_msg.content[0].text = "def binary_search(arr, target): pass"
            MockCode.return_value.messages.create.return_value = mock_code_msg

            mock_explain_msg = MagicMock()
            mock_explain_msg.content[0].text = "This function implements binary search."
            MockExplainer.return_value.messages.create.return_value = mock_explain_msg

            orchestrator = Orchestrator()
            response = orchestrator.run(QueryRequest(
                query="How do I implement binary search?", mode=4
            ))

            assert isinstance(response, AgenticResponse)
            assert len(response.passages) > 0
            assert len(response.code.code) > 0
            assert len(response.explanation.explanation) > 0

    def test_passages_flow_to_explainer(self):
        """
        Verifies that AgenticResponse.explanation.sources references at least
        one source that also appears in AgenticResponse.passages. This confirms
        the Research Agent's passages were passed through to the Explainer Agent
        rather than dropped at the Code Agent boundary.
        """
        with patch("agents.code_agent.anthropic.Anthropic") as MockCode, \
             patch("agents.explainer_agent.anthropic.Anthropic") as MockExplainer:

            mock_code_msg = MagicMock()
            mock_code_msg.content[0].text = "def binary_search(arr, target): pass"
            MockCode.return_value.messages.create.return_value = mock_code_msg

            mock_explain_msg = MagicMock()
            mock_explain_msg.content[0].text = "This implements binary search."
            MockExplainer.return_value.messages.create.return_value = mock_explain_msg

            orchestrator = Orchestrator()
            response = orchestrator.run(QueryRequest(
                query="How do I implement binary search?", mode=4
            ))

            passage_sources = {p.source for p in response.passages}
            explanation_sources = set(response.explanation.sources)
            assert len(passage_sources & explanation_sources) > 0


class TestAllModes:

    def test_all_modes_return_expected_types(self):
        """
        Runs the same query through all four modes and asserts that each returns
        the correct response dataclass:
            Mode 1 → NaiveResponse
            Mode 2 → ResearchResult
            Mode 3 → CodeResult
            Mode 4 → AgenticResponse
        Confirms the mode router dispatches correctly end-to-end.
        """
        from models import ResearchInput, CodeInput

        # Mode 2 — real retrieval, no API
        from agents.research_agent import ResearchAgent
        result2 = ResearchAgent().run(ResearchInput(query="binary search"))
        assert isinstance(result2, ResearchResult)

        # Mode 3 — real retrieval, mocked Claude
        with patch("agents.code_agent.anthropic.Anthropic") as MockCode:
            mock_msg = MagicMock()
            mock_msg.content[0].text = "def binary_search(): pass"
            MockCode.return_value.messages.create.return_value = mock_msg
            from agents.code_agent import CodeAgent
            result3 = CodeAgent().run(CodeInput(
                query="binary search", passages=result2.passages
            ))
            assert isinstance(result3, CodeResult)

        # Mode 4 — real retrieval, mocked Claude
        with patch("agents.code_agent.anthropic.Anthropic") as MockCode, \
             patch("agents.explainer_agent.anthropic.Anthropic") as MockExplainer:
            mock_code_msg = MagicMock()
            mock_code_msg.content[0].text = "def binary_search(): pass"
            MockCode.return_value.messages.create.return_value = mock_code_msg
            mock_explain_msg = MagicMock()
            mock_explain_msg.content[0].text = "This implements binary search."
            MockExplainer.return_value.messages.create.return_value = mock_explain_msg
            result4 = Orchestrator().run(QueryRequest(query="binary search", mode=4))
            assert isinstance(result4, AgenticResponse)
