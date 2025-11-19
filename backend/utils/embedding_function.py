from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

class EmbeddingFunction:
    def __init__(self, model: SentenceTransformer):
        self.model = model

    def _encode(self, text_or_texts):
        """Encode text(s) to embeddings."""
        return self.model.encode(text_or_texts, convert_to_numpy=True).tolist()

    def __call__(self, texts):
        """ChromaDB batch embedding."""
        return self._encode(texts)

    def embed_query(self, text):
        """LangChain single query embedding."""
        return self._encode(text)

    def embed_documents(self, texts):
        """LangChain batch document embedding."""
        return self._encode(texts)


_embedding_function = None

def get_embedding_function() -> EmbeddingFunction:
    """Get or create the cached embedding function."""
    global _embedding_function

    if _embedding_function is None:
        model = SentenceTransformer(EMBEDDING_MODEL)
        _embedding_function = EmbeddingFunction(model)

    return _embedding_function
