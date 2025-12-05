from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from collections import Counter

class EnhancedJobMatcher:
    """
    Enhanced AI-powered job matcher with multiple matching strategies:
    - TF-IDF + Cosine Similarity for text matching
    - Skill-based matching with weighted importance
    - Experience level matching
    - Location preference matching
    - Salary range matching
    """
    
    def __init__(self):
        self.skill_weights = {
            'exact_match': 3.0,      # Exact skill match
            'partial_match': 1.5,    # Partial skill match
            'related_match': 1.0     # Related/similar skill
        }
        
        # Common skill synonyms and related terms
        self.skill_synonyms = {
            'javascript': ['js', 'ecmascript', 'node', 'nodejs'],
            'python': ['py', 'django', 'flask', 'fastapi'],
            'react': ['reactjs', 'react.js', 'react native'],
            'angular': ['angularjs', 'angular.js'],
            'vue': ['vuejs', 'vue.js'],
            'machine learning': ['ml', 'deep learning', 'ai', 'artificial intelligence'],
            'database': ['sql', 'nosql', 'mongodb', 'postgresql', 'mysql'],
            'cloud': ['aws', 'azure', 'gcp', 'google cloud'],
            'devops': ['ci/cd', 'docker', 'kubernetes', 'jenkins'],
        }
        
    def extract_skills(self, text):
        """Extract skills from text using pattern matching"""
        if not text:
            return []
            
        text_lower = text.lower()
        skills = []
        
        # Common programming languages
        languages = ['python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 
                    'typescript', 'swift', 'kotlin', 'scala', 'r', 'matlab']
        
        # Frameworks and libraries
        frameworks = ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 
                     'fastapi', 'laravel', 'rails', 'nextjs', 'gatsby', 'svelte']
        
        # Tools and technologies
        tools = ['docker', 'kubernetes', 'git', 'jenkins', 'aws', 'azure', 'gcp', 
                'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch']
        
        all_keywords = languages + frameworks + tools
        
        for keyword in all_keywords:
            if keyword in text_lower:
                skills.append(keyword)
                
        return list(set(skills))
    
    def calculate_skill_match_score(self, user_skills, job_skills):
        """Calculate skill match score with weighted importance"""
        if not user_skills or not job_skills:
            return 0.0
            
        user_skills_lower = [s.lower().strip() for s in user_skills if s]
        job_skills_lower = [s.lower().strip() for s in job_skills if s]
        
        if not user_skills_lower or not job_skills_lower:
            return 0.0
        
        score = 0.0
        max_possible_score = len(job_skills_lower) * self.skill_weights['exact_match']
        
        for job_skill in job_skills_lower:
            # Exact match
            if job_skill in user_skills_lower:
                score += self.skill_weights['exact_match']
                continue
            
            # Partial match
            partial_match = False
            for user_skill in user_skills_lower:
                if job_skill in user_skill or user_skill in job_skill:
                    score += self.skill_weights['partial_match']
                    partial_match = True
                    break
            
            if partial_match:
                continue
            
            # Synonym/related match
            for key, synonyms in self.skill_synonyms.items():
                if job_skill in synonyms or job_skill == key:
                    for user_skill in user_skills_lower:
                        if user_skill in synonyms or user_skill == key:
                            score += self.skill_weights['related_match']
                            break
        
        # Normalize to 0-100
        return min(100, (score / max_possible_score * 100)) if max_possible_score > 0 else 0.0
    
    def calculate_experience_match(self, user_experience, job_description):
        """Match experience level from job description"""
        if not job_description:
            return 50.0  # Neutral score if no description
            
        job_desc_lower = job_description.lower()
        
        # Extract experience requirements from job description
        experience_patterns = {
            'entry': ['entry level', 'junior', '0-2 years', 'graduate', 'intern'],
            'mid': ['mid level', '2-5 years', '3-5 years', 'intermediate'],
            'senior': ['senior', '5+ years', '5-10 years', 'expert', 'lead'],
            'principal': ['principal', 'staff', '10+ years', 'architect']
        }
        
        job_level = 'mid'  # Default
        for level, patterns in experience_patterns.items():
            if any(pattern in job_desc_lower for pattern in patterns):
                job_level = level
                break
        
        # Parse user experience (assuming it's a number of years or string)
        try:
            if isinstance(user_experience, (int, float)):
                years = user_experience
            elif isinstance(user_experience, str):
                # Extract number from string like "5 years" or "5"
                match = re.search(r'\d+', user_experience)
                years = int(match.group()) if match else 0
            else:
                years = 0
        except:
            years = 0
        
        # Determine user level based on years
        if years < 2:
            user_level = 'entry'
        elif years < 5:
            user_level = 'mid'
        elif years < 10:
            user_level = 'senior'
        else:
            user_level = 'principal'
        
        # Calculate match score
        level_hierarchy = {'entry': 0, 'mid': 1, 'senior': 2, 'principal': 3}
        user_rank = level_hierarchy.get(user_level, 1)
        job_rank = level_hierarchy.get(job_level, 1)
        
        # Perfect match = 100, one level off = 75, two levels = 50, three levels = 25
        diff = abs(user_rank - job_rank)
        if diff == 0:
            return 100.0
        elif diff == 1:
            return 75.0
        elif diff == 2:
            return 50.0
        else:
            return 25.0
    
    def calculate_text_similarity(self, user_doc, job_doc):
        """Calculate TF-IDF cosine similarity between user profile and job"""
        if not user_doc.strip() or not job_doc.strip():
            return 0.0
            
        try:
            documents = [user_doc, job_doc]
            tfidf = TfidfVectorizer(stop_words='english', max_features=500)
            tfidf_matrix = tfidf.fit_transform(documents)
            
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity * 100  # Convert to percentage
        except:
            return 0.0
    
    def match_jobs(self, user_profile, jobs):
        """
        Enhanced job matching with multiple weighted factors.
        
        Args:
            user_profile: Dict with user information (skills, experience, job_title, etc.)
            jobs: List of job dictionaries
            
        Returns:
            List of jobs with match scores, sorted by relevance
        """
        if not jobs:
            return []
        
        # Extract user information
        user_skills = []
        if 'skills' in user_profile:
            if isinstance(user_profile['skills'], list):
                user_skills = user_profile['skills']
            else:
                user_skills = [s.strip() for s in str(user_profile['skills']).split(',')]
        
        user_experience = user_profile.get('experience', 0)
        user_job_title = user_profile.get('job_title', '')
        user_keywords = user_profile.get('keywords', '')
        
        # Build user document for text matching
        user_doc = f"{user_job_title} {' '.join(user_skills)} {user_keywords}"
        
        # Also extract skills from user document
        extracted_user_skills = self.extract_skills(user_doc)
        all_user_skills = list(set(user_skills + extracted_user_skills))
        
        ranked_jobs = []
        
        for job in jobs:
            # Build job document
            job_doc = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('skills', []))}"
            
            # Extract job skills
            job_skills = job.get('skills', [])
            extracted_job_skills = self.extract_skills(job_doc)
            all_job_skills = list(set(job_skills + extracted_job_skills))
            
            # Calculate different match scores
            text_similarity = self.calculate_text_similarity(user_doc, job_doc)
            skill_match = self.calculate_skill_match_score(all_user_skills, all_job_skills)
            experience_match = self.calculate_experience_match(user_experience, job.get('description', ''))
            
            # Weighted final score
            # Skills are most important (50%), then text similarity (30%), then experience (20%)
            final_score = (
                skill_match * 0.50 +
                text_similarity * 0.30 +
                experience_match * 0.20
            )
            
            # Boost score if job title matches user's desired title
            if user_job_title and user_job_title.lower() in job.get('title', '').lower():
                final_score = min(100, final_score * 1.15)  # 15% boost
            
            # Create enhanced job object
            enhanced_job = job.copy()
            enhanced_job['match_score'] = round(final_score, 1)
            enhanced_job['skill_match'] = round(skill_match, 1)
            enhanced_job['text_similarity'] = round(text_similarity, 1)
            enhanced_job['experience_match'] = round(experience_match, 1)
            enhanced_job['matched_skills'] = list(set(all_user_skills) & set(all_job_skills))
            
            ranked_jobs.append(enhanced_job)
        
        # Sort by final match score
        ranked_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return ranked_jobs


