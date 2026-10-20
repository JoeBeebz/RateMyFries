import sqlite3

import pytest

from app import create_app, db, one
from locations import GooglePlaces, LocationUnavailable
from test_app import app, client, listing, make_admin, post, register, token


def test_public_registration_cannot_elevate(client, app):
    assert post(client, '/register', {'username': 'alice', 'email': 'alice@example.com',
                'password': 'correct horse battery', 'role': 'admin'}).status_code == 302
    with app.app_context():
        assert one('SELECT role FROM users')['role'] == 'user'
        with pytest.raises(sqlite3.IntegrityError):
            db().execute("UPDATE users SET role='superuser'")
        db().rollback()
    for path in ['/restaurants/new', '/admin/inbox', '/admin/accounts']:
        assert client.get(path).status_code == 403
        assert post(client, path, {'username': 'alice'}).status_code in (403, 405)
    assert b'Admin inbox' not in client.get('/profile').data


def test_submission_review_privacy_and_idempotency(app, client):
    register(client)
    business = {'name': 'Local Diner', 'address': '123 Business Road', 'description': '<script>draft</script>'}
    assert post(client, '/business-requests/new', business).status_code == 302
    assert post(client, '/business-requests/new', business).status_code == 400
    assert b'Local Diner' not in client.get('/search').data
    with app.app_context():
        rid = one('SELECT id FROM business_requests')['id']
        assert one('SELECT COUNT(*) n FROM restaurants')['n'] == 0
    assert post(client, f'/admin/requests/{rid}/review', {'decision': 'approved'}).status_code == 403
    post(client, '/logout')
    register(client, 'bobby')
    assert b'Local Diner' not in client.get('/business-requests').data
    make_admin(client)
    assert b'&lt;script&gt;' in client.get('/admin/inbox').data
    assert client.post(f'/admin/requests/{rid}/review', data={'decision': 'approved'}).status_code == 400
    assert post(client, f'/admin/requests/{rid}/review', {'decision': 'hacked'}).status_code == 400
    assert post(client, f'/admin/requests/{rid}/review', {'decision': 'approved', 'review_note': 'Verified'}).status_code == 302
    assert post(client, f'/admin/requests/{rid}/review', {'decision': 'approved'}).status_code == 409
    with app.app_context():
        assert one('SELECT COUNT(*) n FROM restaurants')['n'] == 1
        assert one('SELECT status FROM business_requests')['status'] == 'approved'
    assert b'Local Diner' in client.get('/search').data


def test_rejection_and_validation(client, app):
    register(client)
    assert post(client, '/business-requests/new', {'name': ' ', 'address': 'Here'}).status_code == 400
    assert post(client, '/business-requests/new', {'name': 'Business', 'address': 'x'*241}).status_code == 400
    post(client, '/business-requests/new', {'name': 'Business', 'address': 'Here'})
    make_admin(client)
    with app.app_context():
        rid = one('SELECT id FROM business_requests')['id']
    post(client, f'/admin/requests/{rid}/review', {'decision': 'rejected', 'review_note': 'Please correct the address.'})
    assert b'Please correct the address.' in client.get('/business-requests').data
    assert b'Business' not in client.get('/search').data


def test_admin_bootstrap_and_authorization(client, app):
    register(client)
    runner = app.test_cli_runner()
    assert runner.invoke(args=['bootstrap-admin', 'missing']).exit_code != 0
    assert runner.invoke(args=['bootstrap-admin', 'alice']).exit_code == 0
    post(client, '/logout')
    register(client, 'bobby')
    assert runner.invoke(args=['bootstrap-admin', 'bobby']).exit_code != 0
    assert post(client, '/admin/accounts', {'username': 'bobby'}).status_code == 403
    post(client, '/logout')
    post(client, '/login', {'identity': 'alice', 'password': 'correct horse battery'})
    assert client.post('/admin/accounts', data={'username': 'bobby'}).status_code == 400
    assert post(client, '/admin/accounts', {'username': 'bobby'}).status_code == 302
    assert post(client, '/admin/accounts', {'username': 'bobby'}).status_code == 302
    with app.app_context():
        assert one("SELECT role FROM users WHERE username='bobby'")['role'] == 'admin'
        assert one("SELECT COUNT(*) n FROM admin_audit WHERE action='promote'")['n'] == 1


def test_private_address_owner_only_clear_and_search(app, client, monkeypatch):
    register(client)
    private = '987 Private Home Avenue'
    assert post(client, '/profile', {'username': 'alice', 'email': 'alice@example.com', 'address': private, 'role': 'admin'}).status_code == 302
    assert private.encode() in client.get('/profile').data
    assert private.encode() not in client.get('/search').data
    calls = []
    monkeypatch.setattr(app.extensions['places'], 'geocode', lambda address: calls.append(address) or (42.5, -87.8))
    response = post(client, '/search', {'use_saved': '1', 'radius': '10'})
    assert response.status_code == 200
    assert calls == [private]
    assert private.encode() not in response.data
    assert 'Location' not in response.headers
    post(client, '/logout')
    register(client, 'bobby')
    assert private.encode() not in client.get('/profile').data
    assert post(client, '/search', {'use_saved': '1'}).status_code == 400
    post(client, '/logout')
    post(client, '/login', {'identity': 'alice', 'password': 'correct horse battery'})
    post(client, '/profile', {'username': 'alice', 'email': 'alice@example.com', 'address': ''})
    with app.app_context():
        assert one("SELECT address,role FROM users WHERE username='alice'")['address'] == ''
        assert one("SELECT role FROM users WHERE username='alice'")['role'] == 'user'


