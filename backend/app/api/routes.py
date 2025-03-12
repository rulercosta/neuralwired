from flask import jsonify, request, session, current_app
from database import (
    get_all_pages, get_page_by_slug, create_page, update_page, delete_page,
    get_blog_posts, get_site_content, update_setting, verify_credentials, slug_exists
)
from functools import wraps
import re
import os
import uuid
from werkzeug.utils import secure_filename
from .blueprint import api

def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

def slugify(text):
    text = text.lower().replace(' ', '-')
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'\-+', '-', text)
    return text.strip('-')

def generate_excerpt(content, max_length=150):
    if not content.strip():
        return ""
    
    clean_content = content
    for tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        clean_content = re.sub(f'</{tag}>\\s*<{tag}[^>]*>', '\n\n', clean_content)
        clean_content = re.sub(f'</{tag}>', '\n', clean_content)
    
    clean_content = re.sub(r'<br\s*/?>|<br\s[^>]*>', '\n', clean_content)
    clean_content = re.sub(r'<[^>]*>', '', clean_content)
    clean_content = re.sub(r'\s+', ' ', clean_content.strip())
    
    if len(clean_content) > max_length:
        truncate_at = clean_content[:max_length].rfind(' ')
        if truncate_at == -1:
            truncate_at = max_length
        return clean_content[:truncate_at] + '...'
    
    return clean_content

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file):
    if not file:
        return None
        
    if file and allowed_file(file.filename):
        uploads_dir = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        file_path = os.path.join(uploads_dir, unique_filename)
        file.save(file_path)
        
        return f"/static/uploads/{unique_filename}"
    
    return None

# API Routes
@api.route('/pages', methods=['GET'])
def api_get_pages():
    pages = get_all_pages()
    return jsonify(pages)

@api.route('/pages/<slug>', methods=['GET'])
def api_get_page(slug):
    page = get_page_by_slug(slug)
    if page:
        return jsonify(page)
    return jsonify({"error": "Page not found"}), 404

@api.route('/posts', methods=['GET'])
def api_get_posts():
    featured = request.args.get('featured') == 'true'
    limit = request.args.get('limit')
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            limit = None
            
    posts = get_blog_posts(limit=limit, featured_only=featured)
    return jsonify(posts)

@api.route('/content', methods=['GET'])
def api_get_content():
    content = get_site_content()
    return jsonify(content)

@api.route('/login', methods=['POST'])
def api_login():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    username = data.get('username', '')
    password = data.get('password', '')
    
    if verify_credentials(username, password):
        session['logged_in'] = True
        return jsonify({"success": True, "message": "Login successful"})
    
    return jsonify({"error": "Invalid credentials"}), 401

@api.route('/logout', methods=['POST'])
def api_logout():
    session.pop('logged_in', None)
    return jsonify({"success": True, "message": "Logged out successfully"})

@api.route('/check-auth', methods=['GET'])
def api_check_auth():
    is_authenticated = 'logged_in' in session
    return jsonify({"authenticated": is_authenticated})

@api.route('/upload-image', methods=['POST'])
@api_login_required
def api_upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    image_url = save_uploaded_image(file)
    
    if not image_url:
        return jsonify({"error": "Invalid file type"}), 400
    
    return jsonify({"url": image_url})

@api.route('/pages', methods=['POST'])
@api_login_required
def api_create_page():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    title = data.get('title', '').strip()
    content = data.get('content', '')
    custom_slug = data.get('slug', '').strip()
    is_blog = data.get('is_blog', False)
    excerpt = data.get('excerpt', '').strip()
    featured = data.get('featured', False)
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    slug = custom_slug if custom_slug else slugify(title)
    
    if not slug:
        return jsonify({"error": "Invalid slug"}), 400
    
    if slug_exists(slug):
        return jsonify({"error": "A page with this slug already exists"}), 400
    
    if is_blog and not excerpt:
        excerpt = generate_excerpt(content)
    
    page_id = create_page(title, slug, content, is_blog, excerpt, featured)
    return jsonify({"success": True, "message": "Page created", "id": page_id, "slug": slug}), 201

@api.route('/pages/<slug>', methods=['PUT'])
@api_login_required
def api_update_page(slug):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    page = get_page_by_slug(slug)
    if not page:
        return jsonify({"error": "Page not found"}), 404
        
    title = data.get('title', '').strip()
    content = data.get('content', '')
    is_blog = data.get('is_blog', page.get('is_blog', False))
    excerpt = data.get('excerpt', '').strip()
    featured = data.get('featured', page.get('featured', False))
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    if is_blog and not excerpt:
        excerpt = generate_excerpt(content)
    
    update_page(slug, title, content, is_blog, excerpt, featured)
    return jsonify({"success": True, "message": "Page updated", "slug": slug})

@api.route('/pages/<slug>', methods=['DELETE'])
@api_login_required
def api_delete_page(slug):
    page = get_page_by_slug(slug)
    if not page:
        return jsonify({"error": "Page not found"}), 404
        
    delete_page(slug)
    return jsonify({"success": True, "message": "Page deleted"})

@api.route('/content/intro', methods=['PUT'])
@api_login_required
def api_update_intro():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    content = data.get('content', '')
    update_setting('introduction', content)
    return jsonify({"success": True, "message": "Introduction updated"})

@api.after_request
def add_cache_control(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
