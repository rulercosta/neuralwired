/**
 * Error Handler Component
 * Centralized error handling for the SPA
 */
class ErrorHandler {
    constructor() {
        this.errorListeners = [];
    }

    /**
     * Register an error listener
     * @param {function} listener - Function to call when an error occurs
     */
    addErrorListener(listener) {
        this.errorListeners.push(listener);
    }

    /**
     * Handle an error
     * @param {Error} error - The error object
     * @param {string} source - The source of the error (component name)
     */
    handleError(error, source = 'unknown') {
        console.error(`Error in ${source}:`, error);
        
        // Notify all listeners
        this.errorListeners.forEach(listener => {
            try {
                listener(error, source);
            } catch (listenerError) {
                console.error('Error in error listener:', listenerError);
            }
        });

        // Return a formatted error message for display
        return this.formatErrorMessage(error);
    }

    /**
     * Format an error message for display
     * @param {Error} error - The error object
     * @returns {string} - Formatted error message
     */
    formatErrorMessage(error) {
        if (error.message) {
            return error.message;
        }
        return 'An unexpected error occurred. Please try again.';
    }

    /**
     * Check if the error is an authentication error
     * @param {Error} error - The error object
     * @returns {boolean} - True if authentication error
     */
    isAuthError(error) {
        return error.status === 401 || 
               (error.message && error.message.toLowerCase().includes('authentication'));
    }
}

// Create and expose a singleton instance
const errorHandler = new ErrorHandler();
