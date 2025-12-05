from flask import Blueprint, request, jsonify, session
import database as db
import email_utils
import hashlib

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        if not all([email, password]):
            return jsonify({"status": "error", "message": "Email and password required"}), 400
        
        password_hash = hash_password(password)
        user_id = db.create_user(email, password_hash, full_name)
        
        if user_id is None:
            return jsonify({"status": "error", "message": "Email already exists"}), 400
        
        # Set session
        session['user_id'] = user_id
        
        # Send welcome email (non-blocking - don't fail signup if email fails)
        try:
            email_utils.send_welcome_email(email, full_name or 'User')
        except Exception as email_error:
            print(f"Warning: Failed to send welcome email: {email_error}")
        
        return jsonify({
            "status": "success", 
            "message": "Account created successfully",
            "user": {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "profile_photo": None
            }
        }), 200
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({"status": "error", "message": "Email and password required"}), 400
        
        user = db.get_user_by_email(email)
        
        if not user or user['password_hash'] != hash_password(password):
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        
        db.update_last_login(user['id'])
        
        # Set session
        session['user_id'] = user['id']
        
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user['full_name'],
                "profile_photo": user['profile_photo']
            }
        }), 200
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully"})

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    
    user = db.get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({"status": "error", "message": "User not found"}), 404
        
    return jsonify({
        "status": "success",
        "user": {
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name'],
            "profile_photo": user['profile_photo']
        }
    })

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({"status": "error", "message": "Email required"}), 400
        
        user = db.get_user_by_email(email)
        if not user:
            return jsonify({
                "status": "success",
                "message": "If the email exists, a reset link has been sent"
            })
        
        token = db.create_reset_token(email)
        if not token:
            return jsonify({"status": "error", "message": "Failed to generate reset token"}), 500
        
        email_sent = email_utils.send_password_reset_email(email, token, user.get('full_name'))
        
        if email_sent:
            return jsonify({
                "status": "success",
                "message": "Password reset instructions have been sent to your email"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to send email. Please try again later."
            }), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.json
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not all([token, new_password]):
            return jsonify({"status": "error", "message": "Token and new password required"}), 400
        
        user_id = db.verify_reset_token(token)
        
        if not user_id:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 400
        
        new_password_hash = hash_password(new_password)
        db.update_user_password(user_id, new_password_hash)
        db.mark_token_used(token)
        
        return jsonify({"status": "success", "message": "Password reset successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
