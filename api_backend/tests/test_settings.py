"""
Tests for settings API
"""
import json

def test_get_settings(client):
    """Test getting all settings."""
    response = client.get('/api/settings')
    assert response.status_code == 200
    data = json.loads(response.data)
    # At least the introduction setting should exist
    assert 'introduction' in data

def test_get_setting(client):
    """Test getting a specific setting."""
    # Get the introduction setting
    response = client.get('/api/settings/introduction')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'introduction' in data
    assert isinstance(data['introduction'], str)
    
    # Try to get a non-existent setting
    response = client.get('/api/settings/nonexistent')
    assert response.status_code == 404

def test_update_setting(client, auth):
    """Test updating a setting."""
    auth.login()
    
    # Update an existing setting
    response = client.put(
        '/api/settings/introduction',
        json={'value': 'Updated introduction text.'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    
    # Verify the update
    response = client.get('/api/settings/introduction')
    data = json.loads(response.data)
    assert data['introduction'] == 'Updated introduction text.'
    
    # Create a new setting
    response = client.put(
        '/api/settings/new_setting',
        json={'value': 'This is a new setting.'}
    )
    assert response.status_code == 200
    
    # Verify the new setting
    response = client.get('/api/settings/new_setting')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['new_setting'] == 'This is a new setting.'

def test_update_multiple_settings(client, auth):
    """Test updating multiple settings at once."""
    auth.login()
    
    settings_data = {
        'setting1': 'Value 1',
        'setting2': 'Value 2',
        'setting3': 'Value 3'
    }
    
    response = client.post(
        '/api/settings',
        json=settings_data
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    
    # Verify all settings were updated
    response = client.get('/api/settings')
    data = json.loads(response.data)
    for key, value in settings_data.items():
        assert key in data
        assert data[key] == value

def test_delete_setting(client, auth):
    """Test deleting a setting."""
    auth.login()
    
    # Create a setting to delete
    client.put(
        '/api/settings/delete_me',
        json={'value': 'This setting will be deleted.'}
    )
    
    # Delete the setting
    response = client.delete('/api/settings/delete_me')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    
    # Verify deletion
    response = client.get('/api/settings/delete_me')
    assert response.status_code == 404

def test_authentication_required(client):
    """Test that authentication is required for modifying settings."""
    # Try to update a setting without authentication
    response = client.put(
        '/api/settings/test',
        json={'value': 'Unauthorized update'}
    )
    assert response.status_code == 401
    
    # Try to delete a setting without authentication
    response = client.delete('/api/settings/introduction')
    assert response.status_code == 401
    
    # Try to update multiple settings without authentication
    response = client.post(
        '/api/settings',
        json={'setting1': 'Unauthorized'}
    )
    assert response.status_code == 401
