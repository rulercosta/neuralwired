/**
 * Manage Pages Component
 * Administrative interface for managing pages and posts
 */
class ManagePagesComponent {
    constructor() {
        this.pages = [];
    }

    async fetchData() {
        try {
            this.pages = await api.getAllPages();
        } catch (error) {
            console.error('Error fetching pages:', error);
            this.pages = [];
        }
    }

    render() {
        if (!this.pages) {
            return '<div class="loading">Loading...</div>';
        }

        return `
        <header>
            <h1>Manage Pages</h1>
            <div class="site-nav page-nav">
                <ul>
                    <li><a href="/">← back to home</a></li>
                </ul>
            </div>
        </header>

        <div class="actions">
            <a href="/new" class="btn-primary">Create New Page</a>
        </div>

        <div class="pages-list">
            ${this.pages && this.pages.length > 0 ? `
                <table class="pages-table">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Slug</th>
                            <th>Last Updated</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.pages.map(page => `
                            <tr>
                                <td>${page.title}</td>
                                <td><a href="/p/${page.slug}" target="_blank">${page.slug}</a></td>
                                <td>${page.updated_at}</td>
                                <td class="actions-cell">
                                    <a href="/edit/${page.slug}" class="action-btn edit-btn">
                                        Edit
                                    </a>
                                    <button data-slug="${page.slug}" class="action-btn delete-btn delete-page-btn">
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : `
                <p class="no-pages-message">No pages have been created yet.</p>
            `}
        </div>`;
    }

    postRender() {
        // Setup delete buttons
        document.querySelectorAll('.delete-page-btn').forEach(button => {
            button.addEventListener('click', async () => {
                const slug = button.getAttribute('data-slug');
                if (confirm('Are you sure you want to delete this page?')) {
                    try {
                        await api.deletePage(slug);
                        await this.fetchData();
                        document.getElementById('content-container').innerHTML = this.render();
                        this.postRender();
                    } catch (error) {
                        console.error(`Error deleting page "${slug}":`, error);
                    }
                }
            });
        });
    }
}

const managePagesComponent = new ManagePagesComponent();
