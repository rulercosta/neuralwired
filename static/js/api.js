/**
 * API Client Library
 * Handles all communication with the backend API
 */
class ApiClient {
    constructor() {
        this.baseUrl = '/api';
        // Add event handling for auth state changes
        this.events = {
            authStateChanged: []
        };
    }

    /**
     * Add event listener for API events
     */
    addEventListener(event, callback) {
        if (this.events[event]) {
            this.events[event].push(callback);
        }
    }

    /**
     * Trigger event listeners
     */
    triggerEvent(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => callback(data));
        }
    }

    /**
     * Make API request with fetch
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        // Set default headers
        if (!options.headers) {
            options.headers = {
                'Content-Type': 'application/json'
            };
        }
        
        // Include credentials for session cookies
        options.credentials = 'same-origin';
        
        try {
            const response = await fetch(url, options);
            
            // Handle no content responses
            if (response.status === 204) {
                return null;
            }
            
            // Parse JSON response
            const data = await response.json();
            
            // If response is not ok, throw error with message
            if (!response.ok) {
                throw new Error(data.error || `API request failed with status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error(`API Request Error (${endpoint}):`, error);
            // Re-throw for component handling
            throw error;
        }
    }

    /**
     * Upload an image file
     * @param {File} file - The image file to upload
     * @returns {Promise<{url: string}>} - The URL of the uploaded image
     */
    async uploadImage(file) {
        const formData = new FormData();
        formData.append('image', file);
        
        const response = await fetch(`${this.baseUrl}/upload-image`, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Image upload failed');
        }
        
        return await response.json();
    }

    // Authentication
    async login(username, password) {
        const result = await this.request('/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        // Trigger auth state changed event
        this.triggerEvent('authStateChanged', { authenticated: true });
        flashMessage.success('Logged in successfully');
        return result;
    }

    async logout() {
        const result = await this.request('/logout', {
            method: 'POST'
        });
        // Trigger auth state changed event
        this.triggerEvent('authStateChanged', { authenticated: false });
        flashMessage.info('Logged out successfully');
        return result;
    }

    async checkAuth() {
        try {
            const result = await this.request('/check-auth');
            // Trigger auth state changed event
            this.triggerEvent('authStateChanged', { authenticated: result.authenticated });
            return result;
        } catch (error) {
            console.warn('Auth check failed, assuming not authenticated:', error);
            this.triggerEvent('authStateChanged', { authenticated: false });
            return { authenticated: false };
        }
    }

    // Content
    async getSiteContent() {
        try {
            return await this.request('/content');
        } catch (error) {
            console.warn('Error fetching site content:', error);
            // Re-throw error for component handling
            throw error;
        }
    }

    async updateIntroduction(content) {
        const result = await this.request('/content/intro', {
            method: 'PUT',
            body: JSON.stringify({ content })
        });
        flashMessage.success('Introduction updated successfully');
        return result;
    }

    // Pages
    async getAllPages() {
        return this.request('/pages');
    }

    async getPageBySlug(slug) {
        return this.request(`/pages/${slug}`);
    }

    async createPage(pageData) {
        const result = await this.request('/pages', {
            method: 'POST',
            body: JSON.stringify(pageData)
        });
        flashMessage.success('Page created successfully');
        return result;
    }

    async updatePage(slug, pageData) {
        const result = await this.request(`/pages/${slug}`, {
            method: 'PUT',
            body: JSON.stringify(pageData)
        });
        flashMessage.success('Page updated successfully');
        return result;
    }

    async deletePage(slug) {
        const result = await this.request(`/pages/${slug}`, {
            method: 'DELETE'
        });
        flashMessage.success('Page deleted successfully');
        return result;
    }

    // Blog posts
    async getBlogPosts(options = {}) {
        const params = new URLSearchParams();
        
        if (options.featured) {
            params.append('featured', 'true');
        }
        
        if (options.limit) {
            params.append('limit', options.limit);
        }
        
        const queryString = params.toString();
        const endpoint = queryString ? `/posts?${queryString}` : '/posts';
        
        try {
            return await this.request(endpoint);
        } catch (error) {
            console.warn('Error fetching blog posts:', error);
            throw error;
        }
    }
}

// Create and expose a singleton instance
const api = new ApiClient();
