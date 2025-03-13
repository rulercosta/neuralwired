"""
Application factory module
"""
import os
from flask import Flask
from flask_cors import CORS
from .config import config

def create_app(config_name='default'):
    """
    Create and configure the Flask application
    
    Args:
        config_name: Name of the configuration to use
        
    Returns:
        Flask application instance
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Set up CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Register database functions
    from .models.database import init_app
    init_app(app)
    
    # Register API blueprints
    from .api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    
    from .api.pages import bp as pages_bp
    app.register_blueprint(pages_bp, url_prefix='/api')
    
    from .api.settings import bp as settings_bp
    app.register_blueprint(settings_bp, url_prefix='/api')
    
    from .api.uploads import bp as uploads_bp
    app.register_blueprint(uploads_bp, url_prefix='/api')
    
    # Register static folder for uploads
    @app.route('/static/uploads/<path:filename>')
    def serve_uploads(filename):
        return app.send_static_file(os.path.join('uploads', filename))
    
    # Add a health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'ok'}, 200
    
    return app
