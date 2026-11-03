import html
import re

import pytest

from app import db
from locations import LocationUnavailable
from test_app import app, client, post


@pytest.fixture
def catalogue(app):
    with app.app_context():
        db().executemany('INSERT INTO restaurants(id,name,address,name_key,address_key) VALUES(?,?,?,?,?)', [
            (1, 'Wingstop', '123 First Street', 'wingstop', '123 first street'),
            (2, "AJ's Deli", '456 Other Street', "aj's deli", '456 other street'),
        ])
        db().executemany('INSERT INTO fries(id,restaurant_id,name,style,seasoned,price_cents) VALUES(?,?,?,?,?,?)', [
            (1, 1, 'Seasoned Fries', 'straight-cut', 1, 400),
            (2, 1, 'Cheese Fries', 'straight-cut', 1, 500),
            (3, 2, 'Cheese Fries', 'curly', 1, 600),
        ])
        db().commit()


def cards(response):
    return [(kind.decode(), int(identity), html.unescape(name.decode())) for kind, identity, name in
            re.findall(rb'<h3><a href="/(restaurants|fries)/(\d+)">([^<]+)</a>', response.data)]


@pytest.mark.parametrize('query', ['Wingstop', 'wingstop', ' WINGSTOP  '])
def test_restaurant_exact_name_returns_its_fries(catalogue, client, query):
    expected = [('restaurants', 1, 'Wingstop'), ('fries', 2, 'Cheese Fries'), ('fries', 1, 'Seasoned Fries')]
    assert cards(client.get('/search', query_string={'q': query})) == expected
    assert cards(post(client, '/search', {'q': query})) == expected


@pytest.mark.parametrize('query', ['wngstop', 'Wing', 'Wingstop fries', '%', '_', "' OR 1=1 --"])
def test_unlisted_partial_and_wildcard_queries_have_zero_matches(catalogue, client, query):
    response = client.get('/search', query_string={'q': query})
    assert response.status_code == 200
    assert cards(response) == []
    assert b'No restaurants found.' in response.data and b'No fries found.' in response.data
    assert cards(post(client, '/search', {'q': query})) == []


def test_fry_style_blank_and_composed_filters(catalogue, client):
    assert {c[:2] for c in cards(client.get('/search?q=cheese%20fries'))} == {
        ('restaurants', 1), ('restaurants', 2), ('fries', 2), ('fries', 3)}
    assert {c[:2] for c in cards(client.get('/search?q=curly'))} == {('restaurants', 2), ('fries', 3)}
    assert len(cards(client.get('/search?q='))) == 5
    assert cards(client.get('/search?q=Wingstop&min_price=4.5&max_price=5')) == [
        ('restaurants', 1, 'Wingstop'), ('fries', 2, 'Cheese Fries')]
    assert cards(client.get('/search?q=Wingstop&style=curly')) == []
    assert cards(client.get('/search', query_string={'q': "AJ's Deli"}))[0] == ('restaurants', 2, "AJ's Deli")


def test_choices_only_publish_existing_public_names(catalogue, app, client, monkeypatch):
    def no_google(*args):
        raise AssertionError('Known catalogue names should not need Google')
    monkeypatch.setattr(app.extensions['places'], 'details', no_google)
    with app.app_context():
        db().execute("INSERT INTO business_requests(name,address,name_key,address_key) "
                     "VALUES('Private pending business','Private address','private','private')")
        db().commit()
    response = client.get('/api/catalogue-choices')
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'no-store'
    assert sorted((c['name'], c['kind']) for c in response.json['choices']) == sorted([
        ('Wingstop', 'Restaurant'), ("AJ's Deli", 'Restaurant'), ('Seasoned Fries', 'Fries'),
        ('Cheese Fries', 'Fries'), ('curly', 'Style'), ('straight-cut', 'Style')])
    assert b'Private' not in response.data and b'123 First Street' not in response.data
    for path in ['/', '/search']:
        page = client.get(path)
        assert b'data-catalogue-search' in page.data and b'catalogue-search.js' in page.data


def test_ids_only_names_resolve_live_and_placeholder_is_not_searchable(catalogue, app, client, monkeypatch):
    with app.app_context():
        db().execute("UPDATE restaurants SET name='Google business',google_place_id='place_id' WHERE id=1")
        db().commit()
    monkeypatch.setattr(app.extensions['places'], 'details', lambda pid: {'displayName': {'text': 'Wingstop'}})
    choices = client.get('/api/catalogue-choices').json['choices']
    assert {'name': 'Wingstop', 'kind': 'Restaurant'} in choices
    assert not any(c['name'] == 'Google business' for c in choices)
    assert len(cards(client.get('/search?q=Wingstop'))) == 3
    assert cards(client.get('/search?q=Google%20business')) == []
    def unavailable(pid):
        raise LocationUnavailable('Unavailable')
    monkeypatch.setattr(app.extensions['places'], 'details', unavailable)
    choices = client.get('/api/catalogue-choices').json['choices']
    assert {'name': "AJ's Deli", 'kind': 'Restaurant'} in choices
    assert not any(c['name'] == 'Google business' for c in choices)


def test_long_existing_names_are_not_truncated(catalogue, app, client):
    name = 'Listed ' + 'f' * 113
    with app.app_context():
        db().execute('UPDATE fries SET name=? WHERE id=1', (name,))
        db().commit()
    assert {c[:2] for c in cards(client.get('/search', query_string={'q': name}))} == {
        ('restaurants', 1), ('fries', 1)}
    assert client.get('/search', query_string={'q': 'x' * 241}).status_code == 400
