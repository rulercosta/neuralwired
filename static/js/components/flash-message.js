/**
 * Flash Message Component
 * Shows temporary notifications that auto-dismiss after a specified time
 */
class FlashMessage {
    constructor() {
        this.visible = false;
        this.message = '';
        this.type = 'info'; // 'info', 'success', 'error', 'warning'
        this.timeout = null;
        this.duration = 3000; // Default duration in milliseconds
    }
    
    /**
     * Show a flash message
     * @param {string} message - Message to display
     * @param {string} type - Message type: 'info', 'success', 'error', 'warning'
     * @param {number} duration - How long to show the message in milliseconds (default: 3000)
     */
    show(message, type = 'info', duration = 3000) {
        // Clear any existing timeout
        if (this.timeout) {
            clearTimeout(this.timeout);
        }
        
        this.message = message;
        this.type = type;
        this.duration = duration;
        
        // Create the message element if it doesn't exist yet
        if (!document.getElementById('flash-message')) {
            this.createMessageElement();
        }
        
        // Update message content and type
        const messageEl = document.getElementById('flash-message');
        messageEl.textContent = message;
        messageEl.className = `flash-message flash-${type}`;
        
        // Show the message immediately without animation
        const containerEl = document.getElementById('flash-message-container');
        containerEl.style.display = 'flex';
        
        // Set visible flag
        this.visible = true;
        
        // Set timeout to hide message after duration
        this.timeout = setTimeout(() => {
            this.hide();
        }, duration);
    }
    
    /**
     * Hide the flash message
     */
    hide() {
        const containerEl = document.getElementById('flash-message-container');
        if (containerEl && this.visible) {
            // Hide immediately without animation
            containerEl.style.display = 'none';
            this.visible = false;
        }
    }
    
    /**
     * Create the flash message DOM element
     */
    createMessageElement() {
        const container = document.createElement('div');
        container.id = 'flash-message-container';
        container.style.display = 'none';
        
        // Create the message element
        container.innerHTML = `<div id="flash-message" class="flash-message"></div>`;
        
        // Add to body
        document.body.appendChild(container);
        
        // Add click handler to dismiss on click
        container.addEventListener('click', () => {
            this.hide();
        });
    }
    
    /**
     * Show a success message
     * @param {string} message - Success message
     * @param {number} duration - How long to show the message
     */
    success(message, duration = 3000) {
        this.show(message, 'success', duration);
    }
    
    /**
     * Show an error message
     * @param {string} message - Error message
     * @param {number} duration - How long to show the message
     */
    error(message, duration = 3000) {
        this.show(message, 'error', duration);
    }
    
    /**
     * Show an info message
     * @param {string} message - Info message
     * @param {number} duration - How long to show the message
     */
    info(message, duration = 3000) {
        this.show(message, 'info', duration);
    }
    
    /**
     * Show a warning message
     * @param {string} message - Warning message
     * @param {number} duration - How long to show the message
     */
    warning(message, duration = 3000) {
        this.show(message, 'warning', duration);
    }
}

// Create and expose a singleton instance
const flashMessage = new FlashMessage();
