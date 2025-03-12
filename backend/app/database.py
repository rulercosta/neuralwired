import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DB_PATH = Path(__file__).parent / 'blogger.db'

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        db.execute('''
        CREATE TABLE IF NOT EXISTS admin_credentials (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
        ''')
        
        # Check if admin user exists
        admin = db.execute('SELECT * FROM admin_credentials WHERE username = ?', 
                         ('admin',)).fetchone()
        
        if not admin:
            # Create default admin user if none exists
            db.execute('INSERT INTO admin_credentials (username, password_hash) VALUES (?, ?)',
                      ('admin', generate_password_hash('admin')))
            db.commit()
            
        # Create pages table if it doesn't exist
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
        
        # Check if title column exists in pages table
        cursor = db.execute("PRAGMA table_info(pages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'is_blog' not in columns:
            db.execute('ALTER TABLE pages ADD COLUMN is_blog BOOLEAN DEFAULT 0')
        if 'excerpt' not in columns:
            db.execute('ALTER TABLE pages ADD COLUMN excerpt TEXT')
        if 'featured' not in columns:
            db.execute('ALTER TABLE pages ADD COLUMN featured BOOLEAN DEFAULT 0')
        if 'published_date' not in columns:
            db.execute('ALTER TABLE pages ADD COLUMN published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        
        # Create settings table if it doesn't exist
        db.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')
        
        # Check if introduction exists in settings
        intro = db.execute('SELECT value FROM settings WHERE key = ?', ('introduction',)).fetchone()
        
        if not intro:
            # Create default introduction if none exists
            default_intro = "hi, i am neuralwired! i write about machine learning, deep learning, and other technical topics."
            db.execute('INSERT INTO settings (key, value) VALUES (?, ?)', ('introduction', default_intro))
            db.commit()

def verify_credentials(username, password):
    with get_db() as db:
        user = db.execute('SELECT * FROM admin_credentials WHERE username = ?', 
                         (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            return True
    return False

def change_password(username, new_password):
    with get_db() as db:
        db.execute('UPDATE admin_credentials SET password_hash = ? WHERE username = ?',
                  (generate_password_hash(new_password), username))
        db.commit()

# Functions for page management
def get_all_pages():
    with get_db() as db:
        pages = db.execute('SELECT id, title, slug, created_at, updated_at, is_blog, featured FROM pages ORDER BY updated_at DESC').fetchall()
        return [dict(page) for page in pages]

def get_page_by_slug(slug):
    with get_db() as db:
        page = db.execute('SELECT * FROM pages WHERE slug = ?', (slug,)).fetchone()
        return dict(page) if page else None

def create_page(title, slug, content, is_blog=False, excerpt=None, featured=False):
    with get_db() as db:
        db.execute('INSERT INTO pages (title, slug, content, is_blog, excerpt, featured, published_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (title, slug, content, is_blog, excerpt, featured, datetime.now()))
        db.commit()
        return db.execute('SELECT id FROM pages WHERE slug = ?', (slug,)).fetchone()['id']

def update_page(slug, title, content, is_blog=None, excerpt=None, featured=None):
    with get_db() as db:
        if is_blog is not None:
            db.execute('UPDATE pages SET title = ?, content = ?, is_blog = ?, excerpt = ?, featured = ?, updated_at = CURRENT_TIMESTAMP WHERE slug = ?',
                    (title, content, is_blog, excerpt, featured, slug))
        else:
            # Preserve existing is_blog status if not specified
            db.execute('UPDATE pages SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE slug = ?',
                    (title, content, slug))
        db.commit()

def delete_page(slug):
    with get_db() as db:
        db.execute('DELETE FROM pages WHERE slug = ?', (slug,))
        db.commit()

def slug_exists(slug):
    with get_db() as db:
        result = db.execute('SELECT 1 FROM pages WHERE slug = ?', (slug,)).fetchone()
        return bool(result)

def get_blog_posts(limit=None, featured_only=False):
    with get_db() as db:
        query = 'SELECT * FROM pages WHERE is_blog = 1'
        params = []
        
        if featured_only:
            query += ' AND featured = 1'
            
        query += ' ORDER BY published_date DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
            
        posts = db.execute(query, params).fetchall()
        return [dict(post) for post in posts]

def get_about_page():
    with get_db() as db:
        page = db.execute('SELECT * FROM pages WHERE slug = ?', ('about',)).fetchone()
        return dict(page) if page else None

def set_featured_post(slug, featured=True):
    with get_db() as db:
        db.execute('UPDATE pages SET featured = ? WHERE slug = ?', (featured, slug))
        db.commit()

# Functions for site settings
def get_setting(key):
    with get_db() as db:
        setting = db.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
        return setting['value'] if setting else None

def update_setting(key, value):
    with get_db() as db:
        db.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        db.commit()

def get_site_content():
    return {
        'introduction': get_setting('introduction') or ''
    }
