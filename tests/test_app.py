import re
import sqlite3
import time

import pytest
from app import create_app, db, one, distance


@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING': True, 'SECRET_KEY': 'test-only', 'DATABASE': str(tmp_path/'test.sqlite')})


@pytest.fixture
def client(app):
    return app.test_client()


def token(client):
    response = client.get('/login')
    return re.search(rb'name="csrf-token" content="([^"]+)"', response.data)[1].decode()


def post(client, path, data=None, **kwargs):
    return client.post(path, data={'csrf': token(client), **(data or {})}, **kwargs)


def register(client, name='alice', email=None):
    return post(client, '/register', {'username': name, 'email': email or name+'@example.com', 'password': 'correct horse battery'})


def make_admin(client):
    with client.application.app_context():
        db().execute("UPDATE users SET role='admin' WHERE id=(SELECT user_id FROM sessions ORDER BY rowid DESC LIMIT 1)")
        db().commit()


def listing(client, name='Golden Diner', address='123 Main Street', **extra):
    make_admin(client)
    response = post(client, '/restaurants/new', {'name': name, 'address': address, **extra})
    assert response.status_code == 302
    rid = int(re.search(r'/restaurants/(\d+)', response.location)[1])
    if extra.get('latitude'):
        with client.application.app_context():
            db().execute('UPDATE restaurants SET latitude=?,longitude=? WHERE id=?', (float(extra['latitude']),float(extra['longitude']),rid))
            db().commit()
    response = post(client, f'/restaurants/{rid}/fries/new', {'name': 'Waffle fries', 'style': 'waffle', 'seasoned': '1', 'price': '4.99'})
    assert response.status_code == 302
    return rid, int(response.location.rsplit('/', 1)[1])


def rate(client, fid, **extra):
    return post(client, f'/fries/{fid}', {'rating': '4', 'mode': 'review', 'body': 'Great crunch!', **extra})


def test_accounts_profile_and_logout(app, client):
    assert register(client).status_code == 302
    with app.app_context():
        person = one('SELECT * FROM users')
        assert person['password_hash'].startswith('scrypt:')
        assert person['email'] == 'alice@example.com'
    assert b'alice' in client.get('/profile').data
    assert post(client, '/profile', {'username':'alice_new','email':'new@example.com'}).status_code == 302
    assert b'alice_new' in client.get('/profile').data
    with client.session_transaction() as s:
        old_auth = s['auth']
    post(client, '/logout')
    assert client.get('/profile').status_code == 302
    with client.session_transaction() as s:
        s['auth'] = old_auth
    assert client.get('/profile').status_code == 302  # server-side revocation
    assert post(client, '/login', {'identity':'new@example.com','password':'wrong'}).status_code == 400
    assert post(client, '/login', {'identity':'ALICE_NEW','password':'correct horse battery'}).status_code == 302


@pytest.mark.parametrize('name,email', [('ALICE','other@example.com'), ('other','ALICE@example.com')])
def test_duplicate_accounts(app, client, name, email):
    register(client)
    assert register(client,name,email).status_code == 400
    with app.app_context():
        assert one('SELECT COUNT(*) AS n FROM users')['n'] == 1


@pytest.mark.parametrize('change', [{'email':'not-an-email'}, {'username':' '}, {'password':'short'}, {'username':'<script>'}])
def test_registration_validation(client, change):
    values={'username':'alice','email':'alice@example.com','password':'correct horse battery',**change}
    assert post(client,'/register',values).status_code == 400


def test_profile_unique_validation(client):
    register(client)
    post(client,'/logout')
    register(client,'bobby')
    assert post(client,'/profile',{'username':'ALICE','email':'new@example.com'}).status_code == 400
    assert b'bobby' in client.get('/profile').data


def test_login_rate_limit(client):
    for _ in range(10):
        assert post(client,'/login',{'identity':'absent','password':'bad'}).status_code == 400
    assert post(client,'/login',{'identity':'absent','password':'bad'}).status_code == 429


def test_csrf_protects_changes(client):
    register(client)
    assert client.post('/logout').status_code == 400
    assert client.post('/restaurants/new',data={'name':'bad'}).status_code == 400
    assert client.get('/profile').status_code == 200


def test_restaurants_details_duplicates_and_fries(app, client):
    register(client)
    rid,fid=listing(client,description='Neighborhood favorite',latitude='40',longitude='-90')
    response=post(client,'/restaurants/new',{'name':'  GOLDEN   DINER ','address':'123 MAIN STREET'})
    assert response.status_code == 400
    assert b'Open Golden Diner' in response.data
    assert b'Waffle fries' in client.get(f'/restaurants/{rid}').data
    assert b'$4.99' in client.get(f'/fries/{fid}').data
    with app.app_context():
        assert one('SELECT COUNT(*) n FROM restaurants')['n']==1
        assert one('SELECT * FROM fries')['seasoned']==1
    assert post(client,f'/restaurants/{rid}/fries/new',{'name':'Plain','style':'straight-cut','seasoned':'0'}).status_code==302


