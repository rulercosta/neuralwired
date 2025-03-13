"""
Settings API routes
"""
from flask import jsonify, request, current_app
from app.models.database import get_db
from app.api.auth.routes import api_login_required
from . import bp

def get_all_settings():
    """
    Get all site settings
    
    Returns:
        dict: Dictionary of all settings
    """
    db = get_db()
    settings = db.execute('SELECT key, value FROM settings').fetchall()
    return {setting['key']: setting['value'] for setting in settings}

def get_setting(key, default=None):
    """
    Get a specific setting by key
    
    Args:
        key: Setting key to retrieve
        default: Default value if setting not found
        
    Returns:
        str: Setting value or default if not found
    """
    db = get_db()
    setting = db.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
    if setting:
        return setting['value']
    return default

def update_setting(key, value):
    """
    Update a setting or create if it doesn't exist
    
    Args:
        key: Setting key to update
        value: New setting value
        
    Returns:
        bool: True if successful
    """
    db = get_db()
    # Check if setting exists
    existing = db.execute('SELECT 1 FROM settings WHERE key = ?', (key,)).fetchone()
    
    if existing:
        db.execute('UPDATE settings SET value = ? WHERE key = ?', (value, key))
    else:
        db.execute('INSERT INTO settings (key, value) VALUES (?, ?)', (key, value))
        
    db.commit()
    return True

def delete_setting(key):
    """
    Delete a setting
    
    Args:
        key: Setting key to delete
        
    Returns:
        bool: True if setting was deleted, False if not found
    """
    db = get_db()
    result = db.execute('DELETE FROM settings WHERE key = ?', (key,))
    db.commit()
    
    return result.rowcount > 0

# API Routes
@bp.route('', methods=['GET'])
def api_get_settings():
    """
    Get all settings
    
    Returns:
        JSON response with all settings
    """
    settings = get_all_settings()
    return jsonify(settings)

@bp.route('/<key>', methods=['GET'])
def api_get_setting(key):
    """
    Get a specific setting by key
    
    Args:
        key: Setting key to retrieve
        
    Returns:
        JSON response with setting value
    """
    value = get_setting(key)
    if value is not None:
        return jsonify({key: value})
    return jsonify({"error": "Setting not found"}), 404

@bp.route('', methods=['POST', 'PUT'])
@api_login_required
def api_update_settings():
    """
    Update multiple settings at once
    
    Returns:
        JSON response with update status
    """
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
        
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No settings provided"}), 400
    
    try:
        for key, value in data.items():
            update_setting(key, value)
        
        return jsonify({"success": True, "message": "Settings updated successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating settings: {str(e)}")
        return jsonify({"error": "Failed to update settings"}), 500

@bp.route('/<key>', methods=['PUT'])
@api_login_required
def api_update_setting(key):
    """
    Update a single setting
    
    Args:
        key: Setting key to update
        
    Returns:
        JSON response with update status
    """
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
        
    data = request.get_json()
    
    if not data or 'value' not in data:
        return jsonify({"error": "No value provided"}), 400
    
    value = data['value']
    
    try:
        update_setting(key, value)
        return jsonify({"success": True, "message": f"Setting '{key}' updated successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating setting: {str(e)}")
        return jsonify({"error": f"Failed to update setting '{key}'"}), 500

@bp.route('/<key>', methods=['DELETE'])
@api_login_required
def api_delete_setting(key):
    """
    Delete a setting
    
    Args:
        key: Setting key to delete
        
    Returns:
        JSON response with deletion status
    """
    try:
        success = delete_setting(key)
        if success:
            return jsonify({"success": True, "message": f"Setting '{key}' deleted successfully"}), 200
        return jsonify({"error": "Setting not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting setting: {str(e)}")
        return jsonify({"error": f"Failed to delete setting '{key}'"}), 500
