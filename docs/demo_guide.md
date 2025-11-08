# Demo Guide

## Post Discharge Medical AI Assistant - Complete Demo Walkthrough

---

## Prerequisites

Before starting the demo, ensure:
- ✅ All dependencies installed (`pip install -r requirements.txt`)
- ✅ `.env` file created with OpenAI API key
- ✅ Database initialized (`python scripts/setup_database.py`)
- ✅ Vector database initialized (`python scripts/setup_vector_db.py`)
- ✅ Backend server running (`uvicorn backend.main:app --reload`)
- ✅ Frontend running (`streamlit run frontend/app.py`)

---

## Demo Scenario 1: Basic Patient Interaction

### Objective
Demonstrate the Receptionist Agent's ability to greet, identify, and retrieve patient information.

### Steps

1. **Start Conversation**
   ```
   User: Hello
   ```
   
   **Expected Response:**
   - Warm greeting from Receptionist Agent
   - Request for patient name

2. **Provide Patient Name**
   ```
   User: My name is John Smith
   ```
   
   **Expected Response:**
   - Receptionist uses `patient_data_retrieval` tool
   - Retrieves discharge report for John Smith
   - Displays diagnosis, medications, dietary restrictions
   - Asks follow-up questions

3. **Answer Follow-up Questions**
   ```
   User: I'm feeling better, taking my medications as prescribed
   ```
   
   **Expected Response:**
   - Acknowledges medication adherence
   - May ask about specific symptoms or dietary compliance

---

## Demo Scenario 2: Medical Query Routing

### Objective
Show how the Receptionist Agent routes medical questions to the Clinical Agent.

### Steps

1. **Continue from Scenario 1** (patient identified)

2. **Ask Medical Question**
   ```
   User: I'm having some swelling in my legs. Should I be worried?
   ```
   
   **Expected Response:**
   - Receptionist recognizes medical concern
   - Routes to Clinical AI Agent
   - Agent handoff logged

3. **Clinical Agent Response**
   - Clinical Agent receives query
   - Uses patient context (CKD diagnosis)
   - Searches nephrology knowledge base
   - Provides evidence-based response with citations
   - Includes medical disclaimer

---

## Demo Scenario 3: RAG in Action

### Objective
Demonstrate the Clinical Agent using RAG over nephrology reference materials.

### Steps

1. **Ask About CKD Stages**
   ```
   User: Can you explain the different stages of chronic kidney disease?
   ```
   
   **Expected Response:**
   - Clinical Agent uses `nephrology_knowledge_base` tool
   - Retrieves relevant information about CKD staging
   - Provides detailed explanation with GFR ranges
   - Cites source: nephrology_reference.txt

2. **Ask About Dietary Restrictions**
   ```
   User: What foods should I avoid with my kidney condition?
   ```
   
   **Expected Response:**
   - Searches knowledge base for dietary information
   - Provides specific recommendations (sodium, potassium, phosphorus)
   - Relates to patient's specific diagnosis
   - Includes citations

---

## Demo Scenario 4: Web Search Fallback

### Objective
Show the Clinical Agent using web search for information outside reference materials.

### Steps

1. **Ask About Recent Research**
   ```
   User: What's the latest research on SGLT2 inhibitors for kidney disease?
   ```
   
   **Expected Response:**
   - Clinical Agent recognizes query requires current information
   - Uses `web_search` tool
   - Returns recent research findings
   - Clearly labels as web search results
   - Provides source URLs
   - Includes disclaimer

2. **Ask About New Medication**
   ```
   User: Tell me about the newest treatments for diabetic nephropathy
   ```
   
   **Expected Response:**
   - Attempts knowledge base first
   - Falls back to web search for recent treatments
   - Provides current information with sources

---

## Demo Scenario 5: Different Patient Profiles

### Objective
Show system handling various patient conditions.

### Test Patients

1. **Sarah Johnson - Acute Kidney Injury**
   ```
   User: I'm Sarah Johnson
   ```
   - Different diagnosis and medications
   - Different warning signs
   - Tailored follow-up questions

2. **Michael Chen - Diabetic Nephropathy**
   ```
   User: My name is Michael Chen
   ```
   - Diabetes-related kidney disease
   - Multiple medications including insulin
   - Blood sugar monitoring instructions

3. **Emily Rodriguez - Polycystic Kidney Disease**
   ```
   User: I'm Emily Rodriguez
   ```
   - Genetic kidney disease
   - Different management approach
   - Specific warning signs

---

## Demo Scenario 6: System Features

### Logging Demonstration

1. **Check Logs**
   - Navigate to `logs/system.log`
   - Show timestamped events
   - Agent interactions
   - Tool usage

2. **Check Interaction Logs**
   - Open `logs/interactions.jsonl`
   - Show structured JSON logs
   - User inputs, agent responses
   - Agent handoffs
   - Database access
   - RAG retrieval
   - Web searches

### System Status

1. **API Status Endpoint**
   ```
   GET http://localhost:8000/status
   ```
   
   **Response:**
   ```json
   {
     "status": "operational",
     "database_patients": 27,
     "vector_store_documents": 150,
     "environment": "development"
   }
   ```

2. **Frontend Status Dashboard**
   - Shows API connection status
   - Patient count
   - Reference document count
   - Environment info

---

## Demo Scenario 7: Error Handling

### Patient Not Found

```
User: I'm Jane Doe
```

