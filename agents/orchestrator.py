"""
agents/orchestrator.py
----------------------
Orchestrator Agent for Mode 4 (Full Agentic). Coordinates the Research, Code,
and Explainer agents in sequence, passing outputs from each stage as inputs to
the next. Owns the top-level agentic loop and assembles the final AgenticResponse
from all three agent outputs.
"""

from models import QueryRequest, ResearchInput, CodeInput, ExplainerInput, AgenticResponse
from agents.research_agent import ResearchAgent
from agents.code_agent import CodeAgent
from agents.explainer_agent import ExplainerAgent


class Orchestrator:

    def __init__(self):
        """
        Instantiates the three sub-agents (Research, Code, Explainer).
        Each agent is stateless across queries and can be reused without
        re-initialization.
        """
        self.research_agent = ResearchAgent()
        self.code_agent = CodeAgent()
        self.explainer_agent = ExplainerAgent()

    def run(self, request: QueryRequest) -> AgenticResponse:
        """
        Executes the full agentic pipeline for a given query in sequence:
            1. Research Agent embeds the query and retrieves relevant passages.
            2. Code Agent receives the query and passages, generates grounded code.
            3. Explainer Agent receives the query, code, and passages, produces
               a plain-language breakdown.

        Args:
            request: QueryRequest with mode=4 and the user's query string.

        Returns:
            AgenticResponse containing passages, CodeResult, and ExplainerResult.
        """
        research_result = self.research_agent.run(ResearchInput(query=request.query))

        code_result = self.code_agent.run(CodeInput(
            query=request.query,
            passages=research_result.passages,
        ))

        explainer_result = self.explainer_agent.run(ExplainerInput(
            query=request.query,
            code=code_result.code,
            passages=research_result.passages,
        ))

        return AgenticResponse(
            query=request.query,
            mode=request.mode,
            passages=research_result.passages,
            code=code_result,
            explanation=explainer_result,
        )
