# C-Drishti

**AI-Assisted Integrated Enforcement Intelligence and Decision-Support Platform**

C-Drishti is an open-source research and demonstration prototype exploring how statistical analytics, machine learning, retrieval-augmented generation (RAG), local large language models, and human-in-the-loop workflows can support integrated public-sector enforcement and decision support.

The platform combines a hybrid procurement anomaly engine with an evidence-grounded legal and policy assistant.

> **Important:** C-Drishti is a research and demonstration system. Its analytics, anomaly scores, retrieved legal material, and generated responses must not be treated as evidence of wrongdoing, legal advice, or authority for consequential enforcement action.

---

## Overview

Public-sector enforcement often requires officers to work across fragmented departmental systems, operational records, legal documents, and large volumes of data.

C-Drishti demonstrates an integrated architecture in which:

- operational data can be screened for unusual patterns;
- statistical and machine-learning models can prioritise cases for review;
- legal and policy documents can be retrieved semantically;
- a local LLM can generate responses grounded in retrieved evidence;
- source metadata can be shown alongside generated answers;
- human officers remain responsible for consequential decisions.

---


## Screenshots

### Integrated Dashboard

The main C-Drishti interface provides an integrated view of enforcement intelligence, analytics, and decision-support capabilities.

![C-Drishti Integrated Dashboard](docs/screenshots/dashboard.png)

### Hybrid Anomaly Engine

The anomaly engine combines statistical 3-sigma detection with Isolation Forest to identify and prioritise unusual procurement patterns.

![C-Drishti Hybrid Anomaly Engine](docs/screenshots/anomaly-engine.png)

### AI-Assisted Legal Intelligence

The Legal Assistant uses retrieval-augmented generation to retrieve relevant legal evidence and generate evidence-grounded responses using a locally hosted LLM.

![C-Drishti Legal RAG Assistant](docs/screenshots/legal-assistant.png)

### FastAPI Backend

The backend exposes versioned REST APIs for system monitoring, anomaly analytics, legal retrieval, RAG generation, and health checks.

![C-Drishti FastAPI Swagger API](docs/screenshots/swagger-api.png)

---



## Core Capabilities

### 1. Hybrid Anomaly Detection

The procurement anomaly engine combines:

- 3-sigma statistical screening;
- Isolation Forest;
- multivariate feature analysis;
- hybrid risk classification;
- explainable anomaly reasons.

The engine analyses features including:

- procurement quantity;
- delivery orders issued;
- delivery orders lifted;
- transport orders issued;
- transport orders lifted;
- total lifted quantity;
- pending lifting quantity;
- pending lifting percentage;
- lifting ratios.

The system distinguishes between:

- statistical anomalies;
- machine-learning anomalies;
- hybrid anomalies.

An anomaly is treated only as a **decision-support signal**.

---

### 2. Legal and Policy RAG Assistant

The Legal Assistant uses a retrieval-augmented generation pipeline:

```text
User Question
      ↓
Sentence Transformer
      ↓
Query Embedding
      ↓
ChromaDB
      ↓
Relevant Legal Evidence
      ↓
Retrieval Quality Filter
      ↓
Grounded Prompt
      ↓
Ollama
      ↓
Llama 3.2
      ↓
Answer + Sources + Disclaimer

Technology Stack
Frontend
HTML
CSS
JavaScript
Fetch API
Backend
Python
FastAPI
Pydantic
Uvicorn
Machine Learning and Analytics
Pandas
NumPy
scikit-learn
Isolation Forest
statistical anomaly screening
Generative AI and Retrieval
Sentence Transformers
ChromaDB
Ollama
Llama 3.2
Retrieval-Augmented Generation
Document Processing
PyPDF
Engineering
Docker
Docker Compose
pytest
structured logging
centralized configuration
global exception handling

Repository Structure
C-Drishti-GitHub/
│
├── index.html
├── README.md
├── docker-compose.yml
├── .gitignore
│
├── analytics/
│
├── data/
│   ├── README.md
│   └── sample_procurement_data.xlsx
│
├── docs/
│   ├── architecture.md
│   └── screenshots/
│
└── backend/
    │
    ├── Dockerfile
    ├── .dockerignore
    ├── .env.example
    ├── requirements.txt
    ├── requirements-dev.txt
    │
    ├── app/
    │   ├── api/
    │   ├── core/
    │   ├── models/
    │   ├── rag/
    │   ├── services/
    │   └── main.py
    │
    ├── storage/
    │   └── chroma/
    │
    └── tests/

Local Setup
Prerequisites

Install:

Python 3.11+
Docker Desktop
Ollama
Git

Pull the local LLM:

ollama pull llama3.2:3b
1. Clone the repository
git clone <repository-url>
cd C-Drishti-GitHub
2. Create Python environment

Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install backend dependencies:

pip install -r backend\requirements.txt
3. Configure environment

Copy:

backend/.env.example

to:

backend/.env

Default development values are already provided in the example file.

4. Build the legal vector index

Start FastAPI:

cd backend
uvicorn app.main:app --reload --port 8000

Open:

http://127.0.0.1:8000/docs

Execute:

POST /api/v1/rag/index

This extracts the legal PDFs, creates embeddings, and stores the vectors in ChromaDB.

5. Start the frontend

From the repository root:

python -m http.server 8080

Open:

http://localhost:8080
Docker

Build:

docker compose build

Start:

docker compose up -d

Check:

docker compose ps

Backend API:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

Stop:

docker compose down

Ollama currently runs on the host machine and is accessed from the backend container through:

host.docker.internal


The original software components in this repository are released under the
MIT License. See [LICENSE](LICENSE).

Third-party legal documents, source materials, datasets, trademarks, and other
external content remain subject to their respective rights and source terms
and are not relicensed under the MIT License.