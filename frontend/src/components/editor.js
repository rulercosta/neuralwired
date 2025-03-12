/**
 * Editor Component
 * Rich text editor for creating and editing content
 */
class EditorComponent {
    constructor() {
        this.page = null;
        this.isEditingIntro = false;
        this.mode = 'create'; // 'create', 'edit', 'editIntro'
        this.pageType = 'page'; // 'page' or 'blog'
    }

    async fetchData(slug) {
        // Special case for editing the introduction
        if (slug === 'introduction') {
            try {
                const content = await api.getSiteContent();
                this.page = {
                    title: 'Edit Introduction',
                    content: content.introduction || '',
                    isIntroduction: true
                };
                this.mode = 'editIntro';
            } catch (error) {
                console.error('Error fetching introduction:', error);
                this.page = null;
            }
            return;
        }

        // If no slug provided, we're creating a new page
        if (!slug) {
            this.page = {
                title: '',
                content: '',
                is_blog: false,
                excerpt: '',
                featured: false
            };
            this.mode = 'create';
            return;
        }

        // Otherwise, load existing page for editing
        try {
            this.page = await api.getPageBySlug(slug);
            this.mode = 'edit';
        } catch (error) {
            console.error(`Error fetching page with slug "${slug}":`, error);
            this.page = null;
        }
    }

    render() {
        if (!this.page) {
            return '<div class="loading">Loading...</div>';
        }

        // Return the appropriate form based on mode
        if (this.mode === 'editIntro') {
            return this.renderIntroEditor();
        } else {
            return this.renderPageEditor();
        }
    }

    renderIntroEditor() {
        return `
        <header>
            <h1>Edit Introduction</h1>
            <div class="site-nav page-nav">
                <ul>
                    <li><a href="/">← back to home</a></li>
                </ul>
            </div>
        </header>

        <form id="intro-editor-form" class="editor-form" autocomplete="off">
            <div class="form-group">
                <label for="intro-content-editor">Introduction Content:</label>
                <div class="editor-toolbar" aria-controls="intro-content-editor">
                    <button type="button" class="toolbar-btn" data-command="bold"><i class="fas fa-bold"></i></button>
                    <button type="button" class="toolbar-btn" data-command="italic"><i class="fas fa-italic"></i></button>
                    <button type="button" class="toolbar-btn" data-command="underline"><i class="fas fa-underline"></i></button>
                    <span class="toolbar-divider"></span>
                    <button type="button" class="toolbar-btn" data-command="justifyLeft"><i class="fas fa-align-left"></i></button>
                    <button type="button" class="toolbar-btn" data-command="justifyCenter"><i class="fas fa-align-center"></i></button>
                    <button type="button" class="toolbar-btn" data-command="justifyRight"><i class="fas fa-align-right"></i></button>
                    <span class="toolbar-divider"></span>
                    <button type="button" class="toolbar-btn" data-command="createLink"><i class="fas fa-link"></i></button>
                    <span class="toolbar-divider"></span>
                    <select class="toolbar-select" data-command="fontSize" aria-label="Font size">
                        <option value="1">Small</option>
                        <option value="3" selected>Normal</option>
                        <option value="5">Large</option>
                        <option value="7">X-Large</option>
                    </select>
                </div>
                <div id="intro-content-editor" class="content-editor" contenteditable="true" data-form-type="other">${this.page.content}</div>
                <textarea name="content" id="intro-content-textarea" style="display: none;" autocomplete="off">${this.page.content}</textarea>
            </div>
            
            <div class="form-actions">
                <button type="submit" class="btn-primary">Save Introduction</button>
                <button type="button" class="btn-secondary" id="cancel-btn">Cancel</button>
            </div>
        </form>`;
    }

