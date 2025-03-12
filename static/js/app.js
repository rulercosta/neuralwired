/**
 * Main Application
 * Manages the SPA lifecycle and component rendering
 */
class App {
    constructor() {
        this.isAuthenticated = false;
        this.initialized = false;
    }

    async init() {
        try {
            // Set up error handling
            this.setupErrorHandling();
            
            // Register auth state change listener
            api.addEventListener('authStateChanged', (data) => {
                this.isAuthenticated = data.authenticated;
                this.updateComponentsAuthStatus();
                this.renderHeader();
            });
            
            // Check authentication status on app start
            await this.checkAuthentication();
            
            // Setup header and footer which are always present
            this.renderHeader();
            this.renderFooter();
            
            // Initialize router first
            router.init();
            
            // Setup routing after router is initialized
            this.setupRouting();
            
            // Mark app as initialized
            this.initialized = true;
            
            // Handle initial route
            router.handleRouteChange();
            
            // Remove theme-initializing class to allow transitions
            setTimeout(() => {
                document.documentElement.classList.remove('theme-initializing');
            }, 200);
        } catch (error) {
            console.error('Error initializing app:', error);
            document.getElementById('content-container').innerHTML = `
                <div class="error-container">
                    <h1>Something went wrong</h1>
                    <p>We're having trouble loading the application. Please try again later.</p>
                    <p><a href="/" class="reload-link">Reload</a></p>
                </div>
            `;
        }
    }
    
