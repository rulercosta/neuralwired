"""
Database module for the application
"""
import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

def get_db():
    """
    Get a database connection, creating it if necessary
    
    Returns:
        SQLite database connection
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    """
    Close the database connection if it exists
    
    Args:
        e: Exception that triggered the close (optional)
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with schema and default data"""
    db = get_db()
    
    # Create tables
    db.execute('''
    CREATE TABLE IF NOT EXISTS admin_credentials (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL
    )
    ''')
    
    # Create pages table
    db.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_blog BOOLEAN DEFAULT 0,
        excerpt TEXT,
        featured BOOLEAN DEFAULT 0,
        published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create settings table
    db.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    ''')
    
    # Create uploads table to track uploaded files
    db.execute('''
    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL UNIQUE,
        original_filename TEXT NOT NULL,
        path TEXT NOT NULL,
        url TEXT NOT NULL,
        size INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Check if admin user exists
    admin = db.execute('SELECT * FROM admin_credentials WHERE username = ?', 
                     ('admin',)).fetchone()
    
    if not admin:
        # Create default admin user if none exists
        db.execute('INSERT INTO admin_credentials (username, password_hash) VALUES (?, ?)',
                  ('admin', generate_password_hash('admin')))
    
    # Check if introduction setting exists
    intro = db.execute('SELECT * FROM settings WHERE key = ?',
                     ('introduction',)).fetchone()
    
    if not intro:
        # Create default introduction if none exists
        default_intro = "hi, i am neuralwired! i write about machine learning, deep learning, and other technical topics."
        db.execute('INSERT INTO settings (key, value) VALUES (?, ?)', 
                 ('introduction', default_intro))
    
    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create new tables and initialize with default data"""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """
    Register database functions with the Flask app
    
    Args:
        app: Flask application instance
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    
    # Initialize the database when the app starts
    with app.app_context():
        init_db()
