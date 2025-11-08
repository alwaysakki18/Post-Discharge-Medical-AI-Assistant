# Post Discharge Medical AI Assistant (POC)

A multi-agent AI system for post-discharge patient care management with RAG capabilities and nephrology expertise.

## 🎯 Overview

This POC demonstrates a chatbot system with multi-agent architecture that manages post-discharge patient reports, uses RAG with nephrology reference materials, and provides intelligent patient interaction through specialized AI agents.

## ✨ Features

- **Multi-Agent Architecture**: Receptionist Agent and Clinical AI Agent with clear workflows
- **RAG Implementation**: Semantic search over comprehensive clinical nephrology PDF (88.5 MB medical textbook)
- **Patient Data Management**: 27 diverse patient discharge reports
- **Web Search Integration**: Fallback for queries outside reference materials
- **Comprehensive Logging**: Complete system flow tracking
- **Modern Web Interface**: Streamlit frontend with FastAPI backend
- **PDF Knowledge Base**: Professional medical literature for accurate clinical information

## 🏗️ Architecture

### Components

1. **Receptionist Agent**
   - Patient identification and greeting
   - Database retrieval of discharge reports
   - Follow-up questions based on patient data
   - Routes medical queries to Clinical Agent

2. **Clinical AI Agent**
   - Handles medical questions and clinical advice
   - RAG over nephrology reference materials
   - Web search for external information
   - Provides citations and sources

3. **Patient Data Retrieval Tool**
   - Dedicated database interaction
   - Patient lookup by name
   - Structured discharge report data
   - Error handling

4. **Web Search Tool**
   - DuckDuckGo and Tavily integration
   - Fallback for specialized queries
   - Source attribution

5. **Logging System**
   - Comprehensive interaction logging
   - Agent handoff tracking
   - Decision process logging
   - Timestamped system flow

### Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Multi-Agent Framework**: LangGraph
- **LLM**: OpenAI GPT-4
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence-Transformers
- **Database**: SQLite
- **Web Search**: Tavily API, DuckDuckGo

## 📋 Prerequisites

- Python 3.9+
- OpenAI API Key
- Tavily API Key (optional, for enhanced web search)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd post-discharge-ai-assistant
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Initialize the system**
```bash
python scripts/setup_database.py
python scripts/setup_vector_db.py  # This will process the PDF (takes 10-15 minutes)
```

**Note**: The vector database setup will automatically use the comprehensive clinical nephrology PDF (`knowledge base for RAG/comprehensive-clinical-nephrology.pdf`) for superior medical accuracy. See `PDF_INTEGRATION_GUIDE.md` for details.

## 🎮 Usage

### Start the Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Start the Frontend

```bash
cd frontend
streamlit run app.py
```

Access the application at `http://localhost:8501`

## 📊 Sample Workflow

1. **Initial Interaction**
   - System greets patient
   - Patient provides name
   - Receptionist Agent retrieves discharge report
   - Agent asks follow-up questions

2. **Medical Query**
   - Patient asks medical question
   - Receptionist routes to Clinical Agent
   - Clinical Agent uses RAG for answer
   - Response includes citations

3. **Web Search Fallback**
   - Patient asks about recent research
   - Clinical Agent uses web search
   - Results clearly indicate external source

## 📁 Project Structure

```
post-discharge-ai-assistant/
├── backend/
│   ├── agents/
│   │   ├── receptionist_agent.py
│   │   ├── clinical_agent.py
│   │   └── agent_graph.py
│   ├── tools/
│   │   ├── patient_retrieval.py
│   │   ├── web_search.py
│   │   └── rag_tool.py
│   ├── database/
│   │   ├── models.py
│   │   └── database.py
│   ├── rag/
│   │   ├── vector_store.py
│   │   └── embeddings.py
│   ├── utils/
│   │   └── logger.py
│   ├── config.py
│   └── main.py
├── frontend/
│   └── app.py
├── data/
│   ├── patient_reports.json
│   └── nephrology_reference.txt
├── knowledge base for RAG/
│   └── comprehensive-clinical-nephrology.pdf
├── scripts/
│   ├── setup_database.py
│   └── setup_vector_db.py
├── logs/
├── tests/
├── docs/
│   ├── architecture_justification.md
│   └── demo_guide.md
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🔒 Medical Disclaimer

**This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice.**

## 📝 License

MIT License

## 👥 Contributors

DataSmith GenAI Intern Project

## 📞 Support

For issues and questions, please open an issue on GitHub.
