/**
 * Page Component
 * Renders a single page
 */
class PageComponent {
    constructor() {
        this.page = null;
        this.isAuthenticated = false;
    }

    setAuthStatus(status) {
        this.isAuthenticated = status;
    }

    async fetchData(slug) {
        try {
            this.page = await api.getPageBySlug(slug);
        } catch (error) {
            console.error(`Error fetching page with slug "${slug}":`, error);
            this.page = null;
        }
    }

    render() {
        if (!this.page) {
            return '<div class="loading">Loading...</div>';
        }

        return `
        <header>
            <div class="intro-section">
                <h1>${this.page.title}</h1>
            </div>
            <div class="site-nav page-nav">
                <ul>
                    <li><a href="/">← Back to home</a></li>
                    ${this.isAuthenticated ? `
                    <li><a href="/edit/${this.page.slug}">Edit this page</a></li>
                    ` : ''}
                </ul>
            </div>
        </header>

        <main>
            <div class="page-content">
                ${this.page.content}
            </div>
        </main>`;
    }
}

const pageComponent = new PageComponent();
