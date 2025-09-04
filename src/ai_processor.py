"""
AI processor module for AI Resume Tailor
Handles Google Gemini API integration for resume optimization
"""
import os
import time
from typing import List, Dict, Optional
import google.generativeai as genai
from models import ResumeData, JobDescription, ContextEntry, OptimizationRequest, OptimizationResult, AIPrompt
from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_TOKENS, TEMPERATURE
import streamlit as st


class AIProcessor:
    """Handles AI processing using Google Gemini API"""
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model_name = GEMINI_MODEL
        self.max_tokens = MAX_TOKENS
        self.temperature = TEMPERATURE
        
        if not self.api_key:
            st.error("Google Gemini API key not found. Please set GEMINI_API_KEY in your environment variables.")
            return
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def optimize_resume(self, request: OptimizationRequest) -> Optional[OptimizationResult]:
        """Optimize resume based on job description and user context"""
        try:
            start_time = time.time()
            
            # Build the optimization prompt
            prompt = self._build_optimization_prompt(request)
            
            # Generate optimization
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            
            processing_time = time.time() - start_time
            
            if not response.text:
                st.error("No response generated from AI model")
                return None
            
            # Parse the response
            result = self._parse_optimization_response(
                response.text, 
                request.resume_data.raw_text,
                processing_time
            )
            
            return result
            
        except Exception as e:
            st.error(f"Error during AI processing: {str(e)}")
            return None
    
    def _build_optimization_prompt(self, request: OptimizationRequest) -> str:
        """Build the optimization prompt for the AI model"""
        
        # System prompt
        system_prompt = """You are an expert resume optimization specialist. Your task is to optimize a resume to better match a specific job description while maintaining authenticity and truthfulness.

Key principles:
1. Only use information provided in the resume and user context
2. Never fabricate or exaggerate experiences
3. Focus on relevant skills and experiences
4. Use action verbs and quantifiable achievements
5. Match keywords from the job description
6. Maintain professional tone and formatting

Provide your response in the following format:
OPTIMIZED_RESUME:
[The optimized resume content]

CHANGES_MADE:
- [List of specific changes made]

SUGGESTIONS:
- [Additional suggestions for improvement]

CONFIDENCE_SCORE:
[Score from 0.0 to 1.0 indicating confidence in the optimization]"""

        # Build context information
        context_info = self._build_context_info(request.user_context)
        
        # Build the main prompt
        prompt = f"""{system_prompt}

JOB DESCRIPTION:
Title: {request.job_description.title}
Company: {request.job_description.company}
Description: {request.job_description.description}

RESUME TO OPTIMIZE:
{request.resume_data.raw_text}

USER CONTEXT (Additional Information):
{context_info}

OPTIMIZATION FOCUS: {request.optimization_focus}

Please optimize the resume to better match the job description while following the principles above."""

        return prompt
    
    def _build_context_info(self, context_entries: List[ContextEntry]) -> str:
        """Build context information string from user context entries"""
        if not context_entries:
            return "No additional context provided."
        
        context_by_category = {}
        for entry in context_entries:
            if entry.category not in context_by_category:
                context_by_category[entry.category] = []
            context_by_category[entry.category].append(entry.content)
        
        context_info = ""
        for category, contents in context_by_category.items():
            context_info += f"\n{category.upper()}:\n"
            for content in contents:
                context_info += f"- {content}\n"
        
        return context_info
    
    def _parse_optimization_response(self, response_text: str, original_resume: str, processing_time: float) -> OptimizationResult:
        """Parse the AI response into structured data"""
        
        # Extract optimized resume
        optimized_resume = self._extract_section(response_text, "OPTIMIZED_RESUME:")
        if not optimized_resume:
            optimized_resume = original_resume
        
        # Extract changes made
        changes_text = self._extract_section(response_text, "CHANGES_MADE:")
        changes_made = self._parse_list(changes_text)
        
        # Extract suggestions
        suggestions_text = self._extract_section(response_text, "SUGGESTIONS:")
        suggestions = self._parse_list(suggestions_text)
        
        # Extract confidence score
        confidence_text = self._extract_section(response_text, "CONFIDENCE_SCORE:")
        confidence_score = self._parse_confidence_score(confidence_text)
        
        return OptimizationResult(
            original_resume=original_resume,
            optimized_resume=optimized_resume,
            changes_made=changes_made,
            suggestions=suggestions,
            confidence_score=confidence_score,
            processing_time=processing_time
        )
    
    def _extract_section(self, text: str, section_header: str) -> str:
        """Extract a specific section from the response text"""
        lines = text.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            if section_header in line:
                in_section = True
                continue
            
            if in_section:
                # Check if we've hit another section
                if any(header in line for header in ["OPTIMIZED_RESUME:", "CHANGES_MADE:", "SUGGESTIONS:", "CONFIDENCE_SCORE:"]):
                    break
                section_content.append(line)
        
        return '\n'.join(section_content).strip()
    
    def _parse_list(self, text: str) -> List[str]:
        """Parse a list from text (bullet points or numbered)"""
        if not text:
            return []
        
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove bullet points, numbers, or dashes
            line = line.lstrip('•-*0123456789. ')
            if line:
                items.append(line)
        
        return items
    
    def _parse_confidence_score(self, text: str) -> float:
        """Parse confidence score from text"""
        if not text:
            return 0.5  # Default confidence
        
        # Look for decimal numbers
        import re
        numbers = re.findall(r'0\.\d+|1\.0', text)
        if numbers:
            return float(numbers[0])
        
        # Look for percentages
        percentages = re.findall(r'(\d+)%', text)
        if percentages:
            return float(percentages[0]) / 100
        
        return 0.5  # Default confidence
    
    def generate_job_insights(self, job_description: JobDescription) -> Dict[str, str]:
        """Generate insights about a job description"""
        try:
            prompt = f"""Analyze this job description and provide insights:

JOB DESCRIPTION:
Title: {job_description.title}
Company: {job_description.company}
Description: {job_description.description}

Please provide:
1. Key skills required
2. Experience level expected
3. Industry/sector
4. Salary range estimate (if possible)
5. Growth opportunities
6. Company culture indicators

Format your response clearly with headers for each section."""

            response = self.model.generate_content(prompt)
            
            if response.text:
                return self._parse_insights_response(response.text)
            else:
                return {"error": "No insights generated"}
                
        except Exception as e:
            return {"error": f"Error generating insights: {str(e)}"}
    
    def _parse_insights_response(self, response_text: str) -> Dict[str, str]:
        """Parse insights response into structured data"""
        insights = {}
        current_section = None
        current_content = []
        
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header
            if any(keyword in line.lower() for keyword in ['key skills', 'experience', 'industry', 'salary', 'growth', 'culture']):
                # Save previous section
                if current_section and current_content:
                    insights[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            insights[current_section] = '\n'.join(current_content)
        
        return insights
    
    def validate_api_key(self) -> bool:
        """Validate if the API key is working"""
        try:
            if not self.api_key:
                return False
            
            # Try a simple test request
            test_response = self.model.generate_content("Hello, this is a test.")
            return test_response.text is not None
            
        except Exception:
            return False
