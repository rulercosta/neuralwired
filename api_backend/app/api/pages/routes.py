"""
Pages API routes
"""
from flask import jsonify, request, current_app
from app.models.database import get_db
# Fix this import to use the correct login_required function
from app.api.auth.routes import login_required
from app.utils.helpers import slugify, generate_excerpt
from . import bp
import datetime

def get_all_pages():
    """
    Get all pages from database
    
    Returns:
        list: List of page dictionaries
    """
    db = get_db()
    pages = db.execute('SELECT * FROM pages WHERE is_blog = 0 ORDER BY title ASC').fetchall()
    return [dict(page) for page in pages]

def get_blog_posts(limit=None, featured=False):
    """
    Get blog posts from database
    
    Args:
        limit: Maximum number of posts to return (optional)
        featured: Whether to only return featured posts (optional)
        
    Returns:
        list: List of blog post dictionaries
    """
    db = get_db()
    query = 'SELECT * FROM pages WHERE is_blog = 1'
    params = []
    
    if featured:
        query += ' AND featured = 1'
        
    query += ' ORDER BY published_date DESC'
    
    if limit:
        query += ' LIMIT ?'
        params.append(limit)
        
    posts = db.execute(query, params).fetchall()
    return [dict(post) for post in posts]

def get_page_by_slug(slug):
    """
    Get page by slug
    
    Args:
        slug: Page slug to search for
        
    Returns:
        dict: Page dictionary or None if not found
    """
    db = get_db()
    page = db.execute('SELECT * FROM pages WHERE slug = ?', (slug,)).fetchone()
    return dict(page) if page else None

def create_page(title, content, is_blog=False, featured=False, excerpt=None):
    """
    Create a new page
    
    Args:
        title: Page title
        content: Page content
        is_blog: Whether page is a blog post (optional)
        featured: Whether blog post is featured (optional)
        excerpt: Custom excerpt (optional)
        
    Returns:
        dict: Created page dictionary
    """
    db = get_db()
    slug = slugify(title)
    
    # Ensure slug is unique
    base_slug = slug
    counter = 1
    while db.execute('SELECT 1 FROM pages WHERE slug = ?', (slug,)).fetchone():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Generate excerpt if not provided
    if not excerpt and is_blog:
        excerpt = generate_excerpt(content)
        
    now = datetime.datetime.now().isoformat()
    
    db.execute(
        '''INSERT INTO pages 
           (title, slug, content, is_blog, excerpt, featured, created_at, updated_at, published_date) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (title, slug, content, is_blog, excerpt, featured, now, now, now)
    )
    db.commit()
    
    return get_page_by_slug(slug)

def update_page(slug, title=None, content=None, is_blog=None, featured=None, excerpt=None):
    """
    Update an existing page
    
    Args:
        slug: Page slug to update
        title: New title (optional)
        content: New content (optional)
        is_blog: Whether page is a blog post (optional)
        featured: Whether blog post is featured (optional)
        excerpt: Custom excerpt (optional)
        
    Returns:
        dict: Updated page dictionary or None if not found
    """
    db = get_db()
    page = db.execute('SELECT * FROM pages WHERE slug = ?', (slug,)).fetchone()
    
    if not page:
        return None
        
    # Prepare update fields
    updates = []
    params = []
    
    if title is not None:
        updates.append('title = ?')
        params.append(title)
        
        # If title changed, update slug too
        new_slug = slugify(title)
        if new_slug != slug:
            updates.append('slug = ?')
            params.append(new_slug)
            slug = new_slug
    
    if content is not None:
        updates.append('content = ?')
        params.append(content)
        
        # Update excerpt if this is a blog post and no custom excerpt provided
        if is_blog and excerpt is None:
            updates.append('excerpt = ?')
            params.append(generate_excerpt(content))
    
    if is_blog is not None:
        updates.append('is_blog = ?')
        params.append(is_blog)
        
    if featured is not None:
        updates.append('featured = ?')
        params.append(featured)
        
    if excerpt is not None:
        updates.append('excerpt = ?')
        params.append(excerpt)
        
    # Always update the updated_at timestamp
    updates.append('updated_at = ?')
    params.append(datetime.datetime.now().isoformat())
    
    # Add slug to params for WHERE clause
    params.append(slug)
    
    # Execute update
    if updates:
        query = f"UPDATE pages SET {', '.join(updates)} WHERE slug = ?"
        db.execute(query, params)
        db.commit()
    
    return get_page_by_slug(slug)

def delete_page(slug):
    """
    Delete a page
    
    Args:
        slug: Page slug to delete
        
    Returns:
        bool: True if page was deleted, False otherwise
    """
    db = get_db()
    page = db.execute('SELECT 1 FROM pages WHERE slug = ?', (slug,)).fetchone()
    
    if not page:
        return False
        
    db.execute('DELETE FROM pages WHERE slug = ?', (slug,))
    db.commit()
    return True

# API Routes
@bp.route('', methods=['GET'])
def api_get_pages():
    """
    Get all pages or blog posts
    
    Returns:
        JSON response with pages or posts
    """
    is_blog = request.args.get('type') == 'blog'
    featured = request.args.get('featured') == 'true'
    limit = request.args.get('limit')
    
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            limit = None
    
    if is_blog:
        posts = get_blog_posts(limit=limit, featured=featured)
        return jsonify(posts)
    else:
        pages = get_all_pages()
        return jsonify(pages)

@bp.route('/<slug>', methods=['GET'])
def api_get_page(slug):
    """
    Get a specific page by slug
    
    Args:
        slug: Page slug to retrieve
        
    Returns:
        JSON response with page data
    """
    page = get_page_by_slug(slug)
    
    if page:
        return jsonify(page)
    else:
        return jsonify({"error": "Page not found"}), 404

@bp.route('', methods=['POST'])
@login_required
def api_create_page():
    """
    Create a new page
    
    Returns:
        JSON response with created page data
    """
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
        
    data = request.get_json()
    
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Missing required fields"}), 400
        
    title = data['title']
    content = data['content']
    is_blog = data.get('is_blog', False)
    featured = data.get('featured', False)
    excerpt = data.get('excerpt')
    
    try:
        page = create_page(title, content, is_blog, featured, excerpt)
        return jsonify(page), 201
    except Exception as e:
        current_app.logger.error(f"Error creating page: {str(e)}")
        return jsonify({"error": "Failed to create page"}), 500

@bp.route('/<slug>', methods=['PUT', 'PATCH'])
@login_required
def api_update_page(slug):
    """
    Update an existing page
    
    Args:
        slug: Page slug to update
        
    Returns:
        JSON response with updated page data
    """
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
        
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No update data provided"}), 400
    
    title = data.get('title')
    content = data.get('content')
    is_blog = data.get('is_blog')
    featured = data.get('featured')
    excerpt = data.get('excerpt')
    
    try:
        page = update_page(slug, title, content, is_blog, featured, excerpt)
        if page:
            return jsonify(page)
        else:
            return jsonify({"error": "Page not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error updating page: {str(e)}")
        return jsonify({"error": "Failed to update page"}), 500

@bp.route('/<slug>', methods=['DELETE'])
@login_required
def api_delete_page(slug):
    """
    Delete a page
    
    Args:
        slug: Page slug to delete
        
    Returns:
        JSON response with deletion status
    """
    try:
        success = delete_page(slug)
        if success:
            return jsonify({"success": True, "message": "Page deleted successfully"}), 200
        else:
            return jsonify({"error": "Page not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting page: {str(e)}")
        return jsonify({"error": "Failed to delete page"}), 500
