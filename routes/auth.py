from flask import Blueprint, request, jsonify, session
import database as db
import hashlib

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Create a new user account - simplified with no email dependencies"""
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        # Validate required fields
        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password required"}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user in database
        user_id = db.create_user(email, password_hash, full_name)
        
        if user_id is None:
            return jsonify({"status": "error", "message": "Email already exists"}), 400
        
        # Set session
        session['user_id'] = user_id
        
        # Return success response
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
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Failed to create account"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and create session"""
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        # Validate required fields
        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password required"}), 400
        
        # Get user from database
        user = db.get_user_by_email(email)
        
        # Check credentials
        if not user or user['password_hash'] != hash_password(password):
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        
        # Update last login
        db.update_last_login(user['id'])
        
        # Set session
        session['user_id'] = user['id']
        
        # Return success response
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user['full_name'],
                "profile_photo": user.get('profile_photo')
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Failed to login"}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Clear user session"""
    try:
        session.clear()
        return jsonify({"status": "success", "message": "Logged out successfully"}), 200
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to logout"}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user"""
    try:
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
                "profile_photo": user.get('profile_photo')
            }
        }), 200
        
    except Exception as e:
        print(f"Get current user error: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to get user"}), 500
