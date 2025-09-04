"""
Database module for AI Resume Tailor
Handles SQLite database operations for user context memory
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from config import DATABASE_PATH


class DatabaseManager:
    """Manages SQLite database operations for user context"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._ensure_database_exists()
        self._create_tables()
    
    def _ensure_database_exists(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User context table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Job descriptions table for caching
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    description TEXT NOT NULL,
                    optimized_resume TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_context(self, category: str, content: str) -> int:
        """Add new context entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_context (category, content)
                VALUES (?, ?)
            ''', (category, content))
            conn.commit()
            return cursor.lastrowid
    
    def get_context_by_category(self, category: str) -> List[Dict]:
        """Get all context entries for a specific category"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM user_context 
                WHERE category = ?
                ORDER BY created_at DESC
            ''', (category,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_context(self) -> List[Dict]:
        """Get all context entries"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM user_context 
                ORDER BY category, created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def update_context(self, context_id: int, content: str) -> bool:
        """Update existing context entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_context 
                SET content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (content, context_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_context(self, context_id: int) -> bool:
        """Delete context entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_context WHERE id = ?', (context_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def save_job_description(self, job_title: str, company: str, description: str, optimized_resume: str = None) -> int:
        """Save job description and optimized resume"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO job_descriptions (job_title, company, description, optimized_resume)
                VALUES (?, ?, ?, ?)
            ''', (job_title, company, description, optimized_resume))
            conn.commit()
            return cursor.lastrowid
    
    def get_similar_job_descriptions(self, job_title: str, company: str) -> List[Dict]:
        """Find similar job descriptions for caching"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM job_descriptions 
                WHERE job_title LIKE ? OR company LIKE ?
                ORDER BY created_at DESC
                LIMIT 5
            ''', (f'%{job_title}%', f'%{company}%'))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT category FROM user_context ORDER BY category')
            return [row[0] for row in cursor.fetchall()]


# Global database instance
db = DatabaseManager()