    /**
     * Set up application-wide error handling
     */
    setupErrorHandling() {
        errorHandler.addErrorListener((error, source) => {
            // If it's an authentication error while authenticated, log user out
            if (this.isAuthenticated && errorHandler.isAuthError(error)) {
                console.warn('Auth error detected, logging out');
                api.logout().catch(e => console.error('Logout error:', e));
            } else {
                // Show error message for other errors
                flashMessage.error(errorHandler.formatErrorMessage(error));
            }
        });
        
        // Add global error handling
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            flashMessage.error('An unexpected error occurred');
        });
    }
    
    /**
     * Check if the user is authenticated
     */
    async checkAuthentication() {
        try {
            const response = await api.checkAuth();
            this.isAuthenticated = response.authenticated;
            
            // Update components that need auth status
            this.updateComponentsAuthStatus();
        } catch (error) {
            console.error('Auth check failed:', error);
            this.isAuthenticated = false;
            this.updateComponentsAuthStatus();
        }
    }
    
    /**
     * Update auth status in components that need it
     */
    updateComponentsAuthStatus() {
        // Components that need to know about authentication status
        headerComponent.setAuthStatus(this.isAuthenticated);
        pageComponent.setAuthStatus(this.isAuthenticated);
        blogPostComponent.setAuthStatus(this.isAuthenticated);
        homeComponent.setAuthStatus(this.isAuthenticated);
    }
    
    /**
     * Render the site header
     */
    renderHeader() {
        const headerContainer = document.getElementById('header-container');
        headerContainer.innerHTML = headerComponent.render();
        headerComponent.postRender();
    }
    
    /**
     * Render the site footer
     */
    renderFooter() {
        const footerContainer = document.getElementById('footer-container');
        footerContainer.innerHTML = footerComponent.render();
    }
    
    /**
     * Setup application routing
     */
    setupRouting() {
        // Home page
        router.addRoute('/', async () => {
            // Force refresh of home component data when navigating to home
            await homeComponent.refreshData();
            await this.renderComponent(homeComponent);
        });
        
        // Login page
        router.addRoute('/login', async () => {
            if (this.isAuthenticated) {
                router.navigate('/');
                return;
            }
            await this.renderComponent(loginComponent);
        });
        
        // Blog index page
        router.addRoute('/blog', async () => {
            await this.renderComponent(blogIndexComponent);
        });
        
        // Blog post page
        router.addRoute(/\/blog\/(?<slug>[a-zA-Z0-9-]+)/, async (params) => {
            await this.renderBlogPost(params.slug);
        });
        
        // View static page
        router.addRoute(/\/p\/(?<slug>[a-zA-Z0-9-]+)/, async (params) => {
            await this.renderPage(params.slug);
        });
        
        // Manage pages (admin)
        router.addRoute('/manage', async () => {
            if (!this.isAuthenticated) {
                router.navigate('/login');
                return;
            }
            await this.renderComponent(managePagesComponent);
        });
        
        // Edit page (admin)
        router.addRoute(/\/edit\/(?<slug>[a-zA-Z0-9-]+)/, async (params) => {
            if (!this.isAuthenticated) {
                router.navigate('/login');
                return;
            }
            await this.renderEditPage(params.slug);
        });
        
        // New page (admin)
        router.addRoute('/new', async () => {
            if (!this.isAuthenticated) {
                router.navigate('/login');
                return;
            }
            await this.renderEditPage();
        });
        
        // Edit introduction (admin)
        router.addRoute('/edit-intro', async () => {
            if (!this.isAuthenticated) {
                router.navigate('/login');
                return;
            }
            await this.renderEditIntroduction();
        });
        
        // 404 Not Found page - Only when truly no match is found
        router.setNotFoundHandler(async () => {
            await this.renderComponent(notFoundComponent);
        });
        
        // Initialize routing on startup - check current path 
        router.handleRouteChange();
    }
    
    /**
     * Render a specific component
     */
    async renderComponent(component, fetchDataParams = null) {
        const contentContainer = document.getElementById('content-container');
        
        // Show loading state
        contentContainer.innerHTML = '<div class="loading">Loading...</div>';
        
        // Fetch data if component has fetchData method
        if (component.fetchData) {
            try {
                if (fetchDataParams !== null) {
                    await component.fetchData(fetchDataParams);
                } else {
                    await component.fetchData();
                }
            } catch (error) {
                console.error('Error fetching data for component:', error);
                contentContainer.innerHTML = `
                    <div class="error-container">
                        <h1>Error</h1>
                        <p>${errorHandler.formatErrorMessage(error)}</p>
                        <p><a href="javascript:window.location.reload()" class="reload-link">Reload page</a></p>
                    </div>
                `;
                return;
            }
        }
        
        // Render component
        contentContainer.innerHTML = component.render();
        
        // Execute post-render logic if available
        if (component.postRender) {
            component.postRender();
        }
    }
    
    /**
     * Render a blog post
     */
    async renderBlogPost(slug) {
        try {
            await blogPostComponent.fetchData(slug);
            
            // If post not found, show 404
            if (!blogPostComponent.post) {
                await this.renderComponent(notFoundComponent);
                return;
            }
            
            // Update auth status and render
            blogPostComponent.setAuthStatus(this.isAuthenticated);
            document.getElementById('content-container').innerHTML = blogPostComponent.render();
        } catch (error) {
            const contentContainer = document.getElementById('content-container');
            contentContainer.innerHTML = `
                <div class="error-container">
                    <h1>Error</h1>
                    <p>${errorHandler.formatErrorMessage(error)}</p>
                    <p><a href="javascript:window.location.reload()" class="reload-link">Reload page</a></p>
                </div>
            `;
        }
    }
    
    /**
     * Render a static page
     */
    async renderPage(slug) {
        try {
            await pageComponent.fetchData(slug);
            
            // If page not found, show 404
            if (!pageComponent.page) {
                await this.renderComponent(notFoundComponent);
                return;
            }
            
            // If it's actually a blog post, redirect to blog URL
            if (pageComponent.page.is_blog) {
                router.navigate(`/blog/${slug}`);
                return;
            }
            
            // Update auth status and render
            pageComponent.setAuthStatus(this.isAuthenticated);
            document.getElementById('content-container').innerHTML = pageComponent.render();
        } catch (error) {
            const contentContainer = document.getElementById('content-container');
            contentContainer.innerHTML = `
                <div class="error-container">
                    <h1>Error</h1>
                    <p>${errorHandler.formatErrorMessage(error)}</p>
                    <p><a href="javascript:window.location.reload()" class="reload-link">Reload page</a></p>
                </div>
            `;
        }
    }
    
    /**
     * Render the page editor for creating or editing pages
     */
    async renderEditPage(slug = null) {
        // Create the edit page component if it doesn't exist yet
        await this.renderComponent(editorComponent, slug);
    }
    
    /**
     * Render the introduction editor
     */
    async renderEditIntroduction() {
        await this.renderComponent(editorComponent, 'introduction');
    }
}

// Create the app instance
const app = new App();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    app.init().catch(error => {
        console.error('Error initializing app:', error);
        document.getElementById('content-container').innerHTML = `
            <div class="error-container">
                <h1>Something went wrong</h1>
                <p>We're having trouble loading the application. Please try again later.</p>
                <p><a href="/" class="reload-link">Reload</a></p>
            </div>
        `;
    });
});
