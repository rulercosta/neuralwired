from flask import Flask, render_template, session, request, jsonify, redirect, send_from_directory
import os
from database import init_db, verify_credentials
from api import api

# Get project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')

# Initialize app with frontend paths
app = Flask(__name__,
           template_folder=os.path.join(FRONTEND_DIR, 'public'),
           static_folder=os.path.join(FRONTEND_DIR, 'src'),
           static_url_path='/static')

# Additional static folder for components
app.additional_static_folder = os.path.join(FRONTEND_DIR, 'src', 'js', 'components')

# Add rule to serve from components directory
@app.route('/static/js/components/<path:filename>')
def serve_component(filename):
    """Serve component files"""
    return send_from_directory(app.additional_static_folder, filename)

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(32)),  # Use env var if available
    ENV=os.environ.get('FLASK_ENV', 'production'),  # Default to production
    UPLOAD_FOLDER=os.path.join(app.static_folder, 'uploads'),  # Add upload folder config
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max upload size
)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()

# Register API blueprint
app.register_blueprint(api, url_prefix='/api')

# Base route - serves the SPA shell
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Serve the single page app for all routes"""
    return render_template('index.html')

# Serve uploaded files (for development)
@app.route('/static/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Server-side login support (optional, can be handled by API too)
@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        # API already handles JSON login
        return jsonify({"error": "Use API endpoint for JSON login"}), 400
        
    # Handle form-based login for non-JS fallback
    username = request.form.get('username')
    password = request.form.get('password')
    
    if verify_credentials(username, password):
        session['logged_in'] = True
        return redirect('/')
    
    return redirect('/login')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    return redirect('/')

# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Set proper cache headers for static assets
    if request.path.startswith('/static/'):
        if request.path.startswith('/static/js/') or request.path.startswith('/static/css/'):
            # Cache JS and CSS for 1 week
            response.headers['Cache-Control'] = 'public, max-age=604800'
        elif request.path.startswith('/static/uploads/'):
            # Cache uploaded images for 1 month
            response.headers['Cache-Control'] = 'public, max-age=2592000'
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
