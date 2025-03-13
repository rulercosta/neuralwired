"""
Tests for uploads API
"""
import json
import io
import os
# Only import pytest if explicitly needed for test marks

def test_list_uploads_empty(client):
    """Test listing uploads when none exist."""
    response = client.get('/api/uploads/list')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0  # No uploads initially

def test_upload_file(client, auth, app):
    """Test uploading a file."""
    auth.login()
    
    # Create a test file
    data = {'file': (io.BytesIO(b'test file content'), 'test.txt')}
    response = client.post(
        '/api/uploads',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    result = json.loads(response.data)
    assert 'url' in result
    assert result['url'].startswith('/static/uploads/')
    assert '.txt' in result['url']
    
    # Verify file was saved
    filename = os.path.basename(result['url'].replace('/static/uploads/', ''))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    assert os.path.exists(file_path)
    with open(file_path, 'rb') as f:
        content = f.read()
        assert content == b'test file content'

def test_upload_unsupported_file(client, auth):
    """Test uploading an unsupported file type."""
    auth.login()
    
    # Create a test file with unsupported extension
    data = {'file': (io.BytesIO(b'test file content'), 'test.xyz')}
    response = client.post(
        '/api/uploads',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result

def test_list_uploads(client, auth):
    """Test listing uploads after uploading a file."""
    auth.login()
    
    # Upload a test file first
    data = {'file': (io.BytesIO(b'test content'), 'test.jpg')}
    client.post('/api/uploads', data=data, content_type='multipart/form-data')
    
    # Now check the list
    response = client.get('/api/uploads/list')
    assert response.status_code == 200
    files = json.loads(response.data)
    assert len(files) >= 1
    # At least one file should contain .jpg
    assert any('.jpg' in file['filename'] for file in files)

def test_delete_uploaded_file(client, auth, app):
    """Test deleting an uploaded file."""
    auth.login()
    
    # Upload a test file first
    data = {'file': (io.BytesIO(b'delete me'), 'delete.txt')}
    response = client.post('/api/uploads', data=data, content_type='multipart/form-data')
    result = json.loads(response.data)
    filename = os.path.basename(result['url'].replace('/static/uploads/', ''))
    
    # Delete the file
    response = client.delete(f'/api/uploads/{filename}')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] is True
    
    # Verify file was deleted
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    assert not os.path.exists(file_path)

def test_authentication_required_for_upload(client):
    """Test that authentication is required for uploading files."""
    # Try to upload without authentication
    data = {'file': (io.BytesIO(b'unauthorized'), 'unauth.txt')}
    response = client.post(
        '/api/uploads',
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 401

def test_authentication_required_for_delete(client, auth):
    """Test that authentication is required for deleting files."""
    # First upload a file
    auth.login()
    data = {'file': (io.BytesIO(b'to be deleted'), 'auth_delete.txt')}
    response = client.post('/api/uploads', data=data, content_type='multipart/form-data')
    result = json.loads(response.data)
    filename = os.path.basename(result['url'].replace('/static/uploads/', ''))
    
    # Log out
    auth.logout()
    
    # Try to delete without authentication
    response = client.delete(f'/api/uploads/{filename}')
    assert response.status_code == 401