    renderPageEditor() {
        return `
        <header>
            <h1>${this.mode === 'edit' ? 'Edit Page' : 'Create New Page'}</h1>
            <div class="site-nav page-nav">
                <ul>
                    <li><a href="/manage">← back to page management</a></li>
                </ul>
            </div>
        </header>

        <form id="page-editor-form" class="editor-form" autocomplete="off">
            <!-- Hidden field to prevent autofill -->
            <input type="text" style="display:none" aria-hidden="true">
            <input type="password" style="display:none" aria-hidden="true">
            
            <div class="form-group">
                <label for="title-input">Title:</label>
                <input type="text" id="title-input" name="title" value="${this.page.title || ''}" required class="full-width-input" autocomplete="off" data-form-type="other">
            </div>
            
            ${this.mode === 'create' ? `
            <div class="form-group">
                <label for="slug-input">Slug (optional):</label>
                <input type="text" id="slug-input" name="slug" value="${this.page.slug || ''}" class="full-width-input" autocomplete="off" data-form-type="other">
                <small class="input-help">If left blank, a slug will be generated from the title.</small>
            </div>
            ` : ''}
            
            <div class="form-group editor-options">
                <div class="checkbox-group">
                    <input type="checkbox" id="is_blog" name="is_blog" ${this.page.is_blog ? 'checked' : ''} autocomplete="off">
                    <label for="is_blog">This is a blog post</label>
                </div>
                
                <div class="checkbox-group blog-option" ${!this.page.is_blog ? 'style="display: none;"' : ''}>
                    <input type="checkbox" id="featured" name="featured" ${this.page.featured ? 'checked' : ''} autocomplete="off">
                    <label for="featured">Featured post</label>
                    <small class="input-help">Featured posts appear in the featured section on the homepage</small>
                </div>
            </div>
            
            <div class="form-group blog-option" ${!this.page.is_blog ? 'style="display: none;"' : ''}>
                <label for="excerpt-editor">Excerpt (optional):</label>
                <div id="excerpt-editor" class="content-editor excerpt-editor" contenteditable="true" data-form-type="other">${this.page.excerpt || ''}</div>
                <textarea id="excerpt" name="excerpt" style="display: none;" autocomplete="off">${this.page.excerpt || ''}</textarea>
                <small class="input-help">A short summary of the post. If left blank, an excerpt will be generated from the content.</small>
            </div>
            
            <div class="form-group">
                <label for="content-editor">Content:</label>
                <div class="editor-toolbar" aria-controls="content-editor">
                    <button type="button" class="toolbar-btn" data-command="bold"><i class="fas fa-bold"></i></button>
                    <button type="button" class="toolbar-btn" data-command="italic"><i class="fas fa-italic"></i></button>
                    <button type="button" class="toolbar-btn" data-command="underline"><i class="fas fa-underline"></i></button>
                    <span class="toolbar-divider"></span>
                    <button type="button" class="toolbar-btn" data-command="justifyLeft"><i class="fas fa-align-left"></i></button>
                    <button type="button" class="toolbar-btn" data-command="justifyCenter"><i class="fas fa-align-center"></i></button>
                    <button type="button" class="toolbar-btn" data-command="justifyRight"><i class="fas fa-align-right"></i></button>
                    <span class="toolbar-divider"></span>
                    <button type="button" class="toolbar-btn" data-command="createLink"><i class="fas fa-link"></i></button>
                    <button type="button" class="toolbar-btn" data-command="insertImage"><i class="fas fa-image"></i></button>
                    <span class="toolbar-divider"></span>
                    <select class="toolbar-select" data-command="fontSize" aria-label="Font size">
                        <option value="1">Small</option>
                        <option value="3" selected>Normal</option>
                        <option value="5">Large</option>
                        <option value="7">X-Large</option>
                    </select>
                    <span class="toolbar-divider"></span>
                    <button type="button" class="toolbar-btn" data-command="insertUnorderedList"><i class="fas fa-list-ul"></i></button>
                    <button type="button" class="toolbar-btn" data-command="insertOrderedList"><i class="fas fa-list-ol"></i></button>
                    <button type="button" class="toolbar-btn" data-command="formatBlock" data-value="H1"><i class="fas fa-heading"></i> 1</button>
                    <button type="button" class="toolbar-btn" data-command="formatBlock" data-value="H2"><i class="fas fa-heading"></i> 2</button>
                    <button type="button" class="toolbar-btn" data-command="formatBlock" data-value="blockquote"><i class="fas fa-quote-right"></i></button>
                </div>
                <div id="content-editor" class="content-editor" contenteditable="true" data-form-type="other">${this.page.content || ''}</div>
                <textarea name="content" id="content-textarea" style="display: none;" autocomplete="off">${this.page.content || ''}</textarea>
            </div>
            
            <div class="form-actions">
                <button type="submit" class="btn-primary">Save Page</button>
                <button type="button" class="btn-secondary" id="cancel-btn">Cancel</button>
            </div>
        </form>`;
    }

    postRender() {
        // Handle toolbar buttons
        document.querySelectorAll('.toolbar-btn').forEach(button => {
            button.addEventListener('click', () => {
                const command = button.dataset.command;
                const value = button.dataset.value || '';
                
                // Focus the correct editor
                let targetId = 'content-editor';
                
                if (this.mode === 'editIntro') {
                    targetId = 'intro-content-editor';
                }
                
                document.getElementById(targetId).focus();
                
                if (command === 'createLink') {
                    const url = prompt('Enter the URL:', 'https://');
                    if (url) {
                        document.execCommand(command, false, url);
                    }
                } else if (command === 'insertImage') {
                    this.handleImageInsertion(targetId);
                } else {
                    document.execCommand(command, false, value);
                }
            });
        });
        
        // Handle font size change
        document.querySelectorAll('.toolbar-select').forEach(select => {
            select.addEventListener('change', function() {
                document.execCommand(this.dataset.command, false, this.value);
                
                let targetId = 'content-editor';
                
                if (document.getElementById('intro-content-editor')) {
                    targetId = 'intro-content-editor';
                }
                
                document.getElementById(targetId).focus();
            });
        });
        
        // Toggle blog options visibility
        const isBlogCheckbox = document.getElementById('is_blog');
        if (isBlogCheckbox) {
            const blogOptions = document.querySelectorAll('.blog-option');
            
            isBlogCheckbox.addEventListener('change', function() {
                blogOptions.forEach(option => {
                    option.style.display = this.checked ? 'block' : 'none';
                });
            });
        }
        
        // Setup form submission
        this.setupFormSubmission();

        // Setup cancel button
        document.getElementById('cancel-btn').addEventListener('click', () => {
            if (this.mode === 'editIntro') {
                router.navigate('/');
            } else {
                router.navigate('/manage');
            }
        });
    }

