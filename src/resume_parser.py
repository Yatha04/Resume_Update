"""
Resume parser module for AI Resume Tailor
Handles PDF and DOCX file parsing and text extraction
"""
import os
import re
import tempfile
from typing import Dict, List, Optional, Tuple
import PyPDF2
import pdfplumber
from docx import Document
import streamlit as st
from models import ResumeData, RESUME_SECTIONS, SKILL_CATEGORIES
from config import SUPPORTED_FORMATS, MAX_FILE_SIZE_MB, TEMP_DIR


class ResumeParser:
    """Handles parsing of resume files in PDF and DOCX formats"""
    
    def __init__(self):
        self.supported_formats = SUPPORTED_FORMATS
        self.max_file_size = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
    
    def parse_file(self, uploaded_file) -> Optional[ResumeData]:
        """Parse uploaded resume file and extract structured data"""
        try:
            # Validate file
            if not self._validate_file(uploaded_file):
                return None
            
            # Extract text based on file type
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            if file_extension == '.pdf':
                raw_text = self._extract_pdf_text(uploaded_file)
            elif file_extension == '.docx':
                raw_text = self._extract_docx_text(uploaded_file)
            else:
                st.error(f"Unsupported file format: {file_extension}")
                return None
            
            if not raw_text or len(raw_text.strip()) < 50:
                st.error("Could not extract meaningful text from the file")
                return None
            
            # Parse structured data
            sections = self._parse_sections(raw_text)
            skills = self._extract_skills(raw_text)
            experience = self._extract_experience(sections.get('experience', ''))
            education = self._extract_education(sections.get('education', ''))
            projects = self._extract_projects(sections.get('projects', ''))
            
            return ResumeData(
                raw_text=raw_text,
                sections=sections,
                skills=skills,
                experience=experience,
                education=education,
                projects=projects,
                file_type=file_extension,
                file_name=uploaded_file.name
            )
            
        except Exception as e:
            st.error(f"Error parsing file: {str(e)}")
            return None
    
    def _validate_file(self, uploaded_file) -> bool:
        """Validate uploaded file"""
        # Check file size
        if uploaded_file.size > self.max_file_size:
            st.error(f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB")
            return False
        
        # Check file format
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in self.supported_formats:
            st.error(f"Unsupported file format. Supported: {', '.join(self.supported_formats)}")
            return False
        
        return True
    
    def _extract_pdf_text(self, uploaded_file) -> str:
        """Extract text from PDF file"""
        try:
            # Try pdfplumber first (better for complex layouts)
            uploaded_file.seek(0)
            with pdfplumber.open(uploaded_file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception:
            # Fallback to PyPDF2
            try:
                uploaded_file.seek(0)
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except Exception as e:
                raise Exception(f"PDF parsing failed: {str(e)}")
    
    def _extract_docx_text(self, uploaded_file) -> str:
        """Extract text from DOCX file"""
        try:
            uploaded_file.seek(0)
            doc = Document(uploaded_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"DOCX parsing failed: {str(e)}")
    
    def _parse_sections(self, text: str) -> Dict[str, str]:
        """Parse resume text into sections"""
        sections = {}
        text_lower = text.lower()
        
        # Define section patterns
        section_patterns = {
            'contact': r'(?:contact|personal|header)\s*:?',
            'summary': r'(?:summary|objective|profile|about)\s*:?',
            'experience': r'(?:experience|work|employment|professional)\s*:?',
            'education': r'(?:education|academic|qualifications)\s*:?',
            'skills': r'(?:skills|technical|competencies)\s*:?',
            'projects': r'(?:projects|portfolio|work samples)\s*:?',
            'certifications': r'(?:certifications|certificates|credentials)\s*:?',
            'achievements': r'(?:achievements|awards|honors)\s*:?',
            'publications': r'(?:publications|papers|research)\s*:?',
            'volunteer': r'(?:volunteer|community|service)\s*:?'
        }
        
        # Find section boundaries
        section_positions = []
        for section_name, pattern in section_patterns.items():
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            for match in matches:
                section_positions.append((match.start(), section_name))
        
        # Sort by position
        section_positions.sort(key=lambda x: x[0])
        
        # Extract section content
        for i, (start_pos, section_name) in enumerate(section_positions):
            # Find end position (next section or end of text)
            if i + 1 < len(section_positions):
                end_pos = section_positions[i + 1][0]
            else:
                end_pos = len(text)
            
            # Extract section content
            section_content = text[start_pos:end_pos].strip()
            sections[section_name] = section_content
        
        return sections
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        skills = set()
        text_lower = text.lower()
        
        # Extract skills from each category
        for category, skill_list in SKILL_CATEGORIES.items():
            for skill in skill_list:
                if skill.lower() in text_lower:
                    skills.add(skill)
        
        # Look for skills section specifically
        skills_section = self._find_section_content(text, 'skills')
        if skills_section:
            # Extract comma-separated or bullet-pointed skills
            skill_patterns = [
                r'[•\-\*]\s*([^,\n]+)',
                r'([^,\n]+)(?=,|\n)',
            ]
            
            for pattern in skill_patterns:
                matches = re.findall(pattern, skills_section, re.IGNORECASE)
                for match in matches:
                    skill = match.strip()
                    if len(skill) > 2 and len(skill) < 50:  # Reasonable skill length
                        skills.add(skill)
        
        return list(skills)
    
    def _extract_experience(self, experience_text: str) -> List[Dict]:
        """Extract work experience from text"""
        experiences = []
        if not experience_text:
            return experiences
        
        # Split by common separators
        entries = re.split(r'\n\s*\n|\n(?=[A-Z][a-z]+.*\d{4})', experience_text)
        
        for entry in entries:
            if len(entry.strip()) < 20:  # Skip very short entries
                continue
            
            # Extract job title, company, dates
            title_match = re.search(r'^([^,\n]+)', entry.strip())
            company_match = re.search(r'at\s+([^,\n]+)|([^,\n]+)\s*,\s*([^,\n]+)', entry)
            date_match = re.search(r'(\d{4})\s*[-–]\s*(\d{4}|present|current)', entry, re.IGNORECASE)
            
            experience = {
                'title': title_match.group(1).strip() if title_match else '',
                'company': '',
                'start_date': '',
                'end_date': '',
                'description': entry.strip()
            }
            
            if company_match:
                experience['company'] = company_match.group(1) or company_match.group(2) or ''
            
            if date_match:
                experience['start_date'] = date_match.group(1)
                experience['end_date'] = date_match.group(2)
            
            experiences.append(experience)
        
        return experiences
    
    def _extract_education(self, education_text: str) -> List[Dict]:
        """Extract education information from text"""
        education = []
        if not education_text:
            return education
        
        # Split by common separators
        entries = re.split(r'\n\s*\n', education_text)
        
        for entry in entries:
            if len(entry.strip()) < 10:
                continue
            
            # Extract degree, institution, dates
            degree_match = re.search(r'([A-Z][^,\n]*(?:degree|bachelor|master|phd|doctorate)[^,\n]*)', entry, re.IGNORECASE)
            institution_match = re.search(r'at\s+([^,\n]+)|([^,\n]+)\s*,\s*([^,\n]+)', entry)
            date_match = re.search(r'(\d{4})', entry)
            
            edu_entry = {
                'degree': degree_match.group(1).strip() if degree_match else '',
                'institution': '',
                'year': '',
                'description': entry.strip()
            }
            
            if institution_match:
                edu_entry['institution'] = institution_match.group(1) or institution_match.group(2) or ''
            
            if date_match:
                edu_entry['year'] = date_match.group(1)
            
            education.append(edu_entry)
        
        return education
    
    def _extract_projects(self, projects_text: str) -> List[Dict]:
        """Extract project information from text"""
        projects = []
        if not projects_text:
            return projects
        
        # Split by common separators
        entries = re.split(r'\n\s*\n|\n(?=[A-Z][a-z]+.*:)', projects_text)
        
        for entry in entries:
            if len(entry.strip()) < 15:
                continue
            
            # Extract project name and description
            name_match = re.search(r'^([^:\n]+)', entry.strip())
            
            project = {
                'name': name_match.group(1).strip() if name_match else '',
                'description': entry.strip(),
                'technologies': []
            }
            
            # Extract technologies mentioned
            for category, tech_list in SKILL_CATEGORIES.items():
                for tech in tech_list:
                    if tech.lower() in entry.lower():
                        project['technologies'].append(tech)
            
            projects.append(project)
        
        return projects
    
    def _find_section_content(self, text: str, section_name: str) -> str:
        """Find content of a specific section"""
        patterns = RESUME_SECTIONS.get(section_name, [section_name])
        
        for pattern in patterns:
            match = re.search(rf'{pattern}\s*:?\s*\n(.*?)(?=\n[A-Z][a-z]+\s*:|\Z)', 
                            text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
