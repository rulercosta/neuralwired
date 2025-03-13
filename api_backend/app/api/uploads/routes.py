"""
Routes for the uploads API
"""
from flask import jsonify, request
import os
from . import bp
from ...utils.helpers import save_uploaded_image, get_uploaded_files, delete_uploaded_file

# Fix the import to properly use the login_required decorator
from ...api.auth.routes import login_required

@bp.route('/uploads', methods=['POST'])
@login_required
def upload_file():
    """
    Upload a new file
    
    Returns:
        JSON response with the URL of the uploaded file
    """
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file part in the request'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'error': 'No file selected'
        }), 400
    
    file_url = save_uploaded_image(file)
    
    if not file_url:
        return jsonify({
            'error': 'Invalid file type or upload failed'
        }), 400
    
    return jsonify({
        'success': True,
        'url': file_url,
        'filename': os.path.basename(file_url)
    }), 201

@bp.route('/uploads/list', methods=['GET'])
def list_files():
    """
    List all uploaded files
    
    Returns:
        JSON response with a list of all uploaded files
    """
    files = get_uploaded_files()
    
    return jsonify({
        'success': True,
        'files': files,
        'count': len(files)
    })

@bp.route('/uploads/<filename>', methods=['DELETE'])
@login_required
def delete_file(filename):
    """
    Delete an uploaded file
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        JSON response indicating success or failure
    """
    if not delete_uploaded_file(filename):
        return jsonify({
            'error': 'File not found or could not be deleted'
        }), 404
    
    return jsonify({
        'success': True,
        'message': f'File {filename} deleted successfully'
    })
