# Vector Databases & RAG Modeling

When building AI-first applications (2026 standard), integrating embedding stores and designing data models for Retrieval-Augmented Generation (RAG) is mandatory.

## Database Selection

| Need | Recommended DB | Reasoning |
|------|---------------|-----------|
| **Existing Relational DB** | `pgvector` | Standard extension for PostgreSQL. Easiest to join metadata with embeddings in a single query. |
| **High Scale / Native Vector DB** | Pinecone, Milvus, Qdrant | Optimized for billions of vectors, highly available, specialized indexes (HNSW, IVF). |
| **Edge / Serverless** | Turso (libSQL) / Cloudflare Vectorize | Extremely fast edge reads, natively integrated with modern serverless frameworks. |

## RAG Data Modeling Principles

1. **Store Metadata Alongside Embeddings:**
   Never just store the vector. Always store a reference to the source document, the chunk index, and relevant filtering metadata (e.g., `tenant_id`, `created_at`, `document_type`).
2. **Chunking Strategy Matters:**
   Design schemas to accommodate parent-child document structures (e.g., a `documents` table and a `document_chunks` table containing the vectors).
3. **Hybrid Search Preparedness:**
   When using pgvector, ensure you can also perform full-text search (FTS) on the raw text for hybrid search (BM25 + Dense Vectors) for better accuracy.

## Anti-Patterns
❌ Using a dedicated Vector DB when pgvector on an existing Postgres instance would suffice.
❌ Forgetting to index vectors (e.g., using `ivfflat` or `hnsw` in pgvector), leading to slow exact K-NN searches over large datasets.
❌ Storing massive text payloads in the vector index instead of pointing back to a relational table.
