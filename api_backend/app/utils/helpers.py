"""
Helper functions for the application
"""
import re
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def slugify(text):
    """
    Create a URL-friendly slug from the given text
    
    Args:
        text: Text to slugify
        
    Returns:
        str: URL-friendly slug
    """
    text = text.lower().replace(' ', '-')
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'\-+', '-', text)
    return text.strip('-')

def generate_excerpt(content, max_length=150):
    """
    Generate an excerpt from content
    
    Args:
        content: Content to generate excerpt from
        max_length: Maximum length of excerpt
        
    Returns:
        str: Generated excerpt
    """
    # Strip HTML tags
    plain_text = re.sub(r'<[^>]*>', '', content)
    
    # Truncate to max_length
    if len(plain_text) > max_length:
        return plain_text[:max_length].rsplit(' ', 1)[0] + '...'
    return plain_text

def allowed_file(filename):
    """
    Check if file has an allowed extension
    
    Args:
        filename: Name of file to check
        
    Returns:
        bool: True if file has allowed extension, False otherwise
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file):
    """
    Save uploaded image to filesystem
    
    Args:
        file: File object to save
        
    Returns:
        str: URL path to saved file
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Use UUID to prevent filename collisions
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Ensure upload directory exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Return the URL path that can be used to access the file
        return f"/static/uploads/{unique_filename}"
    
    return None

def get_uploaded_files():
    """
    List all uploaded files in the uploads directory
    
    Returns:
        list: List of dictionaries containing file information
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # Ensure upload directory exists
    os.makedirs(upload_folder, exist_ok=True)
    
    files = []
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            # Get file stats
            stats = os.stat(file_path)
            files.append({
                'filename': filename,
                'url': f"/static/uploads/{filename}",
                'size': stats.st_size,
                'created': stats.st_mtime
            })
    
    return files

def delete_uploaded_file(filename):
    """
    Delete an uploaded file from the filesystem
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    if not filename or '..' in filename:  # Basic path traversal protection
        return False
        
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        return True
    
    return False