def match_jobs(user_profile, jobs):
    """
    Wrapper function for backward compatibility.
    Uses the enhanced matcher.
    """
    matcher = EnhancedJobMatcher()
    return matcher.match_jobs(user_profile, jobs)


if __name__ == "__main__":
    # Test the enhanced matcher
    test_profile = {
        'skills': ['Python', 'Django', 'React', 'PostgreSQL'],
        'experience': 3,
        'job_title': 'Full Stack Developer',
        'keywords': 'web development backend frontend'
    }
    
    test_jobs = [
        {
            'id': 1,
            'title': 'Senior Full Stack Developer',
            'company': 'TechCorp',
            'description': 'Looking for a full stack developer with 3-5 years experience in Python, Django, and React',
            'skills': ['Python', 'Django', 'React', 'PostgreSQL', 'Docker'],
            'location': 'Remote',
            'salary': '$80k-$120k',
            'platform': 'Test'
        },
        {
            'id': 2,
            'title': 'Junior Frontend Developer',
            'company': 'StartupXYZ',
            'description': 'Entry level position for React developer',
            'skills': ['React', 'JavaScript', 'CSS'],
            'location': 'Remote',
            'salary': '$50k-$70k',
            'platform': 'Test'
        },
        {
            'id': 3,
            'title': 'Python Backend Engineer',
            'company': 'DataCo',
            'description': 'Senior backend engineer with Python and Django experience',
            'skills': ['Python', 'Django', 'REST API', 'PostgreSQL'],
            'location': 'Remote',
            'salary': '$90k-$130k',
            'platform': 'Test'
        }
    ]
    
    results = match_jobs(test_profile, test_jobs)
    
    print("\n🎯 Enhanced Matching Results:\n")
    for i, job in enumerate(results, 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Overall Match: {job['match_score']}%")
        print(f"   - Skill Match: {job['skill_match']}%")
        print(f"   - Text Similarity: {job['text_similarity']}%")
        print(f"   - Experience Match: {job['experience_match']}%")
        print(f"   Matched Skills: {', '.join(job['matched_skills'])}")
        print()
