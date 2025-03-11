from flask import Flask, render_template, redirect, url_for, flash, request, session, abort
from functools import wraps
import os
import re
from database import (
    init_db, verify_credentials, get_all_pages, get_page_by_slug, 
    create_page, update_page, delete_page, slug_exists, get_blog_posts,
    get_about_page, set_featured_post, get_site_content, update_setting
)
from datetime import datetime

# Initialize app
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.urandom(32),  # Generate random secret key on startup
    ENV='production'  # Default to production
)

# Initialize database
init_db()

# Add context processor to make database functions available to templates
@app.context_processor
def inject_globals():
    return {
        'get_all_pages': get_all_pages,
        'get_blog_posts': get_blog_posts,
        'current_year': datetime.now().year,
        'is_authenticated': 'logged_in' in session
    }

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def slugify(text):
    # Convert to lowercase and replace spaces with hyphens
    text = text.lower().replace(' ', '-')
    # Remove special characters
    text = re.sub(r'[^a-z0-9\-]', '', text)
    # Remove multiple hyphens
    text = re.sub(r'\-+', '-', text)
    # Remove leading/trailing hyphens
    return text.strip('-')

def generate_excerpt(content, max_length=150):
    """Generate an excerpt from HTML content with proper formatting preserved"""
    # Strip HTML tags for text length calculation but maintain paragraph structure
    text_only = re.sub(r'<.*?>', '', content)
    
    # Truncate to maximum length if needed
    if len(text_only) > max_length:
        # Find the last space before max_length
        truncate_at = text_only[:max_length].rfind(' ')
        if truncate_at == -1:  # No space found
            truncate_at = max_length
        
        # Get the corresponding HTML up to this point by counting chars
        char_count = 0
        html_excerpt = ""
        in_tag = False
        tag_buffer = ""
        
        for char in content:
            if char == '<':
                in_tag = True
                tag_buffer = char
                continue
            
            if in_tag:
                tag_buffer += char
                if char == '>':
                    html_excerpt += tag_buffer
                    in_tag = False
                    tag_buffer = ""
                continue
            
            html_excerpt += char
            char_count += 1
            
            if char_count >= truncate_at:
                break
        
        # Ensure we have proper closing tags if needed
        if '</p>' in html_excerpt and html_excerpt.count('<p>') > html_excerpt.count('</p>'):
            html_excerpt += '</p>'
        
        return html_excerpt + '...'
    
    return content

@app.route('/')
def home():
    content = get_site_content()
    featured_posts = get_blog_posts(featured_only=True)
    recent_posts = get_blog_posts(limit=5)
    about_page = get_about_page()
    return render_template('home.html', 
                          content=content, 
                          featured_posts=featured_posts,
                          recent_posts=recent_posts,
                          about_page=about_page,
                          is_authenticated='logged_in' in session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if verify_credentials(username, password):
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/editor')
@login_required
def editor():
    # This route is deprecated, redirect to edit_intro
    return redirect(url_for('edit_intro'))

@app.route('/publish', methods=['POST'])
@login_required
def publish():
    # This route is deprecated, redirect to update_intro
    return redirect(url_for('update_intro'))

# Blog management routes
@app.route('/blog')
def blog_index():
    posts = get_blog_posts()
    return render_template('blog/index.html', posts=posts, is_authenticated='logged_in' in session)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = get_page_by_slug(slug)
    if not post or not post.get('is_blog', False):
        abort(404)
    
    # Get referrer or default to blog index
    referrer = request.referrer
    referrer_url = url_for('blog_index')
    
    # If referrer exists and is from our site, use it
    if referrer:
        # Extract path from the full URL
        parsed_referrer = referrer.split('/', 3)
        if len(parsed_referrer) >= 4:
            path = '/' + parsed_referrer[3]
            
            # Only use referrer if it's not the current page and is from our site
            current_path = url_for('blog_post', slug=slug)
            if path != current_path and path.startswith('/'):
                referrer_url = path
    
    return render_template('blog/post.html', 
                           post=post, 
                           referrer_url=referrer_url,
                           is_authenticated='logged_in' in session)

# Page management routes
@app.route('/pages')
@login_required
def manage_pages():
    pages = get_all_pages()
    return render_template('pages/manage.html', pages=pages)

@app.route('/pages/new', methods=['GET'])
@login_required
def new_page():
    page_type = request.args.get('type', 'page')
    return render_template('pages/editor.html', page=None, page_type=page_type)

@app.route('/pages/create', methods=['POST'])
@login_required
def create_new_page():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '')
    custom_slug = request.form.get('slug', '').strip()
    is_blog = request.form.get('is_blog') == 'on'
    excerpt = request.form.get('excerpt', '').strip()
    featured = request.form.get('featured') == 'on'
    
    if not title:
        flash('Title is required')
        return render_template('pages/editor.html', 
                              page={'title': title, 'content': content, 'slug': custom_slug, 
                                    'is_blog': is_blog, 'excerpt': excerpt, 'featured': featured})
    
    # Generate slug from title if not provided
    slug = custom_slug if custom_slug else slugify(title)
    
    if not slug:
        flash('Invalid slug')
        return render_template('pages/editor.html', 
                              page={'title': title, 'content': content, 'slug': custom_slug, 
                                    'is_blog': is_blog, 'excerpt': excerpt, 'featured': featured})
    
    if slug_exists(slug):
        flash('A page with this slug already exists')
        return render_template('pages/editor.html', 
                              page={'title': title, 'content': content, 'slug': custom_slug, 
                                    'is_blog': is_blog, 'excerpt': excerpt, 'featured': featured})
    
    # Generate excerpt from content if none provided and it's a blog post
    if is_blog and not excerpt:
        excerpt = generate_excerpt(content)
    
    create_page(title, slug, content, is_blog, excerpt, featured)
    flash('Page created successfully!')
    return redirect(url_for('manage_pages'))

