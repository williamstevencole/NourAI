import os
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


def configure_ragas_with_openai():
    """Configure RAGAS to use OpenAI models for evaluation."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    openai_llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=api_key,
        temperature=0
    )

    openai_embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key
    )

    ragas_llm = LangchainLLMWrapper(openai_llm)
    ragas_embeddings = LangchainEmbeddingsWrapper(openai_embeddings)

    return ragas_llm, ragas_embeddings
