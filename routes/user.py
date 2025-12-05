from flask import Blueprint, request, jsonify, session
import database as db
import hashlib
import os
import uuid

user_bp = Blueprint('user', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user_id():
    return session.get('user_id')

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    try:
        # Secure: Get ID from session, not query param
        user_id = get_current_user_id()
        
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401
        
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        user.pop('password_hash', None)
        
        return jsonify({"status": "success", "user": user})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401

        data = request.json
        full_name = data.get('full_name')
        email = data.get('email')
        
        success = db.update_user_profile(user_id, full_name, email)
        
        if not success:
            return jsonify({"status": "error", "message": "Email already exists"}), 400
        
        return jsonify({"status": "success", "message": "Profile updated successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@user_bp.route('/change-password', methods=['POST'])
def change_password():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401

        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not all([current_password, new_password]):
            return jsonify({"status": "error", "message": "All fields required"}), 400
        
        user = db.get_user_by_id(user_id)
        
        if not user or user['password_hash'] != hash_password(current_password):
            return jsonify({"status": "error", "message": "Current password incorrect"}), 401
        
        new_password_hash = hash_password(new_password)
        db.update_user_password(user_id, new_password_hash)
        
        return jsonify({"status": "success", "message": "Password changed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@user_bp.route('/upload-photo', methods=['POST'])
def upload_photo():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401

        if 'photo' not in request.files:
            return jsonify({"status": "error", "message": "No photo uploaded"}), 400
        
        photo = request.files['photo']
        
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        filename = photo.filename
        if not filename or '.' not in filename:
            return jsonify({"status": "error", "message": "Invalid file"}), 400
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return jsonify({"status": "error", "message": "Invalid file type"}), 400
        
        # We need to access the app's static folder. 
        # Since we are in a blueprint, we can use current_app or just assume relative path
        from flask import current_app
        uploads_dir = os.path.join(current_app.static_folder, 'uploads', 'profiles')
        os.makedirs(uploads_dir, exist_ok=True)
        
        unique_filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
        filepath = os.path.join(uploads_dir, unique_filename)
        
        photo.save(filepath)
        
        photo_url = f"/uploads/profiles/{unique_filename}"
        db.update_profile_photo(user_id, photo_url)
        
        return jsonify({
            "status": "success",
            "message": "Photo uploaded successfully",
            "photo_url": photo_url
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