@app.route('/pages/<slug>/edit', methods=['GET'])
@login_required
def edit_page(slug):
    page = get_page_by_slug(slug)
    if not page:
        flash('Page not found')
        return redirect(url_for('manage_pages'))
    return render_template('pages/editor.html', page=page)

@app.route('/pages/<slug>/update', methods=['POST'])
@login_required
def update_existing_page(slug):
    page = get_page_by_slug(slug)
    if not page:
        flash('Page not found')
        return redirect(url_for('manage_pages'))
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '')
    is_blog = request.form.get('is_blog') == 'on'
    excerpt = request.form.get('excerpt', '').strip()
    featured = request.form.get('featured') == 'on'
    
    if not title:
        flash('Title is required')
        return render_template('pages/editor.html', 
                              page={'slug': slug, 'title': title, 'content': content, 
                                    'is_blog': is_blog, 'excerpt': excerpt, 'featured': featured})
    
    # Generate excerpt from content if none provided and it's a blog post
    if is_blog and not excerpt:
        excerpt = generate_excerpt(content)
    
    update_page(slug, title, content, is_blog, excerpt, featured)
    flash('Page updated successfully!')
    return redirect(url_for('manage_pages'))

@app.route('/pages/<slug>/delete', methods=['POST'])
@login_required
def delete_existing_page(slug):
    delete_page(slug)
    flash('Page deleted successfully!')
    return redirect(url_for('manage_pages'))

@app.route('/p/<slug>')
def view_page(slug):
    page = get_page_by_slug(slug)
    if not page:
        abort(404)
        
    # Redirect blog posts to the blog post view
    if page.get('is_blog', False):
        return redirect(url_for('blog_post', slug=slug))
        
    return render_template('pages/view.html', page=page, is_authenticated='logged_in' in session)

@app.route('/pages/<slug>/feature', methods=['POST'])
@login_required
def toggle_featured(slug):
    page = get_page_by_slug(slug)
    if not page:
        flash('Page not found')
        return redirect(url_for('manage_pages'))
    
    featured = not page.get('featured', False)
    set_featured_post(slug, featured)
    flash(f"Post {'featured' if featured else 'unfeatured'} successfully!")
    return redirect(url_for('manage_pages'))

@app.route('/edit-intro')
@login_required
def edit_intro():
    content = get_site_content()
    dummy_page = {
        'title': 'Edit Introduction',
        'content': content.get('introduction', ''),
        'is_introduction': True
    }
    return render_template('pages/editor.html', page=dummy_page)

@app.route('/update-intro', methods=['POST'])
@login_required
def update_intro():
    intro_content = request.form.get('content', '')
    update_setting('introduction', intro_content)
    flash('Introduction updated successfully!')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
