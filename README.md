# Agents-memory
a multi-tenant memory service for AI agents, built with Django REST Framework and PostgreSQL. Celery workers extract facts from conversations with an LLM, embed them with pgvector, resolve conflicts and keep version history. Hybrid search returns relevant memories within a token budget. Hashed, scoped API keys and tenant isolation.
