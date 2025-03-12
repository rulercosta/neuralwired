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
