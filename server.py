from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import database as db
from routes.auth import auth_bp
from routes.user import user_bp
from routes.jobs import jobs_bp

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded environment variables")
except ImportError:
    print("⚠ python-dotenv not installed, using system env or defaults")

app = Flask(__name__, static_folder='src')

# Configuration
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key_123')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production (HTTPS)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# CORS - Allow credentials for cookies
CORS(app, supports_credentials=True)

# Initialize database
db.init_database()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(jobs_bp, url_prefix='/api') # Jobs routes were mixed, some /api/recommend, some /api/user/searches

# Serve static files (Frontend)
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    print("Starting Neuronix AI JobFlow Server...")
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
