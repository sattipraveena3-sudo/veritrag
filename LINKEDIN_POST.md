# LinkedIn launch post

I’ve open-sourced **VeriRAG**, an evidence-first reliability gateway for RAG and LLM applications.

Instead of checking only whether an answer “looks right,” VeriRAG decomposes generated answers into claims, retrieves trusted evidence with hybrid BM25 + vector search, scores each claim for support, stores provenance, and produces a machine-readable risk decision that can fail a CI pipeline.

Built with Python, FastAPI, typed modular architecture, SQLite, Docker, pytest and GitHub Actions. The default backend is lightweight and deterministic for CI, with an optional sentence-transformer backend for stronger semantic retrieval.

I’d especially value feedback from people building RAG evaluation, AI observability, information retrieval or trustworthy AI systems. Contributions and benchmark ideas are welcome.

#AI #LLM #RAG #MLOps #OpenSource #AISafety #Python #DeveloperTools
