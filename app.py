"""
AI Resume Tailor - Main Streamlit Application
A web application for AI-powered resume optimization
"""
import streamlit as st
import os
from datetime import datetime
from typing import Optional, List

# Import our modules
from src.database import db
from src.resume_parser import ResumeParser
from src.ai_processor import AIProcessor
from src.models import ResumeData, JobDescription, ContextEntry, OptimizationRequest, OptimizationResult
from src.utils import (
    clean_text, extract_keywords, calculate_similarity, format_file_size,
    validate_resume_content, create_sidebar_navigation, format_optimization_result,
    display_error_message, display_success_message, display_info_message,
    create_download_button, extract_contact_info
)
from config import PAGE_TITLE, PAGE_ICON, LAYOUT

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def initialize_components():
    """Initialize app components"""
    return ResumeParser(), AIProcessor()

resume_parser, ai_processor = initialize_components()

# Session state initialization
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'job_description' not in st.session_state:
    st.session_state.job_description = None
if 'optimization_result' not in st.session_state:
    st.session_state.optimization_result = None
if 'user_context' not in st.session_state:
    st.session_state.user_context = []

def main():
    """Main application function"""
    
    # Sidebar navigation
    current_page = create_sidebar_navigation()
    
    # Main content area
    if current_page == "home":
        show_home_page()
    elif current_page == "upload":
        show_upload_page()
    elif current_page == "context":
        show_context_page()
    elif current_page == "optimize":
        show_optimize_page()
    elif current_page == "results":
        show_results_page()
    elif current_page == "settings":
        show_settings_page()

def show_home_page():
    """Display home page"""
    st.title("🎯 AI Resume Tailor")
    st.markdown("---")
    
    st.markdown("""
    Welcome to **AI Resume Tailor**, your intelligent resume optimization assistant! 
    This tool uses AI to help you tailor your resume for specific job opportunities.
    
    ### 🚀 How it works:
    1. **Upload your resume** (PDF or DOCX format)
    2. **Add additional context** about your experiences and achievements
    3. **Enter the job description** you're applying for
    4. **Get an optimized resume** tailored to the specific role
    
    ### ✨ Features:
    - 📄 **Smart Resume Parsing**: Extracts and structures your resume content
    - 🧠 **AI-Powered Optimization**: Uses Google Gemini AI for intelligent tailoring
    - 💾 **Context Memory**: Stores your additional experiences for future use
    - 🎯 **Keyword Matching**: Aligns your resume with job requirements
    - 📊 **Detailed Analysis**: Shows what changes were made and why
    
    ### 🛠️ Getting Started:
    Use the sidebar to navigate through the application. Start by uploading your resume!
    """)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Resume Uploaded", "✅" if st.session_state.resume_data else "❌")
    
    with col2:
        context_count = len(st.session_state.user_context)
        st.metric("Context Entries", context_count)
    
    with col3:
        st.metric("API Status", "✅" if ai_processor.validate_api_key() else "❌")

def show_upload_page():
    """Display resume upload page"""
    st.title("📄 Upload Resume")
    st.markdown("---")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**File:** {uploaded_file.name}")
        with col2:
            st.info(f"**Size:** {format_file_size(uploaded_file.size)}")
        
        # Parse resume
        if st.button("🔍 Parse Resume", type="primary"):
            with st.spinner("Parsing resume..."):
                resume_data = resume_parser.parse_file(uploaded_file)
                
                if resume_data:
                    st.session_state.resume_data = resume_data
                    display_success_message("Resume parsed successfully!")
                    
                    # Display parsed content
                    with st.expander("📋 Parsed Resume Content", expanded=True):
                        st.text_area("Raw Text", resume_data.raw_text, height=200)
                        
                        # Display structured data
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("🎯 Skills Found")
                            if resume_data.skills:
                                st.write(", ".join(resume_data.skills))
                            else:
                                st.write("No skills detected")
                        
                        with col2:
                            st.subheader("💼 Experience")
                            st.write(f"{len(resume_data.experience)} entries found")
                        
                        # Validation results
                        validation = validate_resume_content(resume_data.raw_text)
                        if validation['is_valid']:
                            display_success_message("Resume validation passed!")
                        else:
                            st.warning("⚠️ Resume validation issues found:")
                            for issue in validation['issues']:
                                st.write(f"• {issue}")
                else:
                    display_error_message("Failed to parse resume")

def show_context_page():
    """Display context management page"""
    st.title("💼 Add Context")
    st.markdown("---")
    
    st.markdown("""
    Add additional information about your experiences, projects, and achievements 
    that might not be fully captured in your resume. This helps the AI provide 
    better optimization suggestions.
    """)
    
    # Add new context
    st.subheader("➕ Add New Context")
    
    with st.form("add_context_form"):
        category = st.selectbox(
            "Category",
            ["experience", "project", "achievement", "skill", "certification", "education", "volunteer", "publication", "award", "other"]
        )
        
        content = st.text_area(
            "Content",
            placeholder="Describe your experience, project, or achievement in detail...",
            height=100
        )
        
        submitted = st.form_submit_button("💾 Save Context", type="primary")
        
        if submitted and content.strip():
            try:
                context_id = db.add_context(category, content.strip())
                display_success_message(f"Context added successfully! (ID: {context_id})")
                st.rerun()
            except Exception as e:
                display_error_message(f"Failed to add context: {str(e)}")
    
    # Display existing context
    st.subheader("📚 Existing Context")
    
    all_context = db.get_all_context()
    if all_context:
        # Group by category
        context_by_category = {}
        for entry in all_context:
            if entry['category'] not in context_by_category:
                context_by_category[entry['category']] = []
            context_by_category[entry['category']].append(entry)
        
        for category, entries in context_by_category.items():
            with st.expander(f"📁 {category.title()} ({len(entries)} entries)"):
                for entry in entries:
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.write(entry['content'])
                        st.caption(f"Added: {entry['created_at']}")
                    
                    with col2:
                        if st.button("🗑️", key=f"delete_{entry['id']}", help="Delete this entry"):
                            if db.delete_context(entry['id']):
                                display_success_message("Context deleted successfully!")
                                st.rerun()
                            else:
                                display_error_message("Failed to delete context")
    else:
        st.info("No context entries yet. Add some to get started!")

