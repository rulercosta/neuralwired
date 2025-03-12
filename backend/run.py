import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import app

if __name__ == '__main__':
    app.run(debug=True)
