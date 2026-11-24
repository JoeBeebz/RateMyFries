import sqlite3
import pytest
from app import db,one,create_app
from migrations import migrate
from test_app import app,client,listing,register,post,rate


def test_five_scores_aggregate_missing_values_edit_delete(app,client):
    register(client);_,fid=listing(client)
    assert rate(client,fid,crispiness='5',seasoning='4',freshness='3',taste='2',value='1',texture='4').status_code==302
    with app.app_context(): rid=one('SELECT id FROM reviews')['id']
    post(client,'/logout');register(client,'bobby')
    assert rate(client,fid,rating='2',taste='4',value='5').status_code==302
    page=client.get(f'/fries/{fid}').data
    assert b'3.0 / 5' in page and b'2 ratings' in page
    # AVG ignores absent dimensions; overall stays independent from qualities.
    with app.app_context():
        row=one('SELECT AVG(rating) overall,AVG(crispiness) crisp,COUNT(crispiness) n,AVG(taste) taste,AVG(value) value FROM reviews')
        assert tuple(row)==(3,5,1,3,3)
        own=one('SELECT id FROM reviews WHERE user_id=(SELECT id FROM users WHERE username=?)',('bobby',))['id']
    assert rate(client,fid,review_id=str(own),rating='5',taste='5',value='').status_code==302
    with app.app_context(): assert one('SELECT AVG(taste),AVG(value) FROM reviews')[:]==(3.5,1.0)
    assert post(client,f'/reviews/{own}/delete',{'confirm':'yes'}).status_code==302
    with app.app_context(): assert one('SELECT COUNT(*) n FROM reviews')['n']==1
    post(client,'/logout');post(client,'/login',{'identity':'alice','password':'correct horse battery'})
    # An old client omitting the new field must not erase an existing taste score.
    assert rate(client,fid,review_id=str(rid),rating='3').status_code==302
    with app.app_context():
        review=one('SELECT * FROM reviews');assert review['taste']==2 and review['texture']==4


@pytest.mark.parametrize('bad',['0','6','2.5','nan','oops'])
def test_taste_validation_is_atomic(app,client,bad):
    register(client);_,fid=listing(client)
    assert rate(client,fid,taste=bad).status_code==400
    with app.app_context(): assert one('SELECT COUNT(*) n FROM reviews')['n']==0


def test_rating_only_keeps_qualities_without_review_text(app,client):
    register(client);_,fid=listing(client)
    assert rate(client,fid,mode='rating',taste='5',freshness='4').status_code==302
    with app.app_context():
        row=one('SELECT body,taste,freshness,rating FROM reviews');assert tuple(row)==(None,5,4,4)
    assert b'Not rated yet' in client.get(f'/fries/{fid}').data


def test_migration_preserves_legacy_review_and_is_restart_safe(tmp_path):
    path=tmp_path/'old.sqlite'
    app=create_app({'TESTING':True,'DATABASE':str(path),'SECRET_KEY':'test'})
    client=app.test_client();register(client);_,fid=listing(client);rate(client,fid,crispiness='5',texture='3')
    with sqlite3.connect(path) as conn:
        # Simulate the actual pre-Sprint-5 schema, with populated rows.
        conn.execute('ALTER TABLE reviews DROP COLUMN taste');conn.commit()
        before=conn.execute('SELECT * FROM reviews').fetchall()
        cols=[r[1] for r in conn.execute('PRAGMA table_info(reviews)')]
        migrate(conn);migrate(conn);conn.commit()
        after=conn.execute('SELECT '+','.join(cols)+' FROM reviews').fetchall()
        assert before==after and conn.execute('SELECT taste FROM reviews').fetchone()[0] is None
        assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not conn.execute('PRAGMA foreign_key_check').fetchall()
        with pytest.raises(sqlite3.IntegrityError): conn.execute('UPDATE reviews SET taste=2.5')