@pytest.mark.parametrize('change',[{'image_url':'javascript:alert(1)'},{'image_url':'https://user:pass@example.com/a.png'}, {'address':'x'*241}, {'name':' '}])
def test_invalid_restaurant_data(client,change):
    register(client)
    make_admin(client)
    assert post(client,'/restaurants/new',{'name':'Test','address':'Here',**change}).status_code==400


@pytest.mark.parametrize('change',[{'price':'-1'},{'price':'1.999'},{'price':'NaN'},{'style':'invalid'},{'seasoned':'2'}])
def test_fry_validation(client,change):
    register(client)
    rid,_=listing(client)
    assert post(client,f'/restaurants/{rid}/fries/new',{'name':'Fries','style':'curly','seasoned':'0',**change}).status_code==400


def test_one_rating_update_delete_and_averages(app,client):
    register(client)
    rid,fid=listing(client)
    assert rate(client,fid,crispiness='5',seasoning='3',context='takeout').status_code==302
    with app.app_context():
        review=one('SELECT * FROM reviews')
        review_id=review['id']
        created=review['created_at']
    assert rate(client,fid).status_code==400  # duplicate is rejected
    assert rate(client,fid,rating='2',review_id=str(review_id),body='Updated',crispiness='1').status_code==302
    with app.app_context():
        assert one('SELECT COUNT(*) n FROM reviews')['n']==1
        assert one('SELECT * FROM reviews')['created_at']==created
    post(client,'/logout')
    register(client,'bobby')
    assert rate(client,fid,rating='5',crispiness='5').status_code==302
    page=client.get(f'/fries/{fid}').data
    assert b'3.5' in page and b'2 ratings' in page and b'Crispiness: 3.0 / 5' in page
    assert b'3.5' in client.get(f'/restaurants/{rid}').data
    assert b'Golden Diner' in client.get('/').data
    assert post(client,f'/reviews/{review_id}/delete',{'confirm':'yes'}).status_code==403
    assert client.get(f'/reviews/{review_id}/delete').status_code==403
    post(client,'/logout')
    post(client,'/login',{'identity':'alice','password':'correct horse battery'})
    assert b'Cancel' in client.get(f'/reviews/{review_id}/delete').data
    post(client,f'/reviews/{review_id}/delete',{'confirm':'no'})
    with app.app_context():
        assert one('SELECT id FROM reviews WHERE id=?',(review_id,))
    post(client,f'/reviews/{review_id}/delete',{'confirm':'yes'})
    assert b'5.0' in client.get(f'/fries/{fid}').data
    with app.app_context():
        assert not one('SELECT id FROM reviews WHERE id=?',(review_id,))


@pytest.mark.parametrize('change',[{'rating':'0'},{'rating':'6'},{'rating':'2.5'},{'body':' '},{'body':'x'*2001},{'crispiness':'6'},{'context':'other'},{'mode':'hacked'}])
def test_review_validation(client,change):
    register(client)
    _,fid=listing(client)
    assert rate(client,fid,**change).status_code==400


def test_rating_only_and_review_upgrade(app,client):
    register(client)
    _,fid=listing(client)
    assert rate(client,fid,mode='rating',body='').status_code==302
    with app.app_context():
        record=one('SELECT * FROM reviews')
        assert record['body'] is None
        ident=record['id']
    assert rate(client,fid,review_id=str(ident)).status_code==302
    assert b'Great crunch!' in client.get(f'/fries/{fid}').data
    assert rate(client,fid,review_id=str(ident),mode='rating',body='old draft').status_code==302
    with app.app_context():
        assert one('SELECT * FROM reviews')['body'] is None


def test_ownership_and_login_required(app,client):
    assert client.get('/restaurants/new').status_code==302
    register(client)
    rid,fid=listing(client)
    rate(client,fid,body='Alice original')
    with app.app_context():
        review_id=one('SELECT id FROM reviews')['id']
    post(client,'/logout')
    assert rate(client,fid).status_code==302
    register(client,'bobby')
    assert post(client,f'/restaurants/{rid}/fries/new',{'name':'Bad'}).status_code==403
    rate(client,fid,review_id=str(review_id),body='Bob contribution')
    with app.app_context():
        assert one('SELECT body FROM reviews WHERE id=?',(review_id,))['body']=='Alice original'
    assert b'Alice original' not in client.get('/profile').data


