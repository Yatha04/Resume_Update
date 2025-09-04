"""
Data models and schemas for AI Resume Tailor
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class ResumeData:
    """Represents parsed resume data"""
    raw_text: str
    sections: Dict[str, str]
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    file_type: str
    file_name: str


@dataclass
class JobDescription:
    """Represents a job description"""
    title: str
    company: str
    description: str
    requirements: List[str]
    responsibilities: List[str]
    skills_mentioned: List[str]


@dataclass
class ContextEntry:
    """Represents a user context entry"""
    id: Optional[int]
    category: str
    content: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


@dataclass
class OptimizationRequest:
    """Represents a resume optimization request"""
    resume_data: ResumeData
    job_description: JobDescription
    user_context: List[ContextEntry]
    optimization_focus: str  # 'skills', 'experience', 'achievements', 'all'


@dataclass
class OptimizationResult:
    """Represents the result of resume optimization"""
    original_resume: str
    optimized_resume: str
    changes_made: List[str]
    suggestions: List[str]
    confidence_score: float
    processing_time: float


@dataclass
class AIPrompt:
    """Represents an AI prompt structure"""
    system_prompt: str
    user_prompt: str
    context: str
    examples: Optional[List[str]] = None


# Common categories for user context
CONTEXT_CATEGORIES = [
    'experience',
    'project',
    'achievement',
    'skill',
    'certification',
    'education',
    'volunteer',
    'publication',
    'award',
    'other'
]

# Resume sections mapping
RESUME_SECTIONS = {
    'contact': ['contact', 'personal', 'header'],
    'summary': ['summary', 'objective', 'profile', 'about'],
    'experience': ['experience', 'work', 'employment', 'professional'],
    'education': ['education', 'academic', 'qualifications'],
    'skills': ['skills', 'technical', 'competencies'],
    'projects': ['projects', 'portfolio', 'work samples'],
    'certifications': ['certifications', 'certificates', 'credentials'],
    'achievements': ['achievements', 'awards', 'honors'],
    'publications': ['publications', 'papers', 'research'],
    'volunteer': ['volunteer', 'community', 'service']
}

# Common skills categories
SKILL_CATEGORIES = {
    'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin'],
    'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'express'],
    'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite'],
    'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
    'data': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'r', 'matplotlib'],
    'tools': ['git', 'jira', 'confluence', 'slack', 'figma', 'photoshop', 'excel'],
    'languages': ['english', 'spanish', 'french', 'german', 'chinese', 'japanese', 'korean']
}
