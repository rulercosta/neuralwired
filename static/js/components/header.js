/**
 * Header Component
 * Renders the site header with navigation and theme toggle
 */
class HeaderComponent {
    constructor() {
        this.isAuthenticated = false;
    }

    setAuthStatus(status) {
        if (this.isAuthenticated !== status) {
            this.isAuthenticated = status;
            // Re-render header when auth status changes directly on the component
            const headerContainer = document.getElementById('header-container');
            if (headerContainer) {
                headerContainer.innerHTML = this.render();
                this.postRender();
            }
        }
    }

    render() {
        return `
        <header class="site-header">
            <div class="container">
                <div class="header-left">
                    <a href="/">neuralwired</a>
                </div>
                <div class="header-right">
                    <div class="header-icons">
                        <button class="theme-toggle icon-link" title="Toggle theme">◐</button>
                        ${this.isAuthenticated ? `
                        <div class="admin-links">
                            <a href="/manage" class="editor-link icon-link" title="Manage Pages">≡</a>
                            <a href="#" class="logout-link icon-link" title="Logout" id="logout-button">↵</a>
                        </div>
                        ` : `
                        <div class="admin-links">
                            <a href="/login" class="login-link icon-link" title="Login">→</a>
                        </div>
                        `}
                    </div>
                </div>
            </div>
        </header>`;
    }

    postRender() {
        // Setup theme toggle
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
            });
        }

        // Setup logout functionality
        const logoutButton = document.getElementById('logout-button');
        if (logoutButton) {
            logoutButton.addEventListener('click', async (e) => {
                e.preventDefault();
                try {
                    await api.logout();
                    router.navigate('/');
                } catch (error) {
                    console.error('Logout error:', error);
                }
            });
        }
    }
}

const headerComponent = new HeaderComponent();
