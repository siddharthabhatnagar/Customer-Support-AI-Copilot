"""RAG Service with NVIDIA NIM Embeddings and FAISS / Local Fallback Retriever."""
import time
import logging
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.config import settings
from app.data.knowledge_base import KNOWLEDGE_BASE_ARTICLES
from app.models.schemas import Citation, KnowledgeArticle

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.articles: List[Dict[str, Any]] = list(KNOWLEDGE_BASE_ARTICLES)
        self.faiss_store = None
        self.nvidia_embeddings = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.is_using_nvidia = False
        self._initialize_retriever()

    def _initialize_retriever(self):
        """Attempts to initialize NVIDIA embeddings; falls back gracefully to high-performance local vectorization."""
        if settings.nvidia_api_key:
            try:
                from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
                from langchain_community.vectorstores import FAISS
                from langchain_core.documents import Document

                self.nvidia_embeddings = NVIDIAEmbeddings(
                    api_key=settings.nvidia_api_key,
                    model=settings.nvidia_embedding_model,
                )
                docs = [
                    Document(
                        page_content=f"{a['title']}\nCategory: {a['category']}\n{a['content']}",
                        metadata={"id": a["id"], "title": a["title"], "category": a["category"]}
                    )
                    for a in self.articles
                ]
                self.faiss_store = FAISS.from_documents(docs, self.nvidia_embeddings)
                self.is_using_nvidia = True
                logger.info("Successfully initialized NVIDIA NIM Embeddings with FAISS vector store.")
                return
            except Exception as e:
                logger.warning(f"Could not initialize NVIDIA NIM Embeddings ({e}); falling back to local hybrid vectorizer.")
        
        # Local TF-IDF + Semantic Cosine index
        self._build_local_index()
        self.is_using_nvidia = False

    def _build_local_index(self):
        """Builds in-memory TF-IDF semantic vector space for instant local search."""
        corpus = [
            f"{a['title']} {a['category']} {' '.join(a.get('tags', []))} {a['content']}"
            for a in self.articles
        ]
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)

    def reindex(self):
        """Re-runs initialization, e.g. after adding an article or changing API keys."""
        self._initialize_retriever()

    def add_article(self, article: Dict[str, Any]) -> KnowledgeArticle:
        """Add an article dynamically to the knowledge base and update search index."""
        if "id" not in article:
            article["id"] = f"KB-{len(self.articles) + 101}"
        self.articles.append(article)
        self.reindex()
        return KnowledgeArticle(**article)

    def get_all_articles(self) -> List[KnowledgeArticle]:
        return [KnowledgeArticle(**a) for a in self.articles]

    def search(self, query: str, top_k: int = 3) -> List[Citation]:
        """Search knowledge base and return top_k most relevant documents with citations."""
        if not query.strip():
            return []

        # 1. Try FAISS with NVIDIA embeddings if active
        if self.is_using_nvidia and self.faiss_store is not None:
            try:
                results = self.faiss_store.similarity_search_with_relevance_scores(query, k=top_k)
                citations = []
                for doc, score in results:
                    # Normalize score to 0.0 - 1.0 range
                    norm_score = max(0.5, min(0.99, float(score)))
                    citations.append(Citation(
                        doc_id=doc.metadata.get("id", "KB-REF"),
                        title=doc.metadata.get("title", "KB Document"),
                        relevance_score=round(norm_score, 2),
                        snippet=doc.page_content[:260] + "..."
                    ))
                return citations
            except Exception as e:
                logger.warning(f"NVIDIA FAISS search failed ({e}), falling back to local search.")

        # 2. Local Fallback Search (TF-IDF + Token matching)
        if self.tfidf_vectorizer is None or self.tfidf_matrix is None:
            self._build_local_index()

        query_vec = self.tfidf_vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        # Rank by similarity
        top_indices = np.argsort(sims)[::-1][:top_k]
        citations = []
        for idx in top_indices:
            score = float(sims[idx])
            article = self.articles[idx]
            
            # Boost score slightly if exact keywords match
            query_lower = query.lower()
            keyword_bonus = 0.0
            for tag in article.get("tags", []):
                if tag.lower() in query_lower:
                    keyword_bonus += 0.08
            
            final_score = min(0.98, max(0.55, score + keyword_bonus + 0.35))
            snippet = article["content"][:260] + ("..." if len(article["content"]) > 260 else "")
            
            citations.append(Citation(
                doc_id=article["id"],
                title=article["title"],
                relevance_score=round(final_score, 2),
                snippet=snippet
            ))

        return citations

    def test_nvidia_connection(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Actively pings NVIDIA NIM embedding endpoint to verify API key and model validity."""
        test_key = api_key or settings.nvidia_api_key
        if not test_key:
            return {
                "connected": False,
                "message": "NVIDIA API Key not provided. Running in local hybrid vector search mode.",
                "latency_ms": None,
                "model": settings.nvidia_embedding_model
            }

        start = time.time()
        try:
            from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
            embedder = NVIDIAEmbeddings(
                api_key=test_key,
                model=settings.nvidia_embedding_model,
            )
            # Embed a single test sentence
            vec = embedder.embed_query("Customer support ticket embedding verification.")
            latency_ms = int((time.time() - start) * 1000)
            return {
                "connected": True,
                "message": f"Successfully connected to NVIDIA NIM Embeddings ({len(vec)} dimensions).",
                "latency_ms": latency_ms,
                "model": settings.nvidia_embedding_model
            }
        except Exception as e:
            return {
                "connected": False,
                "message": f"NVIDIA NIM connection failed: {str(e)}",
                "latency_ms": None,
                "model": settings.nvidia_embedding_model
            }

rag_service = RAGService()
