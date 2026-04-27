"""
rag/embedder.py
---------------
Thin wrapper around the sentence-transformers library for generating dense vector
embeddings. Uses the all-MiniLM-L6-v2 model, which runs locally on CPU with no
API calls required. Invoked at index time by build_index.py and at query time by
retriever.py. On first run, downloads model weights from HuggingFace (~80 MB);
subsequent runs load from the local cache.
"""

from sentence_transformers import SentenceTransformer


class Embedder:

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Loads the sentence-transformers model into memory. Caches the model
        instance on the object so repeated embed() calls do not reload weights.

        Args:
            model_name: HuggingFace model identifier. Defaults to all-MiniLM-L6-v2,
                        which produces 384-dimensional embeddings and runs efficiently
                        on CPU for small corpora.
        """
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        """
        Encodes a single text string into a dense embedding vector.

        Args:
            text: Input string to embed (query or document passage).

        Returns:
            Embedding as a list of floats. Length is 384 for all-MiniLM-L6-v2.
        """
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Encodes a list of text strings into embedding vectors in a single forward
        pass. More efficient than calling embed() in a loop for large document sets
        because sentence-transformers batches the computation internally.

        Args:
            texts: List of input strings to embed.

        Returns:
            List of embeddings, one per input string, in the same order as input.
        """
        return self.model.encode(texts).tolist()
