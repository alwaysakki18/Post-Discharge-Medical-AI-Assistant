# Installation Guide

## Post Discharge Medical AI Assistant - Step-by-Step Setup

---

## System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: 3.9 or higher
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: 2GB free space
- **Internet**: Required for API calls and web search

---

## Step 1: Clone or Download the Repository

```bash
git clone <repository-url>
cd post-discharge-ai-assistant
```

Or download and extract the ZIP file.

---

## Step 2: Create Virtual Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (backend)
- Streamlit (frontend)
- LangChain and LangGraph (multi-agent framework)
- ChromaDB (vector database)
- Sentence-Transformers (embeddings)
- OpenAI API client
- And other dependencies

**Installation time:** 5-10 minutes depending on internet speed

---

## Step 4: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # macOS/Linux
   ```

2. **Edit `.env` file and add your API keys:**
   ```
   OPENAI_API_KEY=sk-your-openai-api-key-here
   TAVILY_API_KEY=tvly-your-tavily-api-key-here  # Optional
   ```

### Getting API Keys

**OpenAI API Key (Required):**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Copy and paste into `.env` file

**Tavily API Key (Optional but Recommended):**
1. Go to https://tavily.com/
2. Sign up for free account
3. Get your API key from dashboard
4. Copy and paste into `.env` file

*Note: If you don't have Tavily API key, the system will use DuckDuckGo as fallback.*

---

## Step 5: Initialize Database

Run the database setup script:

### Windows
```bash
python scripts\setup_database.py
```

### macOS/Linux
```bash
python scripts/setup_database.py
```

**Expected output:**
```
========================================
Post Discharge Medical AI Assistant - Database Setup
========================================

📊 Initializing database...
✅ Database initialized

👥 Loading patient data...
✅ Patient data loaded

📈 Database Statistics:
   - Total patients: 27

📋 Sample Patients:
   1. John Smith - Chronic Kidney Disease Stage 3
   2. Sarah Johnson - Acute Kidney Injury
   ...

========================================
✅ Database setup complete!
========================================
```

---

## Step 6: Initialize Vector Database

Run the vector database setup script:

### Windows
```bash
python scripts\setup_vector_db.py
```

### macOS/Linux
```bash
python scripts/setup_vector_db.py
```

**Expected output:**
```
========================================
Post Discharge Medical AI Assistant - Vector DB Setup
========================================

🔍 Initializing vector store...
✅ Vector store initialized

📚 Indexing nephrology reference materials...
✅ Reference materials indexed

📈 Vector Store Statistics:
   - Total documents: 150+
   - Collection: nephrology_docs
   - Status: initialized

🧪 Testing search functionality...
✅ Search test successful!

========================================
✅ Vector database setup complete!
========================================
```

**Note:** This step may take 2-3 minutes as it processes and indexes the nephrology reference materials.

---

## Step 7: Start the Backend Server

### Windows
```bash
start_backend.bat
```

Or manually:
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### macOS/Linux
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Keep this terminal window open!**

---

## Step 8: Start the Frontend

Open a **NEW terminal window** and activate the virtual environment again:

### Windows
```bash
venv\Scripts\activate
start_frontend.bat
```

Or manually:
```bash
cd frontend
streamlit run app.py
```

### macOS/Linux
```bash
source venv/bin/activate
cd frontend
streamlit run app.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

The frontend should automatically open in your default browser.

---

## Step 9: Verify Installation

1. **Check Frontend:**
   - Browser should open to `http://localhost:8501`
   - You should see "Post Discharge Medical AI Assistant" header
   - Sidebar should show "✅ API Connected"
   - Patient count should show 27

2. **Check Backend:**
   - Visit `http://localhost:8000/docs` in browser
   - You should see FastAPI Swagger documentation
   - Try the `/health` endpoint

3. **Test Basic Functionality:**
   - In the frontend, type "Hello"
   - You should get a greeting from the Receptionist Agent
   - Type "My name is John Smith"
   - You should see the patient's discharge report

---

## Quick Setup (Windows)

For Windows users, we provide an automated setup script:

```bash
setup.bat
```

This will:
1. Create virtual environment
2. Install all dependencies
3. Initialize database
4. Initialize vector database

After running `setup.bat`, just:
1. Edit `.env` file with your API keys
2. Run `start_backend.bat`
3. Run `start_frontend.bat`

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

### Issue: "OpenAI API key not found"

**Solution:**
- Check that `.env` file exists in the root directory
- Verify `OPENAI_API_KEY` is set correctly
- Make sure there are no quotes around the API key

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find and kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### Issue: Frontend can't connect to backend

**Solution:**
- Ensure backend is running on port 8000
- Check `API_BASE_URL` in `frontend/app.py`
- Verify firewall isn't blocking localhost connections

### Issue: Database is empty

**Solution:**
```bash
python scripts/setup_database.py
```

### Issue: Vector store is empty

**Solution:**
```bash
python scripts/setup_vector_db.py
```

### Issue: Slow response times

**Possible causes:**
- First request initializes models (normal)
- Slow internet connection for API calls
- Large context in conversation

**Solution:**
- Wait for first request to complete
- Check internet connection
- Reset session if conversation is very long

---

## Uninstallation

To completely remove the application:

1. **Deactivate virtual environment:**
   ```bash
   deactivate
   ```

2. **Delete the project folder:**
   ```bash
   # Make sure you're in the parent directory
   rm -rf post-discharge-ai-assistant  # macOS/Linux
   rmdir /s post-discharge-ai-assistant  # Windows
   ```

---

## Next Steps

After successful installation:

1. **Read the Demo Guide**: `docs/demo_guide.md`
2. **Review Architecture**: `docs/architecture_justification.md`
3. **Try Different Patients**: See `data/patient_reports.json` for all 27 patients
4. **Explore API Documentation**: Visit `http://localhost:8000/docs`
5. **Check Logs**: Look at `logs/system.log` and `logs/interactions.jsonl`

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs in `logs/` directory
3. Consult the README.md
4. Open an issue on GitHub

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│                   (Streamlit Frontend)                      │
│                   http://localhost:8501                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST API
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                           │
│                   http://localhost:8000                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Multi-Agent System (LangGraph)             │  │
│  │  ┌──────────────────┐    ┌────────────────────────┐ │  │
│  │  │ Receptionist     │───▶│  Clinical AI Agent     │ │  │
│  │  │ Agent            │    │                        │ │  │
│  │  └──────────────────┘    └────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│         │                    │                    │         │
│         ▼                    ▼                    ▼         │
│  ┌──────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │ Patient  │      │ RAG System   │      │ Web Search   │ │
│  │ Database │      │ (ChromaDB)   │      │ (Tavily/DDG) │ │
│  └──────────┘      └──────────────┘      └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Congratulations! 🎉

Your Post Discharge Medical AI Assistant is now installed and ready to use!
