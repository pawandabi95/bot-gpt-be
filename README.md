# BOT GPT – DRF Conversational Backend

BOT GPT is a backend platform for building **multi-turn conversational AI systems** with support for:
- Open chat
- Retrieval-Augmented Generation (RAG) over documents

The system treats the **LLM as stateless** while the backend manages **memory, context, retrieval, and orchestration**.

---

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
```

Activate:
- **Windows (CMD)**
```cmd
venv\Scripts\activate
```

- **Linux / Mac**
```bash
source venv/bin/activate
```

---

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 3. Set Environment Variables

Create a `.env` file (do NOT commit it):

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

---

### 4. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```

Server runs at:
```
http://127.0.0.1:8000
```

---

## API Endpoints

### Conversations
- POST `/api/conversations/`
- POST `/api/conversations/{conversation_id}/continue/`
- GET  `/api/conversations/`
- GET  `/api/conversations/{conversation_id}/`
- DELETE `/api/conversations/{conversation_id}/`

### Documents (RAG)
- POST `/api/documents/`

---

## Architecture & Design

- [Design Document](docs/BOT_GPT_Design.pdf)
- [Architecture Diagram](docs/BOT_GPT_Architecture.pdf)
- [Design](docs/DESIGN.md)

---

## Tech Stack & Rationale

### Backend
- **Python 3.11**
- **Django Rest Framework (DRF)**

### Database
- **SQLite (local) / PostgreSQL (production-ready)**

### LLM Integration
- **Groq API (LLaMA 3.1 – 8B Instant)**

### Retrieval (RAG)
- Chunk-based document retrieval with upgrade path to embeddings

### DevOps & Tooling
- Docker & Docker Compose
- GitHub Actions (CI)
- Environment variables for secrets

---

## Storage & Database Design

The database is the **single source of truth**. The LLM remains stateless.

### Core Entities
- Conversation
- Message (ordered by sequence)
- Document
- DocumentChunk
- ConversationDocument

### Message Ordering & Replay
Messages use explicit sequence numbers to ensure deterministic replay.

### RAG Storage Strategy
Documents are chunked and only relevant chunks are injected into the LLM prompt.

---

## 🔍 RAG Functionality Verification

### 1. Upload Document
POST `/api/documents/`
```json
{
  "name": "Weather Info",
  "content": "Tomorrow will be sunny with 30 degrees."
}
```

### 2. Create RAG Conversation
POST `/api/conversations/`
```json
{
  "first_message": "Tell me about the weather",
  "mode": "rag"
}
```

### 3. Ask Grounded Question
POST `/api/conversations/{conversation_id}/continue/`
```json
{
  "message": "Will it be hot tomorrow?"
}
```

### Expected Result
The response is grounded in the uploaded document.

---

## Tests
```bash
python manage.py test
```

---

