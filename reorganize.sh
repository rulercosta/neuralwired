#!/bin/bash

# Create new directory structure
mkdir -p backend/app
mkdir -p frontend/public
mkdir -p frontend/src/{js,css,components}

# Move backend Python files
mv *.py backend/app/
mv requirements.txt backend/
mv .env backend/
mv blogger.db backend/ 2>/dev/null || true

# Move frontend files
mv static/js/*.js frontend/src/js/
mv static/js/components/* frontend/src/components/
mv static/css/* frontend/src/css/
mv templates/* frontend/public/
mv static/favicon.ico frontend/public/ 2>/dev/null || true

# Clean up old directories
rm -rf static templates

# Copy docker files to backend
mv Dockerfile backend/
mv docker-compose.yml backend/

# Create new docker-compose at root
cat > docker-compose.yml << 'EOL'
version: '3'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend/blogger.db:/app/blogger.db
    env_file:
      - ./backend/.env
    restart: always

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend
EOL

# Create frontend Dockerfile
cat > frontend/Dockerfile << 'EOL'
FROM node:16-alpine

WORKDIR /app
COPY . .

# Install serve for static file serving
RUN npm install -g serve

EXPOSE 3000
CMD ["serve", "-s", "public", "-l", "3000"]
EOL

# Update backend Dockerfile path
sed -i 's|COPY \.|COPY app|g' backend/Dockerfile

# Create README
cat > README.md << 'EOL'
# Blogger

A modern blogging platform with decoupled frontend and backend.

## Structure

```
.
├── backend/            # Flask backend
│   ├── app/           # Python application code
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/          # Static frontend
│   ├── public/       # Static assets
│   └── src/          # Source files
│       ├── components/
│       ├── css/
│       └── js/
└── docker-compose.yml
```

## Development

1. Start the services:
```bash
docker-compose up
```

2. Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
EOL

echo "Project structure has been reorganized!"
echo "Please review the changes and update any paths in your code as needed."
