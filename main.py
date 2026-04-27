"""
main.py
-------
CLI entry point for AlgoAssist. Accepts a user query and operating mode via
command-line arguments (--query, --mode) or falls back to interactive prompts
if arguments are omitted. Dispatches to the same agent pipeline as app.py and
prints the formatted response to stdout. Useful for scripting, testing, and
running AlgoAssist without a browser.
"""

import argparse
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

load_dotenv(".env.local")


def parse_args() -> argparse.Namespace:
    """
    Defines and parses command-line arguments:
        --query  (str, optional): The user's question or coding request.
        --mode   (int, optional): Operating mode 1–4. Defaults to 4 if omitted.

    Returns:
        Parsed argparse.Namespace with query and mode attributes. Either may be
        None if not provided, in which case prompt_user() handles collection.
    """
    parser = argparse.ArgumentParser(
        description="AlgoAssist — Agentic RAG Coding Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Modes:\n"
            "  1  Naive LLM      Direct Claude call, no retrieval\n"
            "  2  Retrieval Only Returns relevant passages, no code\n"
            "  3  RAG + Code     Grounded code with source citations\n"
            "  4  Full Agentic   Code + plain-language explanation (default)\n"
        ),
    )
    parser.add_argument("--query", type=str, help="Your question or coding request")
    parser.add_argument("--mode", type=int, choices=[1, 2, 3, 4], help="Operating mode 1–4")
    return parser.parse_args()


def prompt_user() -> QueryRequest:
    """
    Interactively prompts the user for a query string and mode selection when
    arguments are not provided on the command line. Validates that mode is an
    integer between 1 and 4 and re-prompts on invalid input.

    Returns:
        QueryRequest populated from stdin input.
    """
    print("\nAlgoAssist — Agentic RAG Coding Assistant")
    print("Modes: 1=Naive LLM  2=Retrieval Only  3=RAG+Code  4=Full Agentic\n")
    query = input("Your question: ").strip()
    while True:
        raw = input("Mode [1-4] (default 4): ").strip() or "4"
        try:
            mode = int(raw)
            if 1 <= mode <= 4:
                break
        except ValueError:
            pass
        print("  Please enter a number between 1 and 4.")
    return QueryRequest(query=query, mode=mode)


def print_response(response) -> None:
    """
    Formats and prints a response object to stdout with section headers.
    Handles all four response types:
        NaiveResponse      — prints raw Claude output
        ResearchResult     — prints each passage with source and score
        CodeResult         — prints code block and cited sources
        AgenticResponse    — prints passages, code block, and explanation

    Args:
        response: Any response dataclass returned by the agent pipeline.
    """
    sep = "─" * 50

    if isinstance(response, NaiveResponse):
        print(f"\n── Response {sep}")
        print(response.response)

    elif isinstance(response, ArticleResult):
        print(f"\n── {response.title} {sep}")
        print(response.content)
        print(f"\nSources: {', '.join(response.sources)}")

    elif isinstance(response, CodeResult):
        print(f"\n── Generated Code {sep}")
        print(response.code)
        print(f"\nSources: {', '.join(response.sources)}")

    elif isinstance(response, AgenticResponse):
        print(f"\n── Retrieved Passages {sep}")
        for i, p in enumerate(response.passages, 1):
            print(f"\n[{i}] {p.source}  (score: {p.score:.3f})")
            print(p.content)
        print(f"\n── Generated Code {sep}")
        print(response.code.code)
        print(f"\nSources: {', '.join(response.code.sources)}")
        print(f"\n── Explanation {sep}")
        print(response.explanation.explanation)
        print(f"\nSources: {', '.join(response.explanation.sources)}")


def main() -> None:
    """
    Entry point: parses command-line arguments, falls back to interactive prompts
    if arguments are missing, builds a QueryRequest, dispatches to the correct
    agent pipeline, and prints the formatted result to stdout.
    """
    args = parse_args()

    if args.query:
        request = QueryRequest(query=args.query, mode=args.mode or 4)
    else:
        request = prompt_user()

    if request.mode == 1:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": request.query}],
        )
        response = NaiveResponse(query=request.query, response=message.content[0].text)

    elif request.mode == 2:
        research_result = ResearchAgent().run(ResearchInput(query=request.query))
        response = ArticleAgent().run(CodeInput(
            query=request.query,
            passages=research_result.passages,
        ))

    elif request.mode == 3:
        research_result = ResearchAgent().run(ResearchInput(query=request.query))
        response = CodeAgent().run(CodeInput(
            query=request.query,
            passages=research_result.passages,
        ))

    else:  # mode 4
        response = Orchestrator().run(request)

    print_response(response)


if __name__ == "__main__":
    main()
