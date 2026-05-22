"""
RAG index over S&P 500 sector AML risk profiles.
Data source: SparkCompaniesBuilder.get_sector_summary() output.
Falls back to a bundled CSV if Spark is not available in the agent env.

Set USE_FAKE_EMBEDDINGS=true to run offline without an OPENAI_API_KEY.
"""
import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def _embeddings():
    """Return FakeEmbeddings when USE_FAKE_EMBEDDINGS=true, else OpenAIEmbeddings."""
    if os.getenv("USE_FAKE_EMBEDDINGS", "").lower() == "true":
        from langchain_core.embeddings.fake import FakeEmbeddings
        return FakeEmbeddings(size=1536)
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(model="text-embedding-3-small")


def build_sector_index(sector_rows: list[dict]) -> FAISS:
    """
    sector_rows: list of dicts with keys:
      sector, company_count, avg_employees, aml_risk_flag
    """
    docs = [
        Document(
            page_content=(
                f"Sector: {r['sector']}. "
                f"Companies: {r['company_count']}. "
                f"Avg employees: {r['avg_employees']:.0f}. "
                f"AML risk: {r['aml_risk_flag']}."
            ),
            metadata={"sector": r["sector"], "aml_risk_flag": r["aml_risk_flag"]},
        )
        for r in sector_rows
    ]
    return FAISS.from_documents(docs, _embeddings())
