/**
 * Simple Client-side Router
 * Handles navigation without page reloads
 */
class Router {
    constructor() {
        this.routes = [];
        this.notFoundHandler = () => {
            document.getElementById('content-container').innerHTML = '<h1>Page Not Found</h1>';
        };
        
        // Only add event listeners during init to allow proper sequencing
    }
    
    init() {
        // Handle initial page load
        window.addEventListener('DOMContentLoaded', () => {
            this.handleRouteChange();
        });
        
        // Handle browser back/forward navigation
        window.addEventListener('popstate', () => {
            this.handleRouteChange();
        });
        
        // Intercept link clicks for internal navigation
        document.addEventListener('click', (e) => {
            // Find closest anchor tag if the click target is a child element
            const anchor = e.target.closest('a');
            
            if (!anchor) return;
            
            // Only handle internal links with href starting with / or #
            const href = anchor.getAttribute('href');
            if (!href || href.startsWith('http') || href.startsWith('mailto:')) {
                return;
            }
            
            // Handle internal navigation
            e.preventDefault();
            this.navigate(href);
        });
    }
    
    /**
     * Add a route handler
     * @param {string|RegExp} path - Route path or pattern
     * @param {Function} handler - Function to call when route matches
     */
    addRoute(path, handler) {
        this.routes.push({ path, handler });
        return this;
    }
    
    /**
     * Set the 404 Not Found handler
     */
    setNotFoundHandler(handler) {
        this.notFoundHandler = handler;
        return this;
    }
    
    /**
     * Navigate to a new URL
     */
    navigate(url) {
        // Update browser history
        window.history.pushState(null, '', url);
        
        // Handle the new route
        this.handleRouteChange();
    }
    
    /**
     * Match current URL to routes and execute handler
     */
    handleRouteChange() {
        const path = window.location.pathname;
        
        // Find matching route
        const route = this.findMatchingRoute(path);
        
        if (route) {
            // Extract route parameters if path is a regex
            let params = {};
            if (route.path instanceof RegExp) {
                const matches = path.match(route.path);
                if (matches && matches.groups) {
                    params = matches.groups;
                }
            }
            
            // Execute route handler
            route.handler(params);
        } else {
            this.notFoundHandler();
        }
        
        // Scroll to top on route change
        window.scrollTo(0, 0);
    }
    
    /**
     * Find route that matches the current path
     */
    findMatchingRoute(currentPath) {
        return this.routes.find(route => {
            if (route.path instanceof RegExp) {
                return route.path.test(currentPath);
            }
            return route.path === currentPath;
        });
    }
}

// Create and expose a singleton instance
const router = new Router();
