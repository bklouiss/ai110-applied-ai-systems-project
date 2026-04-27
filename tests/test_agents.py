"""
tests/test_agents.py
--------------------
Unit tests for the Research, Code, and Explainer agents. Dependencies on
external services (ChromaDB, Claude API) are mocked so tests run fast and
offline. Focuses on input/output contract correctness: that each agent returns
the right dataclass type, that fields are populated, and that prompt-building
methods include the expected content.
"""

import pytest
from unittest.mock import MagicMock, patch
from models import ResearchInput, CodeInput, ExplainerInput, Passage, ResearchResult, CodeResult, ExplainerResult
from agents.research_agent import ResearchAgent
from agents.code_agent import CodeAgent
from agents.explainer_agent import ExplainerAgent


SAMPLE_PASSAGES = [
    Passage(content="Binary search requires a sorted array.", source="binary_search.md", score=0.92),
    Passage(content="Time complexity is O(log n).", source="complexity_guide.md", score=0.87),
]


class TestResearchAgent:

    def test_run_returns_research_result(self):
        """
        Mocks the Retriever and verifies that ResearchAgent.run() returns a
        ResearchResult with the same query string that was passed in.
        """
        with patch("agents.research_agent.Retriever") as MockRetriever:
            MockRetriever.return_value.retrieve.return_value = SAMPLE_PASSAGES
            agent = ResearchAgent()
            result = agent.run(ResearchInput(query="binary search"))
            assert isinstance(result, ResearchResult)
            assert result.query == "binary search"

    def test_run_returns_passages(self):
        """
        Mocks the Retriever to return SAMPLE_PASSAGES and verifies that
        ResearchAgent.run() surfaces them in the ResearchResult.
        """
        with patch("agents.research_agent.Retriever") as MockRetriever:
            MockRetriever.return_value.retrieve.return_value = SAMPLE_PASSAGES
            agent = ResearchAgent()
            result = agent.run(ResearchInput(query="binary search"))
            assert result.passages == SAMPLE_PASSAGES


class TestCodeAgent:

    def test_run_returns_code_result(self):
        """
        Mocks the Anthropic client and verifies that CodeAgent.run() returns
        a CodeResult with a non-empty code string.
        """
        with patch("agents.code_agent.anthropic.Anthropic") as MockAnthropic:
            mock_msg = MagicMock()
            mock_msg.content[0].text = "def binary_search(arr, target): pass"
            MockAnthropic.return_value.messages.create.return_value = mock_msg
            agent = CodeAgent()
            result = agent.run(CodeInput(query="binary search", passages=SAMPLE_PASSAGES))
            assert isinstance(result, CodeResult)
            assert len(result.code) > 0

    def test_run_cites_sources(self):
        """
        Verifies that CodeResult.sources is populated with at least one source
        filename from the input passages.
        """
        with patch("agents.code_agent.anthropic.Anthropic") as MockAnthropic:
            mock_msg = MagicMock()
            mock_msg.content[0].text = "def binary_search(arr, target): pass"
            MockAnthropic.return_value.messages.create.return_value = mock_msg
            agent = CodeAgent()
            result = agent.run(CodeInput(query="binary search", passages=SAMPLE_PASSAGES))
            assert len(result.sources) > 0

    def test_build_prompt_includes_passages(self):
        """
        Calls _build_prompt() directly and verifies that the returned string
        contains passage content from the input, confirming the retrieval
        context is injected into the prompt.
        """
        with patch("agents.code_agent.anthropic.Anthropic"):
            agent = CodeAgent()
            prompt = agent._build_prompt(CodeInput(query="binary search", passages=SAMPLE_PASSAGES))
            assert "Binary search requires a sorted array." in prompt


class TestExplainerAgent:

    def test_run_returns_explainer_result(self):
        """
        Mocks the Anthropic client and verifies that ExplainerAgent.run()
        returns an ExplainerResult with a non-empty explanation string.
        """
        with patch("agents.explainer_agent.anthropic.Anthropic") as MockAnthropic:
            mock_msg = MagicMock()
            mock_msg.content[0].text = "This code implements binary search step by step."
            MockAnthropic.return_value.messages.create.return_value = mock_msg
            agent = ExplainerAgent()
            result = agent.run(ExplainerInput(
                query="binary search",
                code="def binary_search(arr, target): pass",
                passages=SAMPLE_PASSAGES,
            ))
            assert isinstance(result, ExplainerResult)
            assert len(result.explanation) > 0

    def test_build_prompt_includes_code(self):
        """
        Calls _build_prompt() directly and verifies that the generated code
        string appears in the prompt, confirming the agent explains the
        actual code rather than ignoring it.
        """
        with patch("agents.explainer_agent.anthropic.Anthropic"):
            agent = ExplainerAgent()
            code = "def binary_search(arr, target): pass"
            prompt = agent._build_prompt(ExplainerInput(
                query="binary search",
                code=code,
                passages=SAMPLE_PASSAGES,
            ))
            assert code in prompt