def test_unified_composed_search_and_address_distance(client, app, monkeypatch):
    register(client)
    listing(client, 'Near Diner', 'Here', latitude='42.5', longitude='-87.8')
    listing(client, 'Far Diner', 'Far', latitude='30', longitude='-80')
    monkeypatch.setattr(app.extensions['places'], 'geocode', lambda address: (42.5, -87.8))
    response = post(client, '/search', {'address': 'Test address', 'radius': '5', 'style': 'waffle', 'min_price': '4', 'max_price': '5', 'sort': 'nearest'})
    assert response.status_code == 200
    assert b'Near Diner' in response.data and b'Far Diner' not in response.data
    assert b'Waffle fries' in response.data
    assert b'name="latitude"' not in response.data and b'type="number" name="lat"' not in response.data
    assert client.get('/fries?q=waffle').location.endswith('/search?q=waffle')
    assert client.get('/restaurants?q=Diner').location.endswith('/search?q=Diner')
    assert post(client, '/search', {'radius': '5'}).status_code == 400
    assert post(client, '/search', {'sort': 'nearest'}).status_code == 400


def test_location_failures_and_autocomplete_contract(client, app, monkeypatch):
    assert post(client, '/search', {'address': 'Test'}).status_code == 400
    assert client.post('/api/address-suggestions').status_code == 400
    payload = {'token': '12345678-1234-1234-1234-123456789012'}
    assert post(client, '/api/address-suggestions', {**payload, 'input': '12'}).json == {'suggestions': []}
    assert post(client, '/api/address-suggestions', {**payload, 'input': '123'}).status_code == 503
    seen = []
    monkeypatch.setattr(app.extensions['places'], 'suggest', lambda text, token: seen.append((text, token)) or ['123 Main Street'])
    assert post(client, '/api/address-suggestions', {**payload, 'input': '123'}).json == {'suggestions': ['123 Main Street']}
    assert seen[0][0] == '123'
    assert post(client, '/api/address-suggestions', {'input': '123', 'token': '../bad'}).status_code == 400


def test_google_import_ids_only_idempotent_no_invented_ratings(app, monkeypatch):
    runner = app.test_cli_runner()
    assert runner.invoke(args=['import-kenosha']).exit_code != 0
    monkeypatch.setattr(app.extensions['places'], 'kenosha', lambda: [{'id': 'place_'+str(i)} for i in range(3)])
    assert runner.invoke(args=['import-kenosha']).exit_code == 0
    assert runner.invoke(args=['import-kenosha']).exit_code == 0
    with app.app_context():
        assert one('SELECT COUNT(*) n FROM restaurants')['n'] == 3
        assert one('SELECT COUNT(*) n FROM reviews')['n'] == 0
        assert one('SELECT COUNT(*) n FROM fries')['n'] == 0
        assert one('SELECT address FROM restaurants')['address'] == ''
    monkeypatch.setattr(app.extensions['places'], 'details', lambda pid: {'displayName': {'text': 'Live Google name'}, 'formattedAddress': 'Kenosha, WI', 'attributions': [{'provider': 'Provider'}]})
    page = app.test_client().get('/search')
    assert b'Live Google name' in page.data and b'Google Maps' in page.data and b'Provider' in page.data


def test_upgrade_existing_database_without_data_loss(tmp_path):
    path = tmp_path / 'old.sqlite'
    with sqlite3.connect(path) as connection:
        connection.executescript("CREATE TABLE users(id INTEGER PRIMARY KEY,username TEXT,username_key TEXT,email TEXT,email_key TEXT,password_hash TEXT); INSERT INTO users VALUES(1,'old','old','old@example.com','old@example.com','hash');")
    application = create_app({'TESTING': True, 'SECRET_KEY': 'test', 'DATABASE': str(path)})
    with application.app_context():
        person = one('SELECT * FROM users')
        assert person['username'] == 'old' and person['role'] == 'user' and person['address'] == ''
    create_app({'TESTING': True, 'SECRET_KEY': 'test', 'DATABASE': str(path)})


def test_places_adapter_requests_no_key_in_url(monkeypatch):
    import locations
    import json
    from io import BytesIO
    seen = []
    def fake_open(req, timeout):
        seen.append(req)
        return BytesIO(json.dumps({'places': [{'location': {'latitude': 42.5, 'longitude': -87.8}}]}).encode())
    monkeypatch.setattr(locations, 'urlopen', fake_open)
    provider = GooglePlaces('test-not-a-real-key')
    assert provider.geocode('Address') == (42.5, -87.8)
    assert 'test-not-a-real-key' not in seen[0].full_url
    assert seen[0].get_header('X-goog-api-key') == 'test-not-a-real-key'
    with pytest.raises(LocationUnavailable):
        provider.details('../invalid')
