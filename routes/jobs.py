from flask import Blueprint, request, jsonify, session, send_file
import database as db
import os
from werkzeug.utils import secure_filename
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime
from cv_parser import CVParser

# Import scrapers/matchers - prioritize production scraper
try:
    from scraper_production import scrape_jobs
    print("✓ Using production scraper with validation")
except ImportError:
    try:
        from scraper_enhanced import scrape_jobs
        print("⚠ Using enhanced scraper (no validation)")
    except ImportError:
        from scraper import scrape_jobs
        print("⚠ Using basic scraper")

try:
    from matcher_enhanced import match_jobs
except ImportError:
    from matcher import match_jobs

jobs_bp = Blueprint('jobs', __name__)

def get_current_user_id():
    return session.get('user_id')

@jobs_bp.route('/recommend/form', methods=['POST'])
def recommend_form():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401

        data = request.json
        jobs = scrape_jobs(data.get('job_title', ''), data.get('location', ''))
        matched_jobs = match_jobs(data, jobs)
        
        keywords = ', '.join(data.get('skills', [])) if isinstance(data.get('skills'), list) else data.get('skills', '')
        search_id = db.save_search(user_id, 'form', data, keywords)
        db.save_job_results(search_id, matched_jobs)
        
        return jsonify({"status": "success", "jobs": matched_jobs, "search_id": search_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@jobs_bp.route('/recommend/chat', methods=['POST'])
def recommend_chat():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401

        data = request.json
        user_message = data.get('message', '')
        
        jobs = scrape_jobs(user_message, "")
        matched_jobs = match_jobs({"keywords": user_message}, jobs)
        
        search_id = db.save_search(user_id, 'chat', {'message': user_message}, user_message[:100])
        db.save_job_results(search_id, matched_jobs)
        
        return jsonify({"status": "success", "jobs": matched_jobs, "search_id": search_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@jobs_bp.route('/recommend/cv', methods=['POST'])
def recommend_cv():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401

        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file uploaded"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
            
        filename = secure_filename(file.filename)
        temp_path = os.path.join("temp_uploads", filename)
        os.makedirs("temp_uploads", exist_ok=True)
        file.save(temp_path)
        
        try:
            parser = CVParser()
            parsed_data = parser.parse(temp_path)
            
            if "error" in parsed_data:
                return jsonify({"status": "error", "message": parsed_data["error"]}), 400
                
            extracted_skills = parsed_data.get("skills", [])
            job_title = parsed_data.get("job_title", "Unknown")
            
            search_query = job_title if job_title != "Unknown" else "Software Engineer"
            if not search_query and extracted_skills:
                search_query = extracted_skills[0]
                
            jobs = scrape_jobs(search_query, "")
            
            user_profile = {
                "skills": extracted_skills,
                "job_title": job_title
            }
            matched_jobs = match_jobs(user_profile, jobs)
            
            skills_str = ", ".join(extracted_skills) if extracted_skills else ""
            
            search_id = db.save_search(user_id, 'cv', {'filename': filename, 'parsed_data': parsed_data}, skills_str)
            db.save_job_results(search_id, matched_jobs)
            
            return jsonify({
                "status": "success", 
                "jobs": matched_jobs, 
                "search_id": search_id,
                "parsed_data": parsed_data
            })
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@jobs_bp.route('/user/searches', methods=['GET'])
def get_searches():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401
        
        searches = db.get_user_searches(user_id)
        return jsonify({"status": "success", "searches": searches})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@jobs_bp.route('/search/<int:search_id>/results', methods=['GET'])
def get_search_results_api(search_id):
    try:
        # Ideally check if search belongs to user, but for now just return results
        results = db.get_search_results(search_id)
        return jsonify({"status": "success", "jobs": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@jobs_bp.route('/user/save-job', methods=['POST'])
def save_job_endpoint():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401

        data = request.json
        job_result_id = data.get('job_result_id')
        notes = data.get('notes', '')
        
        if not job_result_id:
            return jsonify({"status": "error", "message": "Job ID required"}), 400
        
        saved_id = db.save_job(user_id, int(job_result_id), notes)
        
        if saved_id is None:
            return jsonify({"status": "error", "message": "Job already saved"}), 400
        
        return jsonify({"status": "success", "message": "Job saved successfully", "saved_id": saved_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@jobs_bp.route('/user/saved-jobs', methods=['GET'])
def get_saved_jobs_endpoint():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401
        
        saved_jobs = db.get_saved_jobs(user_id)
        return jsonify({"status": "success", "jobs": saved_jobs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@jobs_bp.route('/user/saved-job/<int:saved_id>', methods=['DELETE'])
def unsave_job_endpoint(saved_id):
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401
        
        db.unsave_job(user_id, saved_id)
        return jsonify({"status": "success", "message": "Job removed from saved"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@jobs_bp.route('/export/pdf', methods=['POST'])
def export_pdf():
    try:
        data = request.json
        jobs = data.get('jobs', [])
        user_name = data.get('user_name', 'User')
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=30,
        )
        elements.append(Paragraph(f"Job Recommendations for {user_name}", title_style))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        for idx, job in enumerate(jobs, 1):
            job_title_style = ParagraphStyle(
                'JobTitle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1e293b'),
                spaceAfter=10,
            )
            elements.append(Paragraph(f"{idx}. {job.get('title', 'N/A')}", job_title_style))
            
            job_data = [
                ['Company:', job.get('company', 'N/A')],
                ['Location:', job.get('location', 'N/A')],
                ['Match Score:', f"{job.get('match_score', 0)}%"],
                ['Platform:', job.get('platform', 'N/A')],
            ]
            
            job_table = Table(job_data, colWidths=[1.5*inch, 4.5*inch])
            job_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(job_table)
            elements.append(Spacer(1, 0.1*inch))
            
            desc = job.get('description', 'No description available')[:300] + '...'
            elements.append(Paragraph(f"<b>Description:</b> {desc}", styles['Normal']))
            
            skills = job.get('skills', [])
            if skills:
                skills_text = ', '.join(skills[:10])
                elements.append(Paragraph(f"<b>Skills:</b> {skills_text}", styles['Normal']))
            
            elements.append(Spacer(1, 0.3*inch))
        
        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'job_recommendations_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
