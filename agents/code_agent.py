"""
agents/code_agent.py
--------------------
Code Agent responsible for generating grounded Python code via the Claude API.
Receives the user query and retrieved passages from the Research Agent, constructs
a context-aware prompt that instructs Claude to ground its response in the provided
source material, and returns annotated code with source citations. Used in Modes 3
and 4.
"""

from models import CodeInput, CodeResult
import anthropic
from dotenv import load_dotenv

load_dotenv()


class CodeAgent:

    _SYSTEM = (
        "You are an expert Python programmer. "
        "You are given reference material and a user question. "
        "Write clean, correct Python code grounded in the provided material. "
        "Include inline comments only where the reasoning is non-obvious. "
        "Return code only — no markdown fences, no prose outside the code."
    )

    def __init__(self):
        """
        Initializes the Anthropic client using ANTHROPIC_API_KEY loaded from
        the .env file. Raises an error at construction time if the key is absent
        so failures surface early rather than at query time.
        """
        self.client = anthropic.Anthropic()

    def run(self, code_input: CodeInput) -> CodeResult:
        """
        Constructs a retrieval-grounded prompt from the query and passages,
        calls the Claude API, and parses the response into a CodeResult.

        Args:
            code_input: CodeInput containing the user query and retrieved Passage list.

        Returns:
            CodeResult with the generated code string, language tag ("python"),
            and a list of source filenames cited in the generation prompt.
        """
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=self._SYSTEM,
            messages=[{"role": "user", "content": self._build_prompt(code_input)}],
        )
        code = message.content[0].text.strip()
        sources = list({p.source for p in code_input.passages})
        return CodeResult(code=code, language="python", sources=sources)

    def _build_prompt(self, code_input: CodeInput) -> str:
        """
        Formats the retrieved passages and user query into a structured system
        prompt for the Claude API. Instructs the model to ground its response in
        the provided context, produce clean Python code, and include inline
        comments explaining non-obvious decisions.

        Args:
            code_input: CodeInput containing the query and retrieved passages.

        Returns:
            Formatted prompt string ready for the Claude API messages payload.
        """
        context = "\n\n".join(
            f"[{p.source}]\n{p.content}" for p in code_input.passages
        )
        return f"Reference material:\n{context}\n\nQuestion: {code_input.query}"
