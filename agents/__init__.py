"""
agents/__init__.py
------------------
Package initializer for the agents module. Exposes the four agent classes at
the package level so callers can import directly from `agents` rather than
from individual submodules.
"""

from agents.orchestrator import Orchestrator
from agents.research_agent import ResearchAgent
from agents.code_agent import CodeAgent
from agents.explainer_agent import ExplainerAgent
from agents.article_agent import ArticleAgent

__all__ = ["Orchestrator", "ResearchAgent", "CodeAgent", "ExplainerAgent", "ArticleAgent"]
