"""
app.py
------
Streamlit UI entry point for AlgoAssist. Provides a mode selector sidebar
(Modes 1–4), a query input field, and a formatted multi-panel response display.
Each mode renders its output in a distinct layout: Mode 2 shows retrieved passages
only, Mode 3 adds the generated code block, and Mode 4 adds the plain-language
explanation panel. Dispatches queries to the appropriate agent pipeline based on
the selected mode.
"""

import streamlit as st
from models import (
    QueryRequest, NaiveResponse, ArticleResult, CodeResult, AgenticResponse,
    ResearchInput, CodeInput,
)
from agents.research_agent import ResearchAgent
from agents.article_agent import ArticleAgent
from agents.code_agent import CodeAgent
from agents.orchestrator import Orchestrator
import anthropic
from dotenv import load_dotenv

load_dotenv()

_MODE_LABELS = {
    1: "1 — Naive LLM",
    2: "2 — RAG + Article",
    3: "3 — RAG + Code",
    4: "4 — Full Agentic",
}

_MODE_DESCRIPTIONS = {
    1: "Direct Claude call with no retrieval. Baseline comparison against grounded modes.",
    2: "Retrieves relevant knowledge base passages and generates a full educational article with code examples, complexity analysis, and practical guidance — styled like GeeksforGeeks.",
    3: "Retrieves relevant context, generates grounded Python code with source citations.",
    4: "Full pipeline: retrieval → grounded code → plain-language explanation.",
}


def render_article(article_result: ArticleResult) -> None:
    """
    Renders an ArticleResult as a GeeksforGeeks-style educational page.
    Displays the derived topic title as a prominent heading, the full
    structured markdown article (Introduction through Key Takeaways), and
    a collapsible reference sources footer.

    Args:
        article_result: ArticleResult produced by the Article Agent.
    """
    st.markdown(f"# {article_result.title}")
    st.divider()
    st.markdown(article_result.content)
    st.divider()
    with st.expander("Reference Sources"):
        for s in article_result.sources:
            st.markdown(f"- `{s}`")


def render_passages(passages: list) -> None:
    """
    Renders a list of retrieved Passage objects as labeled expandable sections.
    Each expander shows the passage content, source filename, and cosine
    similarity score so users can see exactly what context the agents worked from.

    Args:
        passages: List of Passage objects from a ResearchResult.
    """
    st.subheader("Retrieved Passages")
    for i, p in enumerate(passages, 1):
        with st.expander(f"Passage {i} — `{p.source}` (score: {p.score:.3f})"):
            st.markdown(p.content)


def render_code(code_result: CodeResult) -> None:
    """
    Renders a CodeResult as a syntax-highlighted Python code block followed
    by an expandable 'Sources' section listing the filenames cited during
    code generation.

    Args:
        code_result: CodeResult produced by the Code Agent.
    """
    st.subheader("Generated Code")
    st.code(code_result.code, language=code_result.language)
    with st.expander("Sources"):
        for s in code_result.sources:
            st.markdown(f"- `{s}`")


def render_explanation(explainer_result) -> None:
    """
    Renders an ExplainerResult as a formatted markdown text section with
    cited source filenames listed at the bottom under a 'Sources' header.

    Args:
        explainer_result: ExplainerResult produced by the Explainer Agent.
    """
    st.subheader("Explanation")
    st.markdown(explainer_result.explanation)
    with st.expander("Sources"):
        for s in explainer_result.sources:
            st.markdown(f"- `{s}`")


def run_query(request: QueryRequest):
    """
    Dispatches a QueryRequest to the appropriate agent or pipeline based on
    the selected mode:
        Mode 1 — direct Claude API call, no retrieval
        Mode 2 — Research Agent only
        Mode 3 — Research Agent → Code Agent
        Mode 4 — Orchestrator (Research → Code → Explainer)

    Args:
        request: QueryRequest containing the user query and selected mode (1–4).

    Returns:
        Response object: NaiveResponse, ResearchResult, CodeResult, or
        AgenticResponse depending on the mode.
    """
    if request.mode == 1:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": request.query}],
        )
        return NaiveResponse(query=request.query, response=message.content[0].text)

    if request.mode == 2:
        research_result = ResearchAgent().run(ResearchInput(query=request.query))
        return ArticleAgent().run(CodeInput(
            query=request.query,
            passages=research_result.passages,
        ))

    if request.mode == 3:
        research_result = ResearchAgent().run(ResearchInput(query=request.query))
        return CodeAgent().run(CodeInput(
            query=request.query,
            passages=research_result.passages,
        ))

    # Mode 4
    return Orchestrator().run(request)


def main() -> None:
    """
    Defines the Streamlit page layout: sets the page title and icon, renders
    the mode selector in the sidebar with a description of each mode, provides
    a query input text area, and routes the submitted query to run_query().
    Passes the returned response to the appropriate render function based on mode.
    """
    st.set_page_config(page_title="AlgoAssist", page_icon="💡", layout="wide")
    st.title("AlgoAssist")
    st.caption("Agentic RAG coding assistant for algorithms, data structures, and design patterns.")

    with st.sidebar:
        st.header("Mode")
        mode = st.radio(
            "Select operating mode",
            options=[1, 2, 3, 4],
            format_func=lambda m: _MODE_LABELS[m],
            index=3,
        )
        st.markdown("---")
        st.markdown(_MODE_DESCRIPTIONS[mode])

    query = st.text_area(
        "Your question",
        placeholder="e.g. How do I implement binary search in Python?",
        height=100,
    )

    if st.button("Run", type="primary") and query.strip():
        request = QueryRequest(query=query.strip(), mode=mode)
        with st.spinner("Running..."):
            response = run_query(request)

        if isinstance(response, NaiveResponse):
            st.subheader("Response")
            st.markdown(response.response)

        elif isinstance(response, ArticleResult):
            render_article(response)

        elif isinstance(response, CodeResult):
            render_code(response)

        elif isinstance(response, AgenticResponse):
            col1, col2 = st.columns([1, 1])
            with col1:
                render_passages(response.passages)
                render_explanation(response.explanation)
            with col2:
                render_code(response.code)


if __name__ == "__main__":
    main()
