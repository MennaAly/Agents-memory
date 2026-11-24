### Agent Memory

A multi-tenant memory service for AI agents. Agents send it conversations, and it stores the facts worth remembering about each user, keeps them correct as they change, and returns the relevant ones when the agent needs them.

Status: in progress. See Roadmap for what is built and what is next.

### Why I'm building it

This is a learning project. I'm building it to understand AI engineering concepts in depth by implementing them in a real backend, not just reading about them. It is modelled on Mem0, an open-source memory layer for AI agents, and rebuilds its core ideas from scratch. It is not affiliated with Mem0.

### What it does
Remembers. An agent posts a user's messages. A background worker uses an LLM to extract durable facts (preferences, people, places, plans) and stores them with embeddings.

Stays correct. New facts are compared with existing ones. The service decides whether to add, update, delete or ignore each one, and keeps a version history instead of overwriting.

Recalls. Hybrid search (keyword + vector) returns the most relevant memories for a user, ranked by relevance, recency and importance, and trimmed to fit the agent's token budget.

Forgets. Single memories or a whole end user can be deleted, including their history and embeddings.
Key design points

Multi-tenant by default. Organisations own projects, and every query is scoped to the caller's project. Another tenant's data returns 404, never 403.

Secure API keys. Keys are random, stored only as a hash, looked up by prefix, scoped, revocable, and shown once at creation.
Async ingestion. Writes return 202 Accepted with a job id and are processed by Celery workers, with retries and idempotency keys so a retried request never creates duplicates.

Safe under concurrency. Transactions, row locks and per-user ordering keep facts consistent when many workers run at once.
Measured. An eval dataset scores recall, updates, forgetting and extraction quality, and every LLM call is logged with tokens, cost and latency./

### Tech stack

| Area            | Tools                                  |
| --------------- | -------------------------------------- |
| API             | Python, Django, Django REST Framework  |
| Database        | PostgreSQL, pgvector, full-text search |
| Background jobs | Celery, Redis                          |
| AI              | LLM structured output, embeddings      |
| Testing and CI  | pytest, factory_boy, GitHub Actions    |
| Infrastructure  | Docker Compose; AWS planned            |

### Roadmap
[x] Data model: organisations, members, projects, API keys, end users

[x] API key generation, hashing, authentication and scope permissions

[x] Tenant scoping on every query

[ ] Organisations and projects endpoints, cursor pagination, Problem Details errors, OpenAPI docs

[ ] Test suite and CI

[ ] Async ingestion with Celery, idempotency and concurrency control

[ ] LLM fact extraction, provider fallback, cost tracking

[ ] Embeddings and filtered vector search

[ ] Conflict resolution, version history, deduplication, forgetting

[ ] Hybrid search and evals

[ ] AWS deployment, caching, rate limiting

[ ] MCP server and demo agent

[ ] React developer dashboard
