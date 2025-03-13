"""
Tests for authentication API
"""
import json

def test_login_success(client):
    """Test successful login."""
    response = client.post(
        '/api/auth/login',
        json={'username': 'admin', 'password': 'admin'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'Login successful' in data['message']

def test_login_missing_fields(client):
    """Test login with missing fields."""
    # Missing password
    response = client.post(
        '/api/auth/login',
        json={'username': 'admin'}
    )
    assert response.status_code == 400
    
    # Missing username
    response = client.post(
        '/api/auth/login',
        json={'password': 'admin'}
    )
    assert response.status_code == 400

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        '/api/auth/login',
        json={'username': 'admin', 'password': 'wrongpassword'}
    )
    assert response.status_code == 401

def test_logout(client, auth):
    """Test logout functionality."""
    # First login
    auth.login()
    
    # Then logout
    response = auth.logout()
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'Logout successful' in data['message']

def test_auth_status(client, auth):
    """Test authentication status."""
    # Initially not authenticated
    response = client.get('/api/auth/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['authenticated'] is False
    
    # After login, should be authenticated
    auth.login()
    response = client.get('/api/auth/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['authenticated'] is True
    assert data['user'] == 'admin'
