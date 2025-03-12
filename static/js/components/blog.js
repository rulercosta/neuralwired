/**
 * Blog Index Component
 * Renders the list of all blog posts
 */
class BlogIndexComponent {
    constructor() {
        this.posts = [];
    }

    async fetchData() {
        try {
            this.posts = await api.getBlogPosts();
        } catch (error) {
            console.error('Error fetching blog posts:', error);
            this.posts = [];
        }
    }

    render() {
        if (!this.posts) {
            return '<div class="loading">Loading...</div>';
        }

        return `
        <header>
            <div class="intro-section">
                <h1>blogs</h1>
            </div>
            <div class="site-nav page-nav">
                <ul>
                    <li><a href="/">← back to home</a></li>
                </ul>
            </div>
        </header>

        <main>
            <section class="content-section blog-archive">
                ${this.posts && this.posts.length > 0 ? `
                    <div class="post-grid">
                        ${this.posts.map(post => `
                            <article class="post-card">
                                <h3><a href="/blog/${post.slug}">${post.title}</a></h3>
                                <div class="post-meta">
                                    <span class="post-date">${post.published_date.split(' ')[0]}</span>
                                </div>
                                <div class="post-excerpt">
                                    ${post.excerpt || this.formatExcerpt(post.content)}
                                </div>
                                <a href="/blog/${post.slug}" class="read-more">read more →</a>
                            </article>
                        `).join('')}
                    </div>
                ` : `
                    <p class="no-posts">No posts published yet.</p>
                `}
            </section>
        </main>`;
    }

    // Helper function to format excerpts from content when no explicit excerpt exists
    formatExcerpt(content) {
        // If no content, return empty string
        if (!content) return '';
        
        // Create a temporary div to handle HTML content
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;
        
        // Get plain text version
        const plainText = tempDiv.textContent || tempDiv.innerText || '';
        
        // Create excerpt with max length of 150 characters
        const maxLength = 150;
        if (plainText.length <= maxLength) {
            return plainText;
        }
        
        // Find a good breaking point
        const truncateAt = plainText.substr(0, maxLength).lastIndexOf(' ');
        const goodBreakPoint = truncateAt > 0 ? truncateAt : maxLength;
        
        return plainText.substr(0, goodBreakPoint) + '...';
    }
}

/**
 * Blog Post Component
 * Renders a single blog post
 */
class BlogPostComponent {
    constructor() {
        this.post = null;
        this.isAuthenticated = false;
    }

    setAuthStatus(status) {
        this.isAuthenticated = status;
    }

    async fetchData(slug) {
        try {
            this.post = await api.getPageBySlug(slug);
        } catch (error) {
            console.error(`Error fetching blog post with slug "${slug}":`, error);
            this.post = null;
        }
    }

    render() {
        if (!this.post) {
            return '<div class="loading">Loading...</div>';
        }

        return `
        <header>
            <div class="site-nav page-nav">
                <ul>
                    <li><a href="/blog">← back</a></li>
                    ${this.isAuthenticated ? `
                    <li><a href="/edit/${this.post.slug}">edit</a></li>
                    ` : ''}
                </ul>
            </div>
        </header>

        <main>
            <article class="blog-post">
                <header class="post-header">
                    <h1 class="post-title">${this.post.title}</h1>
                    <div class="post-meta">
                        <span class="post-date">${this.post.published_date.split(' ')[0]}</span>
                    </div>
                </header>
                <div class="post-content">
                    ${this.post.content}
                </div>
            </article>
        </main>`;
    }
}

const blogIndexComponent = new BlogIndexComponent();
const blogPostComponent = new BlogPostComponent();
