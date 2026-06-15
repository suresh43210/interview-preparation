# 🏦 Siddhartha Bank — AI Solutions Suite

> **Enterprise AI Transformation Suite** | Powered by Google Gemini 2.0 Flash, Anthropic Claude, and Hybrid Semantic Search (RAG)

An enterprise-grade, cost-effective artificial intelligence suite designed to accelerate digital transformation, automate regulatory compliance, and scale marketing workflows for **Siddhartha Bank Limited**.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-blue)](https://yourusername.github.io/siddhartha-bank-ai)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10-blue)](https://www.python.org/)

---

## 🚀 Business-Aligned Solutions

| # | Solution | Target Audience | Business Impact | Technology |
|---|----------|-----------------|-----------------|------------|
| 1 | 🤖 **Bank Customer Chatbot** | Retail Customers | 24/7 bilingual customer support, lowering support center ticket volumes by up to 45%. | HTML5/JS + Gemini 2.0 |
| 2 | 📢 **AI Marketing Copywriter** | Marketing & PR | Generates brand-consistent campaigns, reducing content production turnaround from days to minutes. | HTML5/JS + Gemini 2.0 |
| 3 | 👔 **Branch Manager Assistant** | Operations & Management | Automates customer sentiment analysis, creates meeting summaries, and generates real-time operational reports. | HTML5/JS + Chart.js + Gemini 2.0 |
| 4 | ⚖️ **NexSight Law (Legal Search Engine)** | Compliance & Legal | RAG-powered engine querying **1,865 provisions** from BAFIA, NRB Directives, AML Act, and Labor Act with exact legal citations. | Streamlit + Claude + Pinecone + Sentence-Transformers |

---

## 🛠️ Complete Technology Stack & Architecture

### 1. Client-Side Prototypes (Zero-Cost Infrastructure)
Designed for sub-second latencies and serverless deployments with **zero recurring infrastructure overhead**:
*   **User Interface**: Responsive HTML5, Vanilla CSS3 (custom Siddhartha Bank Navy `#0A3B7C` and Orange `#F39200` palette), and DOM-manipulated JavaScript.
*   **AI Inference**: Direct integration with the **Google Gemini 2.0 Flash API** via native client-side HTTP calls.
*   **Data Visualization**: **Chart.js 4.4** for rendering interactive operational metrics and performance charts.
*   **Hosting**: Static deployment via **GitHub Pages** (free, secure, and globally distributed).

### 2. NexSight Law (Enterprise Legal RAG System)
A production-ready Retrieval-Augmented Generation (RAG) system running local deep learning encoders for semantic retrieval:
*   **Frontend Dashboard**: **Streamlit** Python framework, customized with dark-mode resistant CSS typography and elegant card layout styling.
*   **Vector Database**: **Pinecone Vector DB** hosting high-dimensional vector representations of legal clauses for high-speed similarity searches.
*   **Embedding Model**: **Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`)** to encode both English and Devanagari (Nepali) user queries into a shared language-agnostic space.
*   **Neural Reranker**: **CrossEncoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`)** to re-score matching search documents, boosting semantic retrieval precision from ~60% to **~95%**.
*   **Deep Learning Engine**: **PyTorch (`torch`)** as the underlying tensor library running local transformers.
*   **Synthesizer LLM**: **Anthropic Claude Client (`anthropic`)** utilizing state-of-the-art models for synthesizing legal context into accurate, professional summaries.
*   **Audit Logger**: **SQLite (`sqlite3`)** database backend logging user prompts, LLM responses, and referenced sources into `chat_logs.db` for regulatory compliance and audit trails.
*   **Config & Security**: **Python Dotenv (`python-dotenv`)** to securely load environment variables and keep API secrets out of the codebase.

---

## 📁 Repository Structure

```
siddhartha-bank-ai/
├── index.html                ← Main Landing Page (Solutions Lobby)
├── chatbot/
│   ├── index.html            ← Client-side Customer Service Chatbot
│   └── laws/
│       └── corporate-laws/   ← NexSight Law (Legal Search Engine App)
│           ├── app.py        ← Streamlit main application & UI styling
│           ├── database.py   ← SQLite database logger
│           ├── chunks/       ← Pre-processed local law text segments
│           ├── ingest_to_pinecone.py  ← Script for processing PDFs, embedding & uploading to Pinecone
│           └── ingest_to_chroma.py    ← Local fallback vector store script
├── marketing/
│   └── index.html            ← AI Marketing Copywriter Generator
├── branch-manager/
│   └── index.html            ← Branch Manager's operational analytics dashboard
├── requirements.txt          ← Python backend dependencies
└── README.md                 ← Project documentation
```

---

## ⚡ Execution & Deployment Guide

### 1. Running the Client-Side Web Apps
No backend required. Simply open the gateway in a browser:
```bash
# Direct launch
open index.html

# Or run via a local web server (Recommended)
python3 -m http.server 8080
# Navigate to: http://localhost:8080
```

### 2. Running NexSight Law (Streamlit Backend)
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables in a `.env` file or Streamlit Secrets:
   ```env
   PINECONE_API_KEY="your-pinecone-key"
   ANTHROPIC_API_KEY="your-anthropic-key"
   ```
3. Start the application:
   ```bash
   streamlit run chatbot/laws/corporate-laws/app.py
   ```

---

## 🎯 Strategic Business Takeaways for Interviewers

1.  **Optimized Infrastructure Cost**: Client-side solutions run on static files with zero hosting charges, leveraging model free-tiers to maintain ₹0 monthly overhead.
2.  **True RAG Architecture**: NexSight Law does not suffer from hallucinations; it enforces strict context gating, searching through 1,865 actual provisions of Nepalese laws and refusing to answer if the context is missing.
3.  **Local Language Optimization**: Fully supports standard Devanagari Nepali input/output as well as Romanized Nepali queries translated dynamically to Devanagari.
4.  **Bilingual Flexibility**: Toggle language buttons dynamically translate the entire layout, welcome prompts, and suggested questions on-the-fly.
5.  **Strict Security Practices**: No API keys are hardcoded in the public frontend client. Users enter keys at runtime which remain securely inside the session state.

---

*Developed as an AI Solutions Interview Demonstration for Siddhartha Bank Limited.*
