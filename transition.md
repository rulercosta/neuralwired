# Architecture Transition Guide: Template-based to API-driven SPA

This document outlines the files to be deleted as part of our transition from server-side rendering with Jinja templates to a decoupled architecture with a Flask API backend and a client-side JavaScript SPA frontend.

## Overview of Change

We have transitioned from:
- **Template-based approach**: Flask + Jinja2 templates with server-side rendering
- **To**: Decoupled architecture with Flask backend API + client-side JavaScript SPA

## Deleted Files

The following files have been removed as part of this transition:
- `/templates/` directory (except for `index.html` which serves as the SPA shell)
  - Removed all Jinja2 template files for individual pages
  - Removed template partials
- `/static/js/main.js` (replaced with component-based structure)
- `/static/js/editor-old.js` (replaced with new editor component)
- Any other template-specific CSS files

## Modified App Structure

### Flask Routes
The main app.py file has been modified:
- All template-rendering routes have been replaced by a single route that serves the SPA shell
- Additional routes only needed for API endpoints

### JavaScript Structure
- Component-based architecture
- Each feature has its own component file
- Routing handled client-side

## Next Steps

1. Ensure all API endpoints in `/api/__init__.py` are working correctly
2. Verify the SPA functionality with the client-side JS components
3. Test all editor functionality including image uploads
4. Ensure proper error handling for API requests
5. Update documentation to reflect the new architecture
6. Add automated tests for the API endpoints

## Benefits of New Architecture

- **Better separation of concerns**: Backend focuses on data, frontend on presentation
- **Improved performance**: Less server load, faster user experience after initial load
- **More scalable**: Backend can be scaled independently from frontend
- **Modern development**: Aligns with current web development practices
- **Improved developer experience**: Easier to maintain and extend the codebase
