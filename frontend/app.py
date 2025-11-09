"""
Streamlit frontend for Post Discharge Medical AI Assistant.
"""

import streamlit as st
import requests
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Post Discharge Medical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .disclaimer {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .receptionist-badge {
        background-color: #2196f3;
        color: white;
    }
    .clinical-badge {
        background-color: #4caf50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_system_status():
    """Get system status from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def send_message(message: str, session_id: str = None):
    """Send message to API."""
    try:
        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error communicating with API: {str(e)}")
        return None


def reset_session():
    """Reset the chat session."""
    try:
        response = requests.post(f"{API_BASE_URL}/reset", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Main application."""
    
    # Header
    st.markdown('<div class="main-header">🏥 Post Discharge Medical AI Assistant</div>', unsafe_allow_html=True)
    
    # Medical Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ Medical Disclaimer:</strong><br>
        This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice.
        In case of emergency, call 911 or go to the nearest emergency room.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ System Information")
        
        # Check API health
        api_healthy = check_api_health()
        
        if api_healthy:
            st.success("✅ API Connected")
            
            # Get system status
            status = get_system_status()
            if status:
                st.metric("Patients in Database", status.get("database_patients", 0))
                st.metric("Reference Documents", status.get("vector_store_documents", 0))
                st.info(f"Environment: {status.get('environment', 'Unknown')}")
        else:
            st.error("❌ API Not Connected")
            st.warning("Please start the backend server:\n```\ncd backend\nuvicorn main:app --reload\n```")
        
        st.divider()
        
        # Session controls
        st.header("🔄 Session Controls")
        if st.button("Reset Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.session_state.current_patient = None
            st.success("Session reset successfully!")
            st.rerun()
        
        st.divider()
        
        # Download Report Section
        st.header("📄 Download Report")
        patient_name_input = st.text_input(
            "Enter patient name to download report:",
            placeholder="e.g., John Smith",
            key="pdf_patient_name"
        )
        if st.button("📥 Download PDF Report", use_container_width=True):
            if patient_name_input:
                with st.spinner("Generating PDF..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/patient/report/pdf",
                            json={"patient_name": patient_name_input},
                            timeout=30
                        )
                        if response.status_code == 200:
                            # Get filename from headers or create default
                            filename = f"discharge_report_{patient_name_input.replace(' ', '_')}.pdf"
                            
                            # Offer download
                            st.download_button(
                                label="💾 Save PDF",
                                data=response.content,
                                file_name=filename,
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success(f"✅ Report generated for {patient_name_input}!")
                        elif response.status_code == 404:
                            st.error(f"❌ Patient '{patient_name_input}' not found")
                        else:
                            st.error("❌ Error generating report")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter a patient name")
        
        st.divider()
        
        # About
        st.header("📖 About")
        st.markdown("""
        This AI assistant helps post-discharge patients by:
        
        - **Receptionist Agent**: Greets patients, retrieves discharge reports, asks follow-up questions
        
        - **Clinical AI Agent**: Answers medical questions using nephrology reference materials and web search
        
        **Features:**
        - 27+ patient discharge reports
        - RAG over nephrology materials
        - Web search for recent information
        - Comprehensive logging
        """)
        
        st.divider()
        
        # Quick Start Guide
        with st.expander("🚀 Quick Start Guide"):
            st.markdown("""
            1. **Start a conversation** by saying hello
            2. **Provide your name** when asked
            3. **Answer follow-up questions** about your health
            4. **Ask medical questions** - they'll be routed to the Clinical Agent
            
            **Example patients:**
            - John Smith
            - Sarah Johnson
            - Michael Chen
            - Emily Rodriguez
            """)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial greeting from Receptionist Agent
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hello! I'm your post-discharge care assistant. I'm here to help you with your recovery. What's your name?",
            "agent": "Receptionist Agent",
            "timestamp": datetime.now().isoformat()
        })
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "current_patient" not in st.session_state:
        st.session_state.current_patient = None
    
    # Main chat interface
    st.header("💬 Chat Interface")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            agent = message.get("agent", "receptionist")
            
            if role == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong><br>
                    {content}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Normalize agent name
                agent_lower = agent.lower()
                is_receptionist = "receptionist" in agent_lower
                
                agent_badge_class = "receptionist-badge" if is_receptionist else "clinical-badge"
                agent_name = "Receptionist Agent" if is_receptionist else "Clinical AI Agent"
                agent_icon = "👋" if is_receptionist else "⚕️"
                
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <span class="agent-badge {agent_badge_class}">{agent_icon} {agent_name}</span><br>
                    {content.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    if api_healthy:
        # Use a form to handle message submission
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([6, 1])
            with col1:
                user_input = st.text_input(
                    "Type your message here...",
                    key="user_input",
                    label_visibility="collapsed",
                    placeholder="Type your message and press Enter or click Send..."
                )
            with col2:
                submit_button = st.form_submit_button("Send", use_container_width=True)
        
        if submit_button and user_input:
            # Add user message to chat
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Show thinking message
            with st.spinner("🤔 Processing..."):
                # Send to API with session_id
                response = send_message(user_input, st.session_state.session_id)
            
            if response:
                # Store session_id for subsequent messages
                if not st.session_state.session_id:
                    st.session_state.session_id = response.get("session_id")
                
                # Add assistant response to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.get("response", ""),
                    "agent": response.get("agent", "receptionist"),
                    "timestamp": response.get("timestamp", datetime.now().isoformat())
                })
                
                # Rerun to update chat display
                st.rerun()
            else:
                st.error("Failed to get response from the assistant. Please try again.")
    else:
        st.warning("⚠️ Please start the backend server to begin chatting.")
        st.code("cd backend\nuvicorn main:app --reload --port 8000", language="bash")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        Post Discharge Medical AI Assistant v1.0.0 | Built with LangGraph, FastAPI, and Streamlit<br>
        ⚕️ For educational purposes only - Always consult healthcare professionals
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
