import json,re
from app import db
from locations import LocationUnavailable
from test_app import app,client,listing,register


def payload(response):
    return json.loads(re.search(rb'id="restaurant-map-data"[^>]*>(.*?)</script>', response.data, re.S)[1])


def test_map_uses_same_search_results_and_public_fields(app,client):
    register(client)
    rid,fid=listing(client,latitude='42.5',longitude='-87.8')
    response=client.get('/search?q=Golden+Diner')
    assert response.status_code==200
    records=payload(response)
    assert len(records)==1 and records[0]['id']==rid
    assert records[0]['latitude']==42.5
    assert records[0]['fries'][0]['url']==f'/fries/{fid}'
    assert not {'email','user_id','search_names','address_key','google_place_id'} & records[0].keys()
    assert payload(client.get('/search?q=not-listed'))==[]
    assert 'nonce-' in response.headers['Content-Security-Policy']
    assert response.headers['Referrer-Policy']=='strict-origin-when-cross-origin'


def test_map_missing_and_failed_live_locations_keep_catalogue(app,client,monkeypatch):
    register(client)
    rid,fid=listing(client)
    with app.app_context():
        db().execute('UPDATE restaurants SET google_place_id=? WHERE id=?',('place-test',rid)); db().commit()
    def fail(*args): raise LocationUnavailable('Provider down')
    monkeypatch.setattr(app.extensions['places'],'details',fail)
    response=client.get('/search')
    assert response.status_code==200 and b'Golden Diner' in response.data
    assert payload(response)[0]['latitude'] is None
    assert b'Some live locations are unavailable' in response.data
    assert client.get(f'/restaurants/{rid}').status_code==200


def test_map_live_coordinates_are_not_persisted(app,client,monkeypatch):
    register(client);rid,_=listing(client)
    with app.app_context():
        db().execute('UPDATE restaurants SET google_place_id=? WHERE id=?',('place-test',rid));db().commit()
    monkeypatch.setattr(app.extensions['places'],'details',lambda _:dict(displayName={'text':'Live diner'},formattedAddress='Live address',location={'latitude':42,'longitude':-87}))
    assert payload(client.get('/search'))[0]['latitude']==42
    with app.app_context():
        row=db().execute('SELECT name,latitude FROM restaurants').fetchone()
        assert row['name']=='Golden Diner' and row['latitude'] is None


def test_server_places_key_never_exposed(app,client):
    app.config['GOOGLE_PLACES_API_KEY']='server-secret-sentinel'
    app.config['GOOGLE_MAPS_BROWSER_KEY']='browser-public-sentinel'
    page=client.get('/search').data
    assert b'server-secret-sentinel' not in page
    assert b'browser-public-sentinel' in page


def test_map_escapes_script_content(client):
    register(client);listing(client,name='</script><script>alert(1)</script>')
    response=client.get('/search')
    assert b'\\u003c/script\\u003e' in response.data
    assert payload(response)[0]['name']=='</script><script>alert(1)</script>'
