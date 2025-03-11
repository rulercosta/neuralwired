# Minimalist Portfolio Website

A minimalist, elegant portfolio website built with Flask (Python 3.10), featuring:
- Clean, responsive design
- Content management system with rich text editing
- Secure authentication

## Requirements

- Python 3.10.16
- Flask and dependencies (listed in requirements.txt)

## Installation

1. Ensure Python 3.10.16 is installed:
   ```bash
   python --version
   ```

2. Clone this repository:
   ```bash
   git clone <repository-url>
   cd blogger
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Set the Flask environment variables (optional):
   ```bash
   # For development
   export FLASK_ENV=development
   export FLASK_APP=app.py
   
   # For a more secure production key (recommended)
   export SECRET_KEY=your-secure-secret-key
   ```

2. Run the application:
   ```bash
   python app.py
   ```
   
3. Access the website at: http://127.0.0.1:5000/

## Content Management

1. Login via: http://127.0.0.1:5000/login
   - Default credentials:
     - Username: neuralwired
     - Password: your-secure-password

2. After login, you can:
   - Access the editor via the "Edit Content" link
   - Use the rich text editor to update content
   - Click "Publish" to update the live site

## Customization

- Edit CSS styles in `static/css/style.css`
- Modify templates in the `templates` directory
- Update the default content structure in `app.py`

## Security Notes

For production deployment:
1. Change the default password in app.py
2. Set a strong SECRET_KEY environment variable
3. Consider using a proper database instead of JSON file storage
4. Use HTTPS in production

## License

[MIT License](LICENSE)