    // Method to handle image insertion
    handleImageInsertion(targetId) {
        // Create a temporary file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        
        // Handle file selection
        fileInput.addEventListener('change', async (e) => {
            if (fileInput.files && fileInput.files[0]) {
                const file = fileInput.files[0];
                
                try {
                    // Show loading indicator in editor
                    const editor = document.getElementById(targetId);
                    const selection = window.getSelection();
                    const range = selection.getRangeAt(0);
                    
                    // Create a placeholder for the image
                    const placeholder = document.createElement('span');
                    placeholder.className = 'image-placeholder';
                    placeholder.textContent = `Uploading ${file.name}...`;
                    range.insertNode(placeholder);
                    
                    // Use FormData to upload the image
                    const formData = new FormData();
                    formData.append('image', file);
                    
                    // Make API request to upload the image
                    const response = await fetch('/api/upload-image', {
                        method: 'POST',
                        body: formData,
                        credentials: 'same-origin'
                    });
                    
                    if (!response.ok) {
                        throw new Error('Image upload failed');
                    }
                    
                    const data = await response.json();
                    
                    // Replace the placeholder with the actual image
                    const img = document.createElement('img');
                    img.src = data.url;
                    img.alt = file.name;
                    img.style.maxWidth = '100%';
                    
                    if (placeholder.parentNode) {
                        placeholder.parentNode.replaceChild(img, placeholder);
                    }
                } catch (error) {
                    console.error('Error uploading image:', error);
                    
                    // Remove placeholder if there was an error
                    const placeholder = document.querySelector('.image-placeholder');
                    if (placeholder && placeholder.parentNode) {
                        placeholder.parentNode.removeChild(placeholder);
                    }
                }
            }
        });
        
        // Trigger file selection
        fileInput.click();
    }

    setupFormSubmission() {
        // Handle introduction form
        const introForm = document.getElementById('intro-editor-form');
        if (introForm) {
            introForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                // Copy content from contenteditable div to hidden textarea
                const contentHtml = document.getElementById('intro-content-editor').innerHTML;
                document.getElementById('intro-content-textarea').value = contentHtml;
                
                try {
                    await api.updateIntroduction(contentHtml);
                    flashMessage.success('Introduction updated successfully');
                    
                    // Force reload of home component data when returning to home
                    await homeComponent.fetchData();
                    
                    // Redirect to home
                    router.navigate('/');
                } catch (error) {
                    console.error('Error saving introduction:', error);
                    document.getElementById('content-container').innerHTML = this.render();
                    this.postRender();
                }
            });
        }

        // Handle page editor form
        const pageForm = document.getElementById('page-editor-form');
        if (pageForm) {
            pageForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                // Copy content from contenteditable div to hidden textarea
                const contentHtml = document.getElementById('content-editor').innerHTML;
                document.getElementById('content-textarea').value = contentHtml;
                
                // Get form data
                const title = document.getElementById('title-input').value;
                const content = document.getElementById('content-textarea').value;
                const is_blog = document.getElementById('is_blog').checked;
                const featured = document.getElementById('featured')?.checked || false;
                
                // Get excerpt if applicable
                let excerpt = '';
                if (is_blog) {
                    const excerptEditor = document.getElementById('excerpt-editor');
                    if (excerptEditor) {
                        // If user has entered a custom excerpt, use that
                        if (excerptEditor.innerHTML.trim()) {
                            excerpt = excerptEditor.innerHTML;
                            document.getElementById('excerpt').value = excerpt;
                        }
                        // Otherwise, the backend will generate one based on the improved algorithm
                    }
                }
                
                // Get slug if in create mode
                let slug = this.page.slug || '';
                if (this.mode === 'create') {
                    slug = document.getElementById('slug-input').value || '';
                }
                
                try {
                    if (this.mode === 'create') {
                        // Create new page
                        const response = await api.createPage({
                            title,
                            slug,
                            content,
                            is_blog,
                            excerpt,
                            featured
                        });
                        
                        // Redirect to the new page
                        router.navigate('/manage');
                    } else {
                        // Update existing page
                        await api.updatePage(this.page.slug, {
                            title,
                            content,
                            is_blog,
                            excerpt,
                            featured
                        });
                        
                        // Redirect back to manage pages
                        router.navigate('/manage');
                    }
                } catch (error) {
                    console.error('Error saving page:', error);
                    document.getElementById('content-container').innerHTML = this.render();
                    this.postRender();
                }
            });
        }
    }
}

const editorComponent = new EditorComponent();
