/**
 * Home Page Component
 * Renders the main landing page with introduction and featured content
 */
class HomeComponent {
    constructor() {
        this.content = null;
        this.featuredPosts = [];
        this.recentPosts = [];
        this.aboutPage = null;
        this.isAuthenticated = false;
        this.isLoading = true; // Add loading state
    }

    setAuthStatus(status) {
        this.isAuthenticated = status;
    }

    async fetchData() {
        try {
            this.isLoading = true;
            
            // Fetch site content (introduction)
            this.content = await api.getSiteContent();
            
            // Fetch featured blog posts
            this.featuredPosts = await api.getBlogPosts({ featured: true, limit: 3 });
            
            // Fetch recent blog posts
            this.recentPosts = await api.getBlogPosts({ limit: 5 });

            // TODO: Fetch about page if needed
            
            this.isLoading = false;
        } catch (error) {
            console.error('Error fetching home page data:', error);
            // Initialize with empty data to avoid null reference errors
            this.content = this.content || { introduction: '' };
            this.featuredPosts = this.featuredPosts || [];
            this.recentPosts = this.recentPosts || [];
            this.isLoading = false;
        }
    }

    render() {
        if (this.isLoading) {
            return '<div class="loading">Loading...</div>';
        }

        // Always render the page, even if content is missing or empty
        return `
        <header>
            <div class="intro-section">
                <h1>neuralwired blog</h1>
                <p>${this.content && this.content.introduction ? this.content.introduction : ''}</p>
                ${this.isAuthenticated ? `
                <div class="intro-edit">
                    <a href="/edit-intro" class="intro-edit-link" title="Edit Introduction">Edit</a>
                </div>
                ` : ''}
            </div>
        </header>

        <main>
            ${this.featuredPosts && this.featuredPosts.length > 0 ? `
            <section id="featured" class="content-section">
                <h1>featured</h1>
                <div class="featured-posts">
                    ${this.featuredPosts.map(post => `
                        <article class="featured-post">
                            <h3><a href="/blog/${post.slug}">${post.title}</a></h3>
                            <div class="post-meta">
                                <span class="post-date">${post.published_date ? post.published_date.split(' ')[0] : ''}</span>
                            </div>
                            <div class="post-excerpt">
                                ${post.excerpt || this.formatExcerpt(post.content)}
                            </div>
                            <a href="/blog/${post.slug}" class="read-more">read more →</a>
                        </article>
                    `).join('')}
                </div>
            </section>
            ` : ''}

            <section id="recent-posts" class="content-section">
                <h1>recent posts</h1>
                <div class="post-list">
                    ${this.recentPosts && this.recentPosts.length > 0 ? `
                        ${this.recentPosts.map(post => `
                            <article class="post-item">
                                <h3><a href="/blog/${post.slug}">${post.title}</a></h3>
                                <div class="post-meta">
                                    <span class="post-date">${post.published_date ? post.published_date.split(' ')[0] : ''}</span>
                                </div>
                                <div class="post-excerpt">
                                    ${post.excerpt || this.formatExcerpt(post.content)}
                                </div>
                                <a href="/blog/${post.slug}" class="read-more">read more →</a>
                            </article>
                        `).join('')}
                        <div class="view-all">
                            <a href="/blog" class="view-all-link">view all posts →</a>
                        </div>
                    ` : `
                        <p class="no-posts">No posts yet.</p>
                    `}
                </div>
            </section>
        </main>`;
    }

    // Helper function to format excerpts from content
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

const homeComponent = new HomeComponent();
