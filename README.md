# 🎯 AI Resume Tailor

An intelligent resume optimization tool that uses AI to tailor your resume for specific job opportunities. Built with Streamlit and powered by Google Gemini AI.

## ✨ Features

- 📄 **Smart Resume Parsing**: Automatically extracts and structures content from PDF and DOCX resumes
- 🧠 **AI-Powered Optimization**: Uses Google Gemini AI for intelligent resume tailoring
- 💾 **Context Memory**: Stores additional experiences and achievements for future use
- 🎯 **Keyword Matching**: Aligns your resume with job requirements and keywords
- 📊 **Detailed Analysis**: Shows what changes were made and provides improvement suggestions
- 🔄 **Caching**: Remembers previous optimizations for similar job descriptions
- 📱 **Modern UI**: Clean, intuitive web interface built with Streamlit

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Resume_Update
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create a .env file in the project root
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 📖 How to Use

### 1. Upload Your Resume
- Go to the "Upload Resume" page
- Upload your resume in PDF or DOCX format
- The system will parse and extract structured information

### 2. Add Context (Optional)
- Navigate to "Add Context" page
- Add additional experiences, projects, or achievements
- This information helps the AI provide better optimization suggestions

### 3. Optimize Your Resume
- Go to "Optimize Resume" page
- Enter the job title, company, and job description
- Choose optimization focus (skills, experience, achievements, etc.)
- Click "Optimize Resume" and wait for AI processing

### 4. Review Results
- View the optimized resume on the "Results" page
- See what changes were made and why
- Download the optimized resume and change summary

## 🏗️ Project Structure

```
├── app.py                 # Main Streamlit application
├── config.py             # Configuration and API keys
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── src/
│   ├── __init__.py
│   ├── resume_parser.py  # PDF/DOCX resume parsing
│   ├── ai_processor.py   # Google Gemini API integration
│   ├── database.py       # SQLite database operations
│   ├── models.py         # Data models and schemas
│   └── utils.py          # Utility functions
├── data/
│   ├── resume_context.db # SQLite database
│   └── temp/            # Temporary file storage
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### API Costs

- **Google Gemini Pro**: Approximately $2-5/month for 10 resumes/week usage
- The application includes rate limiting and caching to minimize API costs
- Local processing reduces the number of API calls needed

## 🛠️ Technical Details

### Dependencies

- **Streamlit**: Web application framework
- **Google Generative AI**: AI model integration
- **PyPDF2/pdfplumber**: PDF file parsing
- **python-docx**: DOCX file parsing
- **SQLite**: Local database for context memory
- **python-dotenv**: Environment variable management

### Database Schema

The application uses SQLite with the following tables:

```sql
-- User context for additional experiences
CREATE TABLE user_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job descriptions for caching
CREATE TABLE job_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL,
    company TEXT NOT NULL,
    description TEXT NOT NULL,
    optimized_resume TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔒 Privacy & Security

- **Local Processing**: All data is processed locally on your machine
- **No Cloud Storage**: Resumes and personal information are not stored in the cloud
- **API Security**: Only resume content is sent to Google Gemini API for optimization
- **Data Retention**: Context data is stored locally in SQLite database

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your Google Gemini API key is correctly set in the `.env` file
   - Verify the API key is active and has sufficient quota

2. **File Upload Issues**
   - Supported formats: PDF and DOCX only
   - Maximum file size: 10MB
   - Ensure the file is not corrupted or password-protected

3. **Parsing Errors**
   - Some PDFs with complex layouts may not parse perfectly
   - Try converting to DOCX format for better results
   - Ensure the resume contains readable text (not just images)

4. **Database Errors**
   - Ensure the `data/` directory exists and is writable
   - Check file permissions for the SQLite database

### Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Verify all dependencies are installed correctly
3. Ensure your API key is valid and has quota remaining
4. Check that all required directories exist

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for providing the AI capabilities
- Streamlit for the excellent web framework
- The open-source community for the various libraries used

---

**Happy job hunting! 🚀**