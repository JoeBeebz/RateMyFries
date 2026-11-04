import threading

from app import db
from test_app import app, client


def test_live_listing_lookups_overlap_and_are_not_cached(app, client, monkeypatch):
    """Four live calls must start together; repeated searches fetch fresh details."""
    with app.app_context():
        for index in range(4):
            db().execute(
                'INSERT INTO restaurants(name,address,name_key,address_key,google_place_id) '
                'VALUES(?,?,?,?,?)',
                (f'Diner {index}', '', f'diner {index}', f'address {index}', f'place_{index}'))
        db().commit()
    barrier = threading.Barrier(4, timeout=3)
    calls = []
    lock = threading.Lock()

    def details(place_id):
        with lock:
            calls.append(place_id)
        barrier.wait()
        return {'displayName': {'text': 'Live ' + place_id}}

    monkeypatch.setattr(app.extensions['places'], 'details', details)
    for _ in range(2):
        response = client.get('/search')
        assert response.status_code == 200
        for index in range(4):
            assert f'Live place_{index}'.encode() in response.data
        assert response.data.index(b'Live place_0') < response.data.index(b'Live place_3')
    assert sorted(calls) == sorted([f'place_{index}' for index in range(4)] * 2)
