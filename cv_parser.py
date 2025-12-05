import re
import os
from PyPDF2 import PdfReader
import docx

class CVParser:
    def __init__(self):
        # Common technical skills to look for
        self.skills_db = [
            # Programming Languages
            "python", "java", "c++", "c#", "javascript", "typescript", "html", "css", "sql", "r", "go", "ruby", "php", "swift", "kotlin",
            # Web Frameworks
            "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring", "asp.net", "laravel",
            # Data Science & AI
            "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "nlp", "computer vision", "generative ai", "llm",
            # Cloud & DevOps
            "aws", "azure", "google cloud", "docker", "kubernetes", "jenkins", "git", "linux", "terraform", "ansible",
            # Databases
            "postgresql", "mysql", "mongodb", "redis", "oracle", "sqlite", "firebase",
            # Tools & Others
            "jira", "agile", "scrum", "figma", "tableau", "power bi", "excel"
        ]
        
        # Common job titles
        self.job_titles_db = [
            "software engineer", "software developer", "frontend developer", "backend developer", "full stack developer",
            "data scientist", "data analyst", "data engineer", "machine learning engineer", "ai engineer",
            "product manager", "project manager", "ui/ux designer", "devops engineer", "qa engineer",
            "system administrator", "network engineer", "cyber security analyst"
        ]

    def extract_text_from_pdf(self, file_path):
        """Extract text from a PDF file."""
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text

    def extract_text_from_docx(self, file_path):
        """Extract text from a DOCX file."""
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX: {e}")
        return text

    def extract_email(self, text):
        """Extract email address from text."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def extract_phone(self, text):
        """Extract phone number from text."""
        # This is a basic pattern, might need refinement for different formats
        phone_pattern = r'(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None

    def extract_skills(self, text):
        """Extract skills from text based on the skills database."""
        found_skills = set()
        text_lower = text.lower()
        
        for skill in self.skills_db:
            # Use word boundary check to avoid partial matches (e.g., "java" in "javascript")
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.add(skill)
                
        return list(found_skills)

    def extract_job_title(self, text):
        """Attempt to extract the candidate's current or desired job title."""
        text_lower = text.lower()
        for title in self.job_titles_db:
            if title in text_lower:
                return title.title() # Return capitalized
        return "Unknown"

    def parse(self, file_path):
        """Main method to parse a CV file."""
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        
        if ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            text = self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        if not text:
            return {
                "error": "Could not extract text from file"
            }

        return {
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "job_title": self.extract_job_title(text),
            "raw_text": text[:1000] + "..." # Preview
        }

# Usage example
if __name__ == "__main__":
    parser = CVParser()
    # Test with a dummy file if it existed
    # print(parser.parse("test_cv.pdf"))
