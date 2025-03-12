/**
 * Confirmation Dialog Component
 * Custom confirmation dialog that replaces the browser's built-in confirm
 */
class ConfirmDialog {
    constructor() {
        this.isVisible = false;
        this.message = '';
        this.confirmCallback = null;
        this.cancelCallback = null;
    }
    
    /**
     * Show the confirmation dialog
     * @param {string} message - The confirmation message to display
     * @param {function} confirmCallback - Function to call when confirmed
     * @param {function} cancelCallback - Optional function to call when canceled
     */
    show(message, confirmCallback, cancelCallback = null) {
        this.message = message;
        this.confirmCallback = confirmCallback;
        this.cancelCallback = cancelCallback;
        
        // Create the dialog if it doesn't exist yet
        if (!document.getElementById('confirm-dialog')) {
            this.createDialog();
        }
        
        // Update message
        document.getElementById('confirm-dialog-message').textContent = message;
        
        // Show the dialog
        const dialogEl = document.getElementById('confirm-dialog-container');
        dialogEl.style.display = 'flex';
        this.isVisible = true;
    }
    
    /**
     * Hide the confirmation dialog
     */
    hide() {
        const dialogEl = document.getElementById('confirm-dialog-container');
        if (dialogEl) {
            dialogEl.style.display = 'none';
            this.isVisible = false;
        }
    }
    
    /**
     * Create the dialog DOM elements
     */
    createDialog() {
        // Create container
        const container = document.createElement('div');
        container.id = 'confirm-dialog-container';
        
        // Create dialog HTML
        container.innerHTML = `
            <div id="confirm-dialog" class="confirm-dialog">
                <div class="confirm-dialog-content">
                    <p id="confirm-dialog-message"></p>
                    <div class="confirm-dialog-actions">
                        <button id="confirm-dialog-cancel" class="btn-secondary">Cancel</button>
                        <button id="confirm-dialog-confirm" class="btn-primary">Confirm</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add to body
        document.body.appendChild(container);
        
        // Add event listeners
        document.getElementById('confirm-dialog-confirm').addEventListener('click', () => {
            this.hide();
            if (this.confirmCallback) {
                this.confirmCallback();
            }
        });
        
        document.getElementById('confirm-dialog-cancel').addEventListener('click', () => {
            this.hide();
            if (this.cancelCallback) {
                this.cancelCallback();
            }
        });
        
        // Close when clicking outside
        container.addEventListener('click', (e) => {
            if (e.target === container) {
                this.hide();
                if (this.cancelCallback) {
                    this.cancelCallback();
                }
            }
        });
        
        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (this.isVisible && e.key === 'Escape') {
                this.hide();
                if (this.cancelCallback) {
                    this.cancelCallback();
                }
            }
        });
    }
}

// Create and expose a singleton instance
const confirmDialog = new ConfirmDialog();
