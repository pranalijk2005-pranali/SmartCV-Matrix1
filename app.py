import streamlit as st
import pypdf
from google import genai
import os

# Page Configuration
st.set_page_config(
    page_title="SmartCV Matrix",
    page_icon="📄",
    layout="wide"
)

# Custom Styling to match sleek dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📄 SmartCV Matrix")
st.caption("AI-Powered Resume Tailoring | Powered by Gemini & Python")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    # Tries to get key from secrets, defaults to text input if missing
    api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your Google AI Studio API key")
    
    # Priority: Streamlit secrets -> Manual Input -> OS Env
    api_key = st.secrets.get("GEMINI_API_KEY", "") or api_key_input or os.getenv("GEMINI_API_KEY", "")
    
    if not api_key:
        st.warning("⚠️ Please provide a Gemini API Key to run the app.")

# Main Interface (Two Column Layout)
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Application Inputs")
    uploaded_file = st.file_uploader("Upload Base Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Target Job Description", height=220, placeholder="Paste job requirements here...")
    
    submit_btn = st.button("✨ Tailor Resume", type="primary", use_container_width=True)

with col2:
    st.subheader("🎯 Tailoring Results")
    
    if submit_btn:
        if not api_key:
            st.error("Missing API Key! Please enter it in the sidebar.")
        elif not uploaded_file or not job_description:
            st.error("Please upload a PDF resume and enter a job description.")
        else:
            with st.spinner("Analyzing resume and tailoring with Gemini AI..."):
                try:
                    # Extract text from PDF
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    resume_text = ""
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            resume_text += text
                    
                    # Truncate text (limit character length to prevent token issues)
                    resume_text = resume_text[:4000]

                    # Initialize Gemini Client
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    You are an expert resume optimizer. Tailor the following resume to match the job description.
                    Maintain exact personal details, accuracy, and format section titles and lists using Markdown.
                    
                    RESUME TEXT:
                    {resume_text}
                    
                    JOB DESCRIPTION:
                    {job_description}
                    """

                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt,
                    )

                    # Display formatted markdown
                    st.markdown(response.text)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Tailored Resume (.txt)",
                        data=response.text,
                        file_name="SmartCV_Tailored_Resume.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"Error generating resume: {str(e)}")