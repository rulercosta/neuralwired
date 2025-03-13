"""
Routes for authentication API
"""
from flask import request, jsonify, session
from functools import wraps
from . import bp
from ...models.database import get_db
from werkzeug.security import check_password_hash

def login_required(view):
    """
    Decorator to ensure a user is logged in
    
    Args:
        view: The view function to protect
        
    Returns:
        Decorated function that checks for authentication
    """
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return view(*args, **kwargs)
    return wrapped_view

@bp.route('/auth/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    Returns:
        JSON response indicating success or failure
    """
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM admin_credentials WHERE username = ?', 
            (username,)
        ).fetchone()
        
        if user is None or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        session.clear()
        session['user_id'] = user['username']
        
        return jsonify({'success': True, 'message': 'Login successful'}), 200

@bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    User logout endpoint
    
    Returns:
        JSON response indicating success
    """
    session.clear()
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

@bp.route('/auth/status', methods=['GET'])
def auth_status():
    """
    Check authentication status
    
    Returns:
        JSON response with authentication status
    """
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': session['user_id']
        }), 200
    
    return jsonify({'authenticated': False}), 200
