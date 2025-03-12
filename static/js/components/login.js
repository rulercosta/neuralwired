/**
 * Login Component
 * Handles user authentication
 */
class LoginComponent {
    constructor() {
        this.errorMessage = '';
    }

    setError(message) {
        this.errorMessage = message;
    }

    render() {
        return `
        <div class="auth-container">
            <h1>Login</h1>
            
            <form id="login-form">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required ${this.errorMessage ? 'class="input-error"' : ''}>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required ${this.errorMessage ? 'class="input-error"' : ''}>
                </div>
                
                <button type="submit" class="btn-primary">Login</button>
            </form>
            
            <div class="back-link">
                <a href="/">Back to Home</a>
            </div>
        </div>`;
    }

    postRender() {
        const form = document.getElementById('login-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                try {
                    await api.login(username, password);
                    // Redirect to home after successful login
                    router.navigate('/');
                } catch (error) {
                    this.setError('Invalid username or password');
                    flashMessage.error('Login failed: Invalid username or password');
                    // Re-render with error styling on inputs
                    document.getElementById('content-container').innerHTML = this.render();
                    this.postRender();
                }
            });
        }
    }
}

const loginComponent = new LoginComponent();
