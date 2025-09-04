"""
Utility functions and helpers for AI Resume Tailor
"""
import re
import os
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import streamlit as st


def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
    
    # Remove multiple newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text"""
    if not text:
        return []
    
    # Convert to lowercase and split
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter by length and common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    keywords = [word for word in words if len(word) >= min_length and word not in stop_words]
    
    # Count frequency and return unique keywords
    return list(set(keywords))


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts using keyword overlap"""
    if not text1 or not text2:
        return 0.0
    
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))
    
    if not keywords1 or not keywords2:
        return 0.0
    
    intersection = keywords1.intersection(keywords2)
    union = keywords1.union(keywords2)
    
    return len(intersection) / len(union) if union else 0.0


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def generate_file_hash(file_content: bytes) -> str:
    """Generate hash for file content"""
    return hashlib.md5(file_content).hexdigest()


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits) <= 15


def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract contact information from text"""
    contact_info = {
        'email': '',
        'phone': '',
        'linkedin': '',
        'github': '',
        'website': ''
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info['email'] = email_match.group()
    
    # Extract phone
    phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        contact_info['phone'] = phone_match.group()
    
    # Extract LinkedIn
    linkedin_pattern = r'(?:linkedin\.com/in/|linkedin\.com/pub/)([a-zA-Z0-9-]+)'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = f"linkedin.com/in/{linkedin_match.group(1)}"
    
    # Extract GitHub
    github_pattern = r'(?:github\.com/)([a-zA-Z0-9-]+)'
    github_match = re.search(github_pattern, text, re.IGNORECASE)
    if github_match:
        contact_info['github'] = f"github.com/{github_match.group(1)}"
    
    # Extract website
    website_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
    website_match = re.search(website_pattern, text)
    if website_match:
        contact_info['website'] = website_match.group(1)
    
    return contact_info


def format_date(date_str: str) -> str:
    """Format date string to standard format"""
    if not date_str:
        return ""
    
    # Common date formats
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %Y',
        '%b %Y',
        '%Y',
        '%m/%Y',
        '%d-%m-%Y'
    ]
    
    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime('%B %Y')
        except ValueError:
            continue
    
    return date_str  # Return original if no format matches


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def highlight_keywords(text: str, keywords: List[str]) -> str:
    """Highlight keywords in text (for display purposes)"""
    if not text or not keywords:
        return text
    
    highlighted_text = text
    for keyword in keywords:
        # Case-insensitive highlighting
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        highlighted_text = pattern.sub(f"**{keyword}**", highlighted_text)
    
    return highlighted_text


def create_progress_bar(current: int, total: int, label: str = "Progress") -> None:
    """Create a progress bar in Streamlit"""
    if total > 0:
        progress = current / total
        st.progress(progress)
        st.caption(f"{label}: {current}/{total} ({progress:.1%})")


def display_error_message(error: str, details: str = None) -> None:
    """Display formatted error message in Streamlit"""
    st.error(f"❌ {error}")
    if details:
        with st.expander("Error Details"):
            st.code(details)


def display_success_message(message: str) -> None:
    """Display formatted success message in Streamlit"""
    st.success(f"✅ {message}")


def display_info_message(message: str) -> None:
    """Display formatted info message in Streamlit"""
    st.info(f"ℹ️ {message}")


def create_download_button(content: str, filename: str, mime_type: str = "text/plain") -> None:
    """Create a download button in Streamlit"""
    st.download_button(
        label="📥 Download",
        data=content,
        file_name=filename,
        mime=mime_type
    )


def validate_resume_content(resume_text: str) -> Dict[str, Any]:
    """Validate resume content and return analysis"""
    analysis = {
        'is_valid': True,
        'word_count': 0,
        'has_contact': False,
        'has_experience': False,
        'has_education': False,
        'has_skills': False,
        'issues': []
    }
    
    if not resume_text or len(resume_text.strip()) < 50:
        analysis['is_valid'] = False
        analysis['issues'].append("Resume content is too short")
        return analysis
    
    # Word count
    words = resume_text.split()
    analysis['word_count'] = len(words)
    
    if analysis['word_count'] < 100:
        analysis['issues'].append("Resume is very short (less than 100 words)")
    
    # Check for essential sections
    text_lower = resume_text.lower()
    
    # Contact information
    contact_keywords = ['email', 'phone', 'address', '@', 'linkedin', 'github']
    if any(keyword in text_lower for keyword in contact_keywords):
        analysis['has_contact'] = True
    else:
        analysis['issues'].append("No contact information found")
    
    # Experience
    experience_keywords = ['experience', 'work', 'employment', 'job', 'position', 'role']
    if any(keyword in text_lower for keyword in experience_keywords):
        analysis['has_experience'] = True
    else:
        analysis['issues'].append("No work experience section found")
    
    # Education
    education_keywords = ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'phd']
    if any(keyword in text_lower for keyword in education_keywords):
        analysis['has_education'] = True
    else:
        analysis['issues'].append("No education section found")
    
    # Skills
    skills_keywords = ['skills', 'technical', 'programming', 'software', 'tools']
    if any(keyword in text_lower for keyword in skills_keywords):
        analysis['has_skills'] = True
    else:
        analysis['issues'].append("No skills section found")
    
    # Overall validation
    if len(analysis['issues']) > 2:
        analysis['is_valid'] = False
    
    return analysis


def create_sidebar_navigation() -> str:
    """Create sidebar navigation for the app"""
    st.sidebar.title("📄 AI Resume Tailor")
    st.sidebar.markdown("---")
    
    pages = {
        "🏠 Home": "home",
        "📄 Upload Resume": "upload",
        "💼 Add Context": "context",
        "🎯 Optimize Resume": "optimize",
        "📊 View Results": "results",
        "⚙️ Settings": "settings"
    }
    
    selected_page = st.sidebar.selectbox("Navigate", list(pages.keys()))
    return pages[selected_page]


def format_optimization_result(result) -> None:
    """Format and display optimization result"""
    if not result:
        st.error("No optimization result to display")
        return
    
    # Display confidence score
    confidence_color = "green" if result.confidence_score > 0.7 else "orange" if result.confidence_score > 0.5 else "red"
    st.markdown(f"**Confidence Score:** :{confidence_color}[{result.confidence_score:.1%}]")
    
    # Display processing time
    st.caption(f"Processing time: {result.processing_time:.2f} seconds")
    
    # Display changes made
    if result.changes_made:
        st.subheader("📝 Changes Made")
        for change in result.changes_made:
            st.markdown(f"• {change}")
    
    # Display suggestions
    if result.suggestions:
        st.subheader("💡 Suggestions")
        for suggestion in result.suggestions:
            st.markdown(f"• {suggestion}")
    
    # Display optimized resume
    st.subheader("✨ Optimized Resume")
    st.text_area("Optimized Content", result.optimized_resume, height=400)
