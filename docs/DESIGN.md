# BOT GPT – Backend Design & Architecture

This document provides a **detailed design and solution overview** for the BOT GPT conversational backend, as requested in **Section-3 (Deliverables)** of the case study.

The system is designed to support **multi-turn conversations**, **document-grounded RAG workflows**, and **scalable LLM integration**, while keeping the LLM stateless and the backend fully in control of memory and orchestration.

---

## 1. Design Principles

1. **Stateless LLM**
   - The LLM does not retain memory between calls.
   - All context is reconstructed on every request.

2. **Database as Source of Truth**
   - Conversation history, messages, and documents are fully persisted.
   - Enables conversation replay, debugging, and recovery.

3. **Separation of Concerns**
   - API Layer: HTTP request/response handling
   - Service Layer: business logic, RAG, summarization, LLM orchestration
   - Persistence Layer: database storage
   - LLM: reasoning only

4. **Cost-Aware Context Management**
   - Token usage is monitored.
   - Older messages are summarized to avoid context overflow.

---

## 2. High-Level Architecture

```
Client (Postman / UI)
        |
        v
API Layer (Django Rest Framework)
        |
        v
Service Layer
- Context building
- RAG retrieval
- Summarization
- LLM invocation
        |
        v
Database (Conversations, Messages, Documents)
        |
        v
External LLM (Groq – LLaMA)
```

This architecture ensures scalability, clarity, and LLM-provider independence.

---

## 3. Tech Stack & Rationale

### Backend
- **Python 3.11**
  - Mature ecosystem
  - Strong support for AI integrations

- **Django Rest Framework**
  - Rapid REST API development
  - Clear request/response lifecycle
  - Built-in serialization and validation
  - ORM for relational data modeling

### Database
- **SQLite** for local development
- **PostgreSQL-ready schema** for production
- Relational model fits conversation history and document relationships

### LLM Integration
- **Groq API – LLaMA 3.1 (8B Instant)**
  - Free-tier friendly
  - Very low latency
  - Suitable for chat, RAG, and summarization
  - Model configurable via environment variables

### DevOps
- Docker & Docker Compose
- GitHub Actions CI
- Environment variable–based secret management

---

## 4. Data & Storage Design

### 4.1 Core Entities

#### Conversation
Represents a single chat session.

Fields:
- `id` (UUID)
- `mode` (`open` or `rag`)
- `created_at`

Acts as the **root entity** for all messages.

---

#### Message
Stores each turn in a conversation.

Fields:
- `conversation_id` (FK)
- `role` (`user`, `assistant`, `system`)
- `content`
- `sequence`

**Why use sequence instead of timestamps?**
- Guarantees deterministic ordering
- Prevents race-condition ordering issues
- Ensures correct LLM context reconstruction

---

#### Document
Stores uploaded knowledge sources.

Fields:
- `id`
- `name`
- `content`
- `created_at`

Raw document content is never sent directly to the LLM.

---

#### DocumentChunk
Stores chunked portions of documents.

Fields:
- `document_id`
- `chunk_text`
- `chunk_index`
- `embedding` (optional)

Chunking improves retrieval accuracy and controls token usage.

---

#### ConversationDocument
Join table linking conversations to documents.

Purpose:
- Per-conversation document grounding
- Supports multiple documents per conversation
- Enables future access control

---

## 5. Conversation Flow

### Open Chat Mode

```
User Message
 → Persist user message
 → Build context from DB
 → Call LLM
 → Persist assistant message
 → Return response
```

All conversation memory is stored in the database.

---

## 6. RAG (Retrieval-Augmented Generation) Flow

### RAG Design

```
User Question
 → Identify linked documents
 → Retrieve relevant chunks
 → Inject chunks as SYSTEM context
 → Append conversation history
 → Call LLM
 → Return grounded response
```

### Prompt Structure

```
SYSTEM:
Use the following context:
<chunk 1>
<chunk 2>

USER:
<Question>
```

### Retrieval Strategy
- Current: keyword-based chunk matching (simulated)
- Designed for easy upgrade to embedding/vector DB search

---

## 7. Context & Cost Management

### Problem
- LLMs have strict context limits
- Token usage directly impacts cost

### Solution: Summarization

```
If token count exceeds threshold:
 → Summarize older messages
 → Delete old messages
 → Insert system summary message
```

This allows long-running conversations while controlling cost.

---

## 8. Error Handling & Reliability

Handled failure points:
- Missing API key → startup failure
- LLM timeout → graceful error response
- Token overflow → summarization fallback

Logging is added around:
- Prompt construction
- RAG retrieval
- LLM responses

---

## 9. Scalability Considerations

| Layer | Strategy |
|-----|----------|
| API | Stateless → horizontal scaling |
| Database | Indexing, PostgreSQL |
| RAG | Vector DB (FAISS / Pinecone) |
| LLM | Model switching, caching |

---

## 10. Why This Design Works

- Backend owns memory and orchestration
- Conversations are fully auditable
- RAG is explicit and controlled
- LLM provider can be swapped easily
- Suitable for real-world production constraints

---

## 11. Future Improvements

- Replace keyword search with embeddings
- Async document processing
- User authentication and permissions
- Streaming LLM responses
- Response caching

---

## 12. Conclusion

BOT GPT demonstrates a **clean, scalable, and production-oriented backend design** for conversational AI systems, focusing on engineering clarity, reliability, and real-world constraints rather than model experimentation.

## NOTE
User management is intentionally kept out of scope for this assignment. 
The architecture supports adding a User entity and associating conversations 
with users without changes to core flows.
