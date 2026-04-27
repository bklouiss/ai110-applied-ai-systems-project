"""
agents/explainer_agent.py
--------------------------
Explainer Agent responsible for producing plain-language breakdowns of
AI-generated code. Receives the user query, generated code, and original
retrieved passages, then prompts Claude to explain each design decision in
terms a junior developer can understand, keyed to specific lines and sourced
back to the knowledge base. Used in Mode 4 only.
"""

from models import ExplainerInput, ExplainerResult
import anthropic
from dotenv import load_dotenv

load_dotenv()


class ExplainerAgent:

    _SYSTEM = (
        "You are a patient programming teacher explaining code to a junior developer. "
        "For each significant decision in the code, explain WHY it was made — not just what it does. "
        "Reference specific line numbers or constructs. "
        "Cite which source document informed each key choice. "
        "Write in plain language. Use numbered steps."
    )

    def __init__(self):
        """
        Initializes the Anthropic client using ANTHROPIC_API_KEY loaded from
        the .env file. Raises an error at construction time if the key is absent
        so failures surface early rather than at query time.
        """
        self.client = anthropic.Anthropic()

    def run(self, explainer_input: ExplainerInput) -> ExplainerResult:
        """
        Constructs a prompt from the query, code, and source passages, calls
        the Claude API, and returns a plain-language explanation of the code.

        Args:
            explainer_input: ExplainerInput containing the query, generated code
                             string, and list of retrieved Passage objects.

        Returns:
            ExplainerResult with a step-by-step plain-language explanation and
            a list of source filenames referenced in the breakdown.
        """
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=self._SYSTEM,
            messages=[{"role": "user", "content": self._build_prompt(explainer_input)}],
        )
        explanation = message.content[0].text.strip()
        sources = list({p.source for p in explainer_input.passages})
        return ExplainerResult(explanation=explanation, sources=sources)

    def _build_prompt(self, explainer_input: ExplainerInput) -> str:
        """
        Formats the generated code and retrieved passages into a structured prompt
        that instructs Claude to explain each decision in plain language, reference
        specific line numbers or constructs, and cite which source document informed
        each choice. Designed to surface the reasoning behind the code, not just
        describe what it does.

        Args:
            explainer_input: ExplainerInput containing the query, code, and passages.

        Returns:
            Formatted prompt string ready for the Claude API messages payload.
        """
        context = "\n\n".join(
            f"[{p.source}]\n{p.content}" for p in explainer_input.passages
        )
        return (
            f"Original question: {explainer_input.query}\n\n"
            f"Source material:\n{context}\n\n"
            f"Code to explain:\n{explainer_input.code}"
        )