def test_search_sort_filters_distance_price(client):
    register(client)
    rid,fid=listing(client,'Zebra Diner',latitude='40',longitude='-90')
    rate(client,fid,rating='5')
    _,second=listing(client,'Alpha Cafe','999 Test Road',latitude='30',longitude='-80')
    rate(client,second,rating='2')
    data=client.get('/search').data
    assert data.index(b'Alpha Cafe')<data.index(b'Zebra Diner')
    data=client.get('/search?sort=highest').data
    assert data.index(b'Zebra Diner')<data.index(b'Alpha Cafe')
    data=client.get('/search?sort=lowest').data
    assert data.index(b'Alpha Cafe')<data.index(b'Zebra Diner')
    assert b'Alpha Cafe' not in client.get('/search?min_rating=4').data
    assert b'Zebra Diner' in client.get('/search?q=zebra').data
    assert b'No restaurants found' in client.get('/search?q=zzzz').data
    assert b'Alpha Cafe' not in post(client,'/search',{'lat':'40','lon':'-90','radius':'10'}).data
    assert b'Waffle fries' in client.get('/search?style=waffle&min_price=4&max_price=5').data
    assert b'No fries found' in client.get('/search?max_price=3').data
    assert b'No fries found' in client.get('/search?style=curly').data
    assert client.get('/search?min_price=10&max_price=1').status_code==400
    assert post(client,'/search',{'lat':'nan','lon':'0','radius':'5'}).status_code==400
    assert distance(40,-90,40,-90)==0


def test_all_detailed_scores_and_newest_first(app,client):
    register(client)
    _,fid=listing(client)
    rate(client,fid,body='Older review',crispiness='1',seasoning='3',texture='4',freshness='5',portion='2',value='4',sauce='3',context='delivery')
    post(client,'/logout')
    register(client,'bobby')
    rate(client,fid,body='Newer review',crispiness='5')
    data=client.get(f'/fries/{fid}').data
    assert data.index(b'Newer review')<data.index(b'Older review')
    assert b'Crispiness: 3.0 / 5' in data and b'Seasoning: 3.0 / 5' in data
    assert b'delivery' in data and b'Sauce selection 3/5' in data


def test_account_deletion_policy(app,client):
    register(client)
    rid,fid=listing(client)
    rate(client,fid)
    assert post(client,'/account/delete',{'confirm':'yes','password':'wrong'}).status_code==400
    with app.app_context():
        db().execute("UPDATE users SET role='user'")
        db().commit()
    assert post(client,'/account/delete',{'confirm':'yes','password':'correct horse battery'}).status_code==302
    with app.app_context():
        assert one('SELECT COUNT(*) n FROM users')['n']==0
        assert one('SELECT COUNT(*) n FROM reviews')['n']==0
        assert one('SELECT COUNT(*) n FROM sessions')['n']==0
        assert one('SELECT owner_id FROM restaurants WHERE id=?',(rid,))['owner_id'] is None
    assert b'No ratings yet' in client.get(f'/fries/{fid}').data
    assert post(client,'/login',{'identity':'alice','password':'correct horse battery'}).status_code==400


def test_persistence_and_database_constraints(app,client):
    register(client)
    rid,fid=listing(client)
    rate(client,fid)
    restarted=create_app({'TESTING':True,'SECRET_KEY':'test-only','DATABASE':app.config['DATABASE']})
    assert b'Great crunch!' in restarted.test_client().get(f'/fries/{fid}').data
    with app.app_context():
        with pytest.raises(sqlite3.IntegrityError):
            db().execute("INSERT INTO reviews(user_id,fry_id,rating) VALUES(999,?,4)",(fid,))
        db().rollback()
        with pytest.raises(sqlite3.IntegrityError):
            db().execute('UPDATE reviews SET rating=6')
        db().rollback()


def test_escaping_errors_headers_and_routes(app,client):
    register(client)
    rid,fid=listing(client,description='<script>alert(1)</script>')
    rate(client,fid,body='<img src=x onerror=alert(1)>')
    assert b'<script>alert(1)</script>' not in client.get(f'/restaurants/{rid}').data
    assert b'&lt;img' in client.get(f'/fries/{fid}').data
    for path in ('/not-real','/restaurants/9999','/fries/9999'):
        assert client.get(path).status_code==404
        assert b'Back to home' in client.get(path).data
    assert client.get('/logout').status_code==405
    response=client.get('/')
    assert response.headers['X-Frame-Options']=='DENY'
    assert 'no-store' in response.headers['Cache-Control']
    with app.app_context():
        db().execute('ALTER TABLE restaurants RENAME TO unavailable')
        db().commit()
    response=client.get('/search')
    assert response.status_code==503
    assert b'OperationalError' not in response.data and b'SELECT' not in response.data


def test_demo_seed_is_idempotent_and_has_no_fake_reviews(app):
    runner=app.test_cli_runner()
    assert runner.invoke(args=['seed-demo']).exit_code==0
    assert runner.invoke(args=['seed-demo']).exit_code==0
    with app.app_context():
        assert one('SELECT COUNT(*) n FROM restaurants')['n']==3
        assert one('SELECT COUNT(*) n FROM reviews')['n']==0
