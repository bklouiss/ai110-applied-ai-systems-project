"""
agents/article_agent.py
-----------------------
Article Agent responsible for generating GeeksforGeeks-style educational
articles. Receives the user query and retrieved passages from the Research
Agent, then prompts Claude to produce a structured markdown article covering
introduction, algorithm walkthrough, Python implementation, complexity
analysis, a worked example, and practical guidance. Used in Mode 2.
"""

from models import CodeInput, ArticleResult
import anthropic
from dotenv import load_dotenv

load_dotenv(".env.local")


class ArticleAgent:

    _SYSTEM = (
        "You are a technical writer for a computer science educational website "
        "similar to GeeksforGeeks. Write a comprehensive, well-structured "
        "educational article about the topic using the provided reference material.\n\n"
        "Structure your article with exactly these sections in order:\n"
        "## Introduction\n"
        "## How It Works\n"
        "## Python Implementation\n"
        "## Complexity Analysis\n"
        "## Worked Example\n"
        "## When to Use\n"
        "## Key Takeaways\n\n"
        "Guidelines:\n"
        "- Write clearly for a CS student or junior developer.\n"
        "- In 'Python Implementation', include a complete, runnable code block "
        "with inline comments on non-obvious lines.\n"
        "- In 'Complexity Analysis', use a markdown table with Time and Space rows "
        "and a brief explanation of each.\n"
        "- In 'Worked Example', show concrete input, trace through the steps, "
        "and show the output.\n"
        "- In 'Key Takeaways', use 4–6 bullet points.\n"
        "- Ground all content in the provided reference material.\n"
        "- Do not add a top-level H1 title — start directly with ## Introduction."
    )

    def __init__(self):
        """
        Initializes the Anthropic client using ANTHROPIC_API_KEY from the
        .env file. Raises at construction time if the key is absent so
        failures surface early rather than at query time.
        """
        self.client = anthropic.Anthropic()

    def run(self, code_input: CodeInput) -> ArticleResult:
        """
        Generates a GeeksforGeeks-style educational article grounded in the
        retrieved passages. Uses a 4096-token budget to accommodate the full
        article structure including code blocks and tables.

        Args:
            code_input: CodeInput with the user query and retrieved Passage list.
                        Reuses CodeInput since the data shape is identical to
                        what the Code Agent receives.

        Returns:
            ArticleResult with the article title, full markdown content, and
            a deduplicated list of cited source filenames.
        """
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=self._SYSTEM,
            messages=[{"role": "user", "content": self._build_prompt(code_input)}],
        )
        content = message.content[0].text.strip()
        title = self._derive_title(code_input.query)
        sources = list({p.source for p in code_input.passages})
        return ArticleResult(
            query=code_input.query,
            title=title,
            content=content,
            sources=sources,
        )

    def _build_prompt(self, code_input: CodeInput) -> str:
        """
        Formats the retrieved passages and user query into a user message
        requesting a structured educational article.

        Args:
            code_input: CodeInput containing the query and retrieved passages.

        Returns:
            Formatted prompt string for the Claude API user message.
        """
        context = "\n\n".join(
            f"[{p.source}]\n{p.content}" for p in code_input.passages
        )
        return f"Reference material:\n{context}\n\nTopic: {code_input.query}"

    def _derive_title(self, query: str) -> str:
        """
        Derives a clean article title from the user query by title-casing it
        and stripping common question prefixes so the result reads as a topic
        heading rather than a question.

        Args:
            query: Raw user query string.

        Returns:
            Title-cased topic string suitable for an article heading.
        """
        prefixes = (
            "how do i ", "how to ", "what is ", "what are ",
            "explain ", "describe ", "implement ",
        )
        cleaned = query.strip().rstrip("?")
        lower = cleaned.lower()
        for prefix in prefixes:
            if lower.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break
        return cleaned.strip().title()
