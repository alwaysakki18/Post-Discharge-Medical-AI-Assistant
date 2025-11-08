# Quick Start Guide

## Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
# Copy environment file
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-your-key-here
```

### 3. Initialize System
```bash
# Setup database
python scripts/setup_database.py

# Setup vector database
python scripts/setup_vector_db.py
```

### 4. Start Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Start Frontend (New Terminal)
```bash
cd frontend
streamlit run app.py
```

### 6. Open Browser
Visit: `http://localhost:8501`

### 7. Try It Out
```
You: Hello
Bot: [Greeting from Receptionist Agent]

You: My name is John Smith
Bot: [Retrieves discharge report]

You: I have swelling in my legs
Bot: [Routes to Clinical Agent with medical advice]
```

---

## Windows Quick Setup

```bash
# Run automated setup
setup.bat

# Edit .env with your API key

# Start backend
start_backend.bat

# Start frontend (in new window)
start_frontend.bat
```

---

## Test Patients

Try these names:
- John Smith (CKD Stage 3)
- Sarah Johnson (Acute Kidney Injury)
- Michael Chen (Diabetic Nephropathy)
- Emily Rodriguez (Polycystic Kidney Disease)

See `data/patient_reports.json` for all 27 patients.

---

## Need Help?

- Full installation guide: `INSTALLATION.md`
- Demo guide: `docs/demo_guide.md`
- Architecture details: `docs/architecture_justification.md`
