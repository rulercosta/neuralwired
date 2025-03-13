"""
Configuration module for the application
"""
import os

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
    DEBUG = False
    TESTING = False
    DATABASE = os.path.join(BASE_DIR, 'instance', 'blogger.sqlite')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'instance', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    CORS_ORIGINS = ['*']  # In production, specify allowed origins

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE = ':memory:'
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'production'
    # In production, you should set more restrictive CORS settings
    CORS_ORIGINS = ['https://yourdomain.com', 'https://www.yourdomain.com']

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
