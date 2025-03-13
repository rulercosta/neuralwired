"""
Uploads API routes
"""
from flask import jsonify, request, current_app
from app.utils.helpers import allowed_file, save_uploaded_image, get_uploaded_files, delete_uploaded_file
from app.api.auth.routes import login_required
from . import bp

@bp.route('/uploads', methods=['POST'])
@login_required
def upload_file():
    """
    Upload a file
    
    Returns:
        JSON response with the URL of the uploaded file
    """
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        file_url = save_uploaded_image(file)
        
        if file_url:
            return jsonify({"url": file_url}), 201
        else:
            return jsonify({"error": "Failed to save file"}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

@bp.route('/uploads/list', methods=['GET'])
def list_files():
    """
    List all uploaded files
    
    Returns:
        JSON response with list of files
    """
    try:
        files = get_uploaded_files()
        return jsonify(files)
    except Exception as e:
        current_app.logger.error(f"Error listing uploads: {str(e)}")
        return jsonify({"error": "Failed to list uploads"}), 500

@bp.route('/uploads/<filename>', methods=['DELETE'])
@login_required
def delete_file(filename):
    """
    Delete an uploaded file
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        JSON response with deletion status
    """
    try:
        if delete_uploaded_file(filename):
            return jsonify({"success": True, "message": "File deleted successfully"}), 200
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting file: {str(e)}")
        return jsonify({"error": "Failed to delete file"}), 500
