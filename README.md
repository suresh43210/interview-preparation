# 🏦 Siddhartha Bank — AI Solutions Demo

> **Interview Demo Project** | Powered by Google Gemini 2.0 Flash & Anthropic Claude AI

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-blue)](https://yourusername.github.io/siddhartha-bank-ai)

---

## 🚀 Three AI Solutions

| # | Project | Description |
|---|---------|-------------|
| 1 | 🤖 **Bank Customer Chatbot** | Nepali + English AI customer service, available 24/7 |
| 2 | 📢 **AI Marketing Tool** | Pomelli-inspired, brand-consistent content generator |
| 3 | 👔 **Branch Manager Assistant** | Dashboard featuring complaint analyzer and meeting notes generator |

---

## 🛠️ Technology Stack

- **AI Models:** Google Gemini 2.0 Flash (for fast frontend-only tasks) & Anthropic Claude (for advanced legal RAG reasoning)
- **Frontend:** HTML5 + CSS3 + Vanilla JavaScript (zero framework, zero infrastructure cost)
- **Charts:** Chart.js 4.4
- **Hosting:** GitHub Pages (free hosting for prototypes)
- **Total Infrastructure Cost:** Rs. 0

---

## ⚡ How to Run Locally

```bash
# Option 1: Direct file open
open index.html

# Option 2: Local server (recommended)
python3 -m http.server 8080
# Go to browser: http://localhost:8080
```

---

## 🔑 API Key Setup

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Generate a free API key
3. Enter the API key in the app's sidebar/header input field

> ⚠️ **Security:** Never hardcode your API keys in the code. Users supply their own keys at runtime in the app interface.

---

## 📁 Project Structure & Layout

This project is divided into three key business solutions:

```
siddhartha-bank-ai/
├── index.html                ← Main Landing Page (Lobby)
├── chatbot/
│   ├── index.html            ← Customer Service Chatbot
│   └── laws/
│       └── corporate-laws/   ← NexSight Law (Advanced Corporate Legal RAG)
│           ├── app.py        ← Application Interface (Streamlit)
│           ├── database.py   ← SQLite database logger (Logs interactions)
│           └── chunks/       ← 1,865 database sections (Embedded law fragments)
├── marketing/
│   └── index.html            ← AI Marketing Copywriter
└── branch-manager/
    └── index.html            ← Manager's AI Dashboard
```

### 🏢 1. Main Gateway
* **`index.html`**: The unified homepage of the prototype. Styled with Siddhartha Bank's Navy Blue & Orange theme, it allows users to navigate to any of the 3 AI applications in one click.

### 💻 2. Client-Side Prototypes (Frontend-Only Apps)
These applications run directly in the user's browser without requiring backend servers or database overhead:
* **`chatbot/index.html` (Customer Chatbot)**: A responsive chat screen where customers can ask about bank accounts, interest rates, and digital banking services in standard English or Nepali.
* **`marketing/index.html` (AI Marketing Writer)**: A creative tool that automatically writes Facebook posts, emails, and SMS alerts aligned with Siddhartha Bank's official brand guidelines.
* **`branch-manager/index.html` (Branch Manager Assistant)**: A management dashboard used to analyze customer complaints, summarize meeting minutes, and compile branch reports.

### ⚖️ 3. Advanced Legal Search Engine — **NexSight Law** (`chatbot/laws/corporate-laws/`)
The core enterprise AI system that parses bank directives and corporate laws to answer questions with exact citations:
* **`app.py`**: The Streamlit user interface that receives questions, queries the vector database, and generates structured legal summaries using Claude.
* **`database.py` & `chat_logs.db`**: A local SQLite database logging queries, citations, and responses for auditing and optimization.
* **Source Documents (`.pdf` files)**: Official regulatory acts including BAFIA, Nepal Rastra Bank Act, Banking Offence Act, Anti-Money Laundering Act, and Labor Act.
* **Ingestion Pipeline (`ingest_to_pinecone.py`)**: Script that parsed 1,865+ legal sections, generated embeddings, and uploaded them to Pinecone for sub-second vector search.

---

## 🎯 Interview Key Points

1. **Cost-effective:** Utilizes free tier models for zero-cost infrastructure and fast client-side prototyping.
2. **Scalable:** Built on a production-ready RAG search engine (Pinecone + Claude) that can scale to cover all banking directives.
3. **Nepali Language:** Native Devanagari translation and response generation optimized for local customers.
4. **No Vendor Lock-in:** Standard HTML/JS frontend deployable on any platform (GitHub Pages, S3, etc.).
5. **Google Pomelli Concept:** Marketing writer is trained on Siddhartha Bank's brand DNA for consistent copywriting.

---

*Built for Siddhartha Bank Limited AI Solutions Interview Demo*