def show_optimize_page():
    """Display resume optimization page"""
    st.title("🎯 Optimize Resume")
    st.markdown("---")
    
    # Check prerequisites
    if not st.session_state.resume_data:
        st.warning("⚠️ Please upload a resume first!")
        return
    
    # Job description input
    st.subheader("📋 Job Description")
    
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer")
    with col2:
        company = st.text_input("Company", placeholder="e.g., Google")
    
    job_description_text = st.text_area(
        "Job Description",
        placeholder="Paste the complete job description here...",
        height=200
    )
    
    # Optimization options
    st.subheader("⚙️ Optimization Options")
    
    col1, col2 = st.columns(2)
    with col1:
        optimization_focus = st.selectbox(
            "Focus Area",
            ["all", "skills", "experience", "achievements", "keywords"]
        )
    with col2:
        use_context = st.checkbox("Use stored context", value=True)
    
    # Optimize button
    if st.button("🚀 Optimize Resume", type="primary", disabled=not job_description_text.strip()):
        if not job_title or not company:
            st.warning("Please provide both job title and company name.")
            return
        
        # Create job description object
        job_description = JobDescription(
            title=job_title,
            company=company,
            description=job_description_text,
            requirements=[],  # Could be extracted from description
            responsibilities=[],  # Could be extracted from description
            skills_mentioned=extract_keywords(job_description_text)
        )
        
        # Get user context
        user_context = []
        if use_context:
            context_entries = db.get_all_context()
            user_context = [
                ContextEntry(
                    id=entry['id'],
                    category=entry['category'],
                    content=entry['content'],
                    created_at=entry['created_at'],
                    updated_at=entry['updated_at']
                )
                for entry in context_entries
            ]
        
        # Create optimization request
        request = OptimizationRequest(
            resume_data=st.session_state.resume_data,
            job_description=job_description,
            user_context=user_context,
            optimization_focus=optimization_focus
        )
        
        # Perform optimization
        with st.spinner("🤖 AI is optimizing your resume..."):
            result = ai_processor.optimize_resume(request)
            
            if result:
                st.session_state.optimization_result = result
                st.session_state.job_description = job_description
                display_success_message("Resume optimization completed!")
                st.rerun()
            else:
                display_error_message("Failed to optimize resume")

def show_results_page():
    """Display optimization results page"""
    st.title("📊 Optimization Results")
    st.markdown("---")
    
    if not st.session_state.optimization_result:
        st.info("No optimization results yet. Please optimize a resume first!")
        return
    
    result = st.session_state.optimization_result
    job_desc = st.session_state.job_description
    
    # Display job information
    if job_desc:
        st.subheader("🎯 Target Job")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Position:** {job_desc.title}")
        with col2:
            st.write(f"**Company:** {job_desc.company}")
    
    # Display optimization results
    format_optimization_result(result)
    
    # Download options
    st.subheader("📥 Download Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_download_button(
            result.optimized_resume,
            "optimized_resume.txt",
            "text/plain"
        )
    
    with col2:
        changes_text = "\n".join([f"• {change}" for change in result.changes_made])
        create_download_button(
            changes_text,
            "changes_made.txt",
            "text/plain"
        )
    
    with col3:
        suggestions_text = "\n".join([f"• {suggestion}" for suggestion in result.suggestions])
        create_download_button(
            suggestions_text,
            "suggestions.txt",
            "text/plain"
        )

def show_settings_page():
    """Display settings page"""
    st.title("⚙️ Settings")
    st.markdown("---")
    
    # API Configuration
    st.subheader("🔑 API Configuration")
    
    api_key_status = ai_processor.validate_api_key()
    if api_key_status:
        st.success("✅ Google Gemini API key is configured and working")
    else:
        st.error("❌ Google Gemini API key is not configured or invalid")
        st.info("Please set the GEMINI_API_KEY environment variable")
    
    # Database Information
    st.subheader("💾 Database Information")
    
    try:
        all_context = db.get_all_context()
        categories = db.get_categories()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Context Entries", len(all_context))
        with col2:
            st.metric("Categories", len(categories))
        
        if categories:
            st.write("**Available Categories:**")
            for category in categories:
                count = len([c for c in all_context if c['category'] == category])
                st.write(f"• {category.title()}: {count} entries")
    
    except Exception as e:
        st.error(f"Database error: {str(e)}")
    
    # Clear Data
    st.subheader("🗑️ Clear Data")
    
    if st.button("Clear All Context", type="secondary"):
        try:
            # This would need to be implemented in the database module
            st.warning("This feature is not yet implemented")
        except Exception as e:
            st.error(f"Error clearing data: {str(e)}")

if __name__ == "__main__":
    main()
