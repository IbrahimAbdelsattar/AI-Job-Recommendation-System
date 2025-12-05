from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def match_jobs(user_profile, jobs):
    """
    Matches user profile against a list of jobs using TF-IDF and Cosine Similarity.
    """
    if not jobs:
        return []
        
    # 1. Prepare Job Documents
    job_docs = []
    for job in jobs:
        # Combine title, description and skills into a single string for matching
        doc = f"{job['title']} {job['description']} {' '.join(job['skills'])}"
        job_docs.append(doc)
        
    # 2. Prepare User Document
    user_doc = ""
    if 'skills' in user_profile:
        if isinstance(user_profile['skills'], list):
            user_doc += " ".join(user_profile['skills'])
        else:
            user_doc += str(user_profile['skills'])
            
    if 'job_title' in user_profile:
        user_doc += " " + user_profile['job_title']
        
    if 'keywords' in user_profile: # From chat
        user_doc += " " + user_profile['keywords']

    if not user_doc.strip():
        # If no user info, just return jobs as is
        return jobs

    # 3. Vectorization
    documents = [user_doc] + job_docs
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(documents)
    
    # 4. Calculate Similarity
    # user_vector is at index 0
    user_vector = tfidf_matrix[0:1]
    # job_vectors are from index 1 onwards
    job_vectors = tfidf_matrix[1:]
    
    similarity_scores = cosine_similarity(user_vector, job_vectors).flatten()
    
    # 5. Rank Jobs
    ranked_jobs = []
    for i, score in enumerate(similarity_scores):
        job = jobs[i].copy()
        job['match_score'] = round(score * 100, 1) # Convert to percentage
        ranked_jobs.append(job)
        
    # Sort by score descending
    ranked_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    
    return ranked_jobs
