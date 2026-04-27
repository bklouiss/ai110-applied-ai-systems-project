# AlgoAssist — Architecture Diagram

```mermaid
flowchart TD
    A["User Query\nquery: str · mode: int"] --> B["Entry Point\napp.py &nbsp;·&nbsp; main.py"]
    B --> C{Mode Router}

    C -->|Mode 1 · Naive LLM| D["Claude API\nno retrieval"]
    C -->|Mode 2 · RAG + Article| E["Research Agent"]
    C -->|Mode 3 · RAG + Code| F["Research Agent"]
    C -->|Mode 4 · Full Agentic| G["Orchestrator"]

    D --> R1["NaiveResponse\nresponse: str"]

    E --> KB[("Knowledge Base\nChromaDB · sentence-transformers")]
    KB --> E
    E --> EA["Article Agent"]
    EA --> R2["ArticleResult\ntitle · content · sources"]

    F --> KB
    KB --> F
    F -->|"ResearchResult"| H["Code Agent"]
    H --> R3["CodeResult\ncode: str · sources: list[str]"]

    G --> I["Research Agent"]
    I --> KB
    KB --> I
    I -->|"ResearchResult"| J["Code Agent"]
    I -->|"passages"| K["Explainer Agent"]
    J -->|"CodeResult"| K
    K --> R4["AgenticResponse\npassages · code · explanation"]

    style KB fill:#f5f5f5,stroke:#aaa,stroke-dasharray:4
    style R1 fill:#e8f4e8,stroke:#6a6
    style R2 fill:#e8f4e8,stroke:#6a6
    style R3 fill:#e8f4e8,stroke:#6a6
    style R4 fill:#c8e6c8,stroke:#4a4,stroke-width:2px
```

## Mode Progression

| Mode | Agents Active | Output |
|------|--------------|--------|
| 0 — Standard IDE | *(conceptual baseline, not in app)* | — |
| 1 — Naive LLM | Claude API only | Raw LLM response |
| 2 — RAG + Article | Research Agent → Article Agent | GeeksforGeeks-style article with code, complexity, examples |
| 3 — RAG + Code | Research Agent → Code Agent | Grounded code + source citations |
| 4 — Full Agentic | Orchestrator → Research → Code → Explainer | Code + plain-language explanation |
