import streamlit as st
import pypdf
from google import genai
import os
import json

# Page Configuration
st.set_page_config(
    page_title="SmartCV Matrix",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for Dark Mode visibility, disabled text boxes, and metric styling
st.markdown("""
    <style>
    /* Dark background for app */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Text input and Text area styling (Editable) */
    .stTextArea textarea, .stTextInput input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    /* Fix for Disabled / Read-Only Text Areas (Comparison Tab) */
    .stTextArea textarea:disabled {
        background-color: #1e293b !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important; /* Forces full white text on Webkit browsers */
        opacity: 1 !important; /* Removes Streamlit default dimmed opacity */
        border: 1px solid #475569 !important;
    }

    /* Placeholder text color */
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {
        color: #94a3b8 !important;
    }

    /* Input Labels color */
    .stTextArea label, .stTextInput label, .stFileUploader label {
        color: #e2e8f0 !important;
    }

    /* Custom Metric Styling */
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 2.2rem !important;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📄 SmartCV Matrix")
st.caption("AI-Powered Resume Tailoring & Match Analysis | Powered by Gemini & Python")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your Google AI Studio API key")
    
    # Priority: Streamlit secrets -> Manual Input -> OS Env
    api_key = st.secrets.get("GEMINI_API_KEY", "") or api_key_input or os.getenv("GEMINI_API_KEY", "")
    
    if not api_key:
        st.warning("⚠️ Please provide a Gemini API Key to run the app.")

# Main Interface (Two Column Layout)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Application Inputs")
    uploaded_file = st.file_uploader("Upload Base Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Target Job Description", height=240, placeholder="Paste job requirements here...")
    
    submit_btn = st.button("✨ Tailor & Analyze Resume", type="primary", use_container_width=True)

with col2:
    st.subheader("🎯 Tailoring Results & Match Analysis")
    
    if submit_btn:
        if not api_key:
            st.error("Missing API Key! Please enter it in the sidebar.")
        elif not uploaded_file or not job_description:
            st.error("Please upload a PDF resume and enter a job description.")
        else:
            with st.spinner("Analyzing resume match score and tailoring content..."):
                try:
                    # 1. Extract text from PDF
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    resume_text = ""
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            resume_text += text
                    
                    resume_text = resume_text[:4000]

                    # 2. Call Gemini API with JSON structure request
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    You are an expert ATS (Applicant Tracking System) specialist and resume optimizer.
                    Analyze the following resume against the job description.
                    
                    Provide your output strictly in valid JSON format with three keys:
                    1. "match_score": An integer between 0 and 100 representing how well the tailored resume matches the job description.
                    2. "key_changes": A bulleted summary (in markdown format) highlighting what was added, modified, or emphasized (e.g., missing keywords added, skills reordered).
                    3. "tailored_resume": The fully rewritten and tailored resume in Markdown format.

                    RESUME TEXT:
                    {resume_text}
                    
                    JOB DESCRIPTION:
                    {job_description}
                    """

                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )

                    # 3. Parse JSON response
                    result_data = json.loads(response.text)
                    match_score = result_data.get("match_score", 85)
                    key_changes = result_data.get("key_changes", "Keywords and layout tailored for job alignment.")
                    tailored_resume = result_data.get("tailored_resume", "")

                    # 4. Display Metrics
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.metric(label="🎯 ATS Match Score", value=f"{match_score}%")
                    with m_col2:
                        st.download_button(
                            label="📥 Download Tailored Resume",
                            data=tailored_resume,
                            file_name="SmartCV_Tailored_Resume.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                    st.markdown("---")

                    # 5. Display Comparisons using Streamlit Tabs
                    tab1, tab2, tab3 = st.tabs(["✨ Tailored Resume", "🔍 Original vs Tailored", "⚡ Key Modifications"])

                    with tab1:
                        st.markdown(tailored_resume)

                    with tab2:
                        comp_col1, comp_col2 = st.columns(2)
                        with comp_col1:
                            st.markdown("### 📄 Original Resume")
                            st.text_area("Extracted Original Content", value=resume_text, height=400, disabled=True)
                        with comp_col2:
                            st.markdown("### 🎯 Tailored Output")
                            st.text_area("Optimized Content", value=tailored_resume, height=400, disabled=True)

                    with tab3:
                        st.markdown("### 📝 Changes & Keyword Enhancements")
                        st.markdown(key_changes)

                except Exception as e:
                    st.error(f"Error generating analysis: {str(e)}")