**Expected Response:**
- Receptionist searches database
- Patient not found
- Asks for correct spelling or full name

### Ambiguous Name

```
User: I'm John
```

**Expected Response:**
- Multiple matches possible
- Lists similar names
- Asks for clarification

---

## Demo Scenario 8: Session Management

### Reset Session

1. **Click "Reset Conversation" in sidebar**
   
   **Expected:**
   - Session cleared
   - New session ID generated
   - Fresh conversation starts

2. **Start New Conversation**
   - System greets as new patient
   - No memory of previous conversation

---

## Key Features to Highlight

### 1. Multi-Agent Architecture
- ✅ Clear separation of responsibilities
- ✅ Receptionist for patient management
- ✅ Clinical Agent for medical queries
- ✅ Seamless handoff between agents

### 2. RAG Implementation
- ✅ Semantic search over nephrology materials
- ✅ Source citations
- ✅ Accurate medical information
- ✅ Reduced hallucination

### 3. Web Search Integration
- ✅ Fallback for recent information
- ✅ Clear labeling of sources
- ✅ Tavily or DuckDuckGo
- ✅ Medical disclaimer

### 4. Patient Data Management
- ✅ 27 diverse patient profiles
- ✅ Fast database retrieval
- ✅ Fuzzy name matching
- ✅ Comprehensive discharge information

### 5. Logging System
- ✅ Complete audit trail
- ✅ Agent interactions logged
- ✅ Tool usage tracked
- ✅ Timestamped events

### 6. User Interface
- ✅ Clean, intuitive design
- ✅ Agent identification
- ✅ Medical disclaimers
- ✅ System status monitoring

---

## Common Demo Questions & Answers

### Q: How does the system handle medical emergencies?
**A:** The Clinical Agent recognizes severe symptoms and provides emergency guidance, advising patients to call 911 or go to the ER.

### Q: What happens if the knowledge base doesn't have the answer?
**A:** The system uses web search as a fallback, clearly labeling the source of information.

### Q: How is patient privacy maintained?
**A:** All data is dummy data for POC. In production, would implement HIPAA compliance, encryption, and access controls.

### Q: Can the system handle multiple patients simultaneously?
**A:** Current POC uses session-based management. Production version would support concurrent users with proper session isolation.

### Q: How accurate is the medical information?
**A:** Information comes from curated nephrology reference materials and reputable web sources. Always includes disclaimer to consult healthcare professionals.

---

## Troubleshooting

### Backend Not Starting
- Check `.env` file exists with valid API keys
- Ensure port 8000 is not in use
- Verify all dependencies installed

### Frontend Not Connecting
- Ensure backend is running on port 8000
- Check API_BASE_URL in frontend/app.py
- Verify CORS settings

### Database Empty
- Run `python scripts/setup_database.py`
- Check `data/patient_reports.json` exists

### Vector Store Empty
- Run `python scripts/setup_vector_db.py`
- Check `data/nephrology_reference.txt` exists

---

## Performance Metrics

### Expected Response Times
- Patient retrieval: < 1 second
- RAG query: 2-5 seconds
- Web search: 3-7 seconds
- Agent handoff: < 1 second

### System Capacity (POC)
- Patients: 27
- Reference documents: 1 (chunked into ~150 segments)
- Concurrent users: 1 (single session)
- Vector store size: ~50 MB

---

## Next Steps After Demo

1. **Gather Feedback**
   - User experience
   - Response accuracy
   - Feature requests

2. **Potential Enhancements**
   - Voice interface
   - Multi-language support
   - Mobile app
   - Integration with EHR systems
   - Appointment scheduling
   - Medication reminders

3. **Production Considerations**
   - HIPAA compliance
   - User authentication
   - Multi-user support
   - Scalability improvements
   - Monitoring and analytics

---

## Demo Script (5-Minute Version)

**Minute 1: Introduction**
- Explain the problem: Post-discharge patient care
- Show system architecture diagram
- Highlight multi-agent approach

**Minute 2: Basic Interaction**
- Greet system
- Provide patient name (John Smith)
- Show discharge report retrieval
- Answer follow-up questions

**Minute 3: Medical Query**
- Ask about leg swelling
- Show agent handoff
- Demonstrate RAG with citations
- Highlight medical disclaimer

**Minute 4: Advanced Features**
- Ask about recent research (web search)
- Show logging system
- Display system status
- Demonstrate different patient

**Minute 5: Wrap-up**
- Summarize key features
- Show architecture justification
- Discuss production roadmap
- Q&A

---

## Recording Tips

1. **Prepare Environment**
   - Clean browser cache
   - Close unnecessary applications
   - Test audio/video
   - Have backup plan

2. **Screen Recording**
   - Use OBS Studio or similar
   - 1080p resolution
   - Show both terminal and browser
   - Highlight cursor

3. **Narration**
   - Speak clearly and slowly
   - Explain what you're doing
   - Highlight key features
   - Keep under 5 minutes

4. **Editing**
   - Add title slide
   - Include timestamps
   - Add captions if possible
   - Export in MP4 format

---

## Conclusion

This demo showcases a complete, working POC of a multi-agent AI system for post-discharge patient care, featuring:
- ✅ 27+ patient discharge reports
- ✅ RAG over nephrology reference materials
- ✅ Multi-agent architecture with LangGraph
- ✅ Web search integration
- ✅ Comprehensive logging
- ✅ Modern web interface

The system is ready for demonstration, testing, and further development toward production deployment.
