import copy
from pathlib import Path
import sqlite3

import pytest

from migrations import migrate
from tools.import_catalogue import import_catalogue, load_manifest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def catalogue_db(tmp_path):
    path = tmp_path / 'fries.sqlite3'
    with sqlite3.connect(path) as connection:
        connection.executescript((ROOT / 'schema.sql').read_text())
        migrate(connection)
        connection.execute("INSERT INTO users(id,username,username_key,email,email_key,password_hash) "
                           "VALUES(1,'existing','existing','existing@example.com','existing@example.com','hash')")
        connection.execute("INSERT INTO restaurants(id,owner_id,name,address,name_key,address_key) "
                           "VALUES(1,1,'Keep Me','User address','keep me','user address')")
    return path


def test_catalogue_dry_run_and_backup(catalogue_db, tmp_path):
    manifest = load_manifest(ROOT / 'data/kenosha-catalogue.json')
    before = catalogue_db.read_bytes()
    preview = import_catalogue(catalogue_db, manifest)
    assert preview['restaurants_added'] == 14
    assert preview['products_added'] == 37
    assert catalogue_db.read_bytes() == before
    with pytest.raises(ValueError, match='backup-dir'):
        import_catalogue(catalogue_db, manifest, apply=True)
    saved = import_catalogue(catalogue_db, manifest, apply=True, backup_dir=tmp_path / 'backups')
    with sqlite3.connect(saved['backup']) as backup:
        assert backup.execute('SELECT COUNT(*) FROM restaurants').fetchone()[0] == 1
        assert backup.execute('SELECT COUNT(*) FROM fries').fetchone()[0] == 0
    with sqlite3.connect(catalogue_db) as connection:
        assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert connection.execute('SELECT name FROM restaurants WHERE id=1').fetchone()[0] == 'Keep Me'


def test_repeat_import_preserves_reviews_and_existing_content(catalogue_db, tmp_path):
    manifest = load_manifest(ROOT / 'data/kenosha-catalogue.json')
    with sqlite3.connect(catalogue_db) as connection:
        connection.execute("INSERT INTO restaurants(id,name,address,name_key,address_key,google_place_id) "
                           "VALUES(2,'Google business','','google business','place-2',?)",
                           (manifest['restaurants'][0]['google_place_id'],))
    saved = import_catalogue(catalogue_db, manifest, apply=True, backup_dir=tmp_path / 'backups')
    assert saved['restaurants_enriched'] == 1
    assert saved['restaurants_added'] == 13
    with sqlite3.connect(catalogue_db) as connection:
        assert connection.execute('SELECT name FROM restaurants WHERE id=2').fetchone()[0] == "MelKat's"
        fry_id = connection.execute('SELECT id FROM fries LIMIT 1').fetchone()[0]
        connection.execute("INSERT INTO reviews(user_id,fry_id,rating,body) VALUES(1,?,4,'Keep this review')", (fry_id,))
        connection.execute("UPDATE fries SET description='Admin edit' WHERE id=?", (fry_id,))
    again = import_catalogue(catalogue_db, manifest, apply=True, backup_dir=tmp_path / 'backups')
    assert again.get('restaurants_added', 0) == again.get('restaurants_enriched', 0) == again.get('products_added', 0) == 0
    assert again['products_existing'] == 37
    with sqlite3.connect(catalogue_db) as connection:
        assert connection.execute('SELECT description FROM fries WHERE id=?', (fry_id,)).fetchone()[0] == 'Admin edit'
        assert connection.execute('SELECT fry_id,body FROM reviews').fetchone() == (fry_id, 'Keep this review')
        assert connection.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 1


def test_owned_listing_conflict_rolls_back_entire_import(catalogue_db, tmp_path):
    manifest = load_manifest(ROOT / 'data/kenosha-catalogue.json')
    with sqlite3.connect(catalogue_db) as connection:
        connection.execute('UPDATE restaurants SET google_place_id=? WHERE id=1',
                           (manifest['restaurants'][-1]['google_place_id'],))
    with pytest.raises(ValueError, match='owned listing'):
        import_catalogue(catalogue_db, manifest, apply=True, backup_dir=tmp_path / 'backups')
    with sqlite3.connect(catalogue_db) as connection:
        assert connection.execute('SELECT COUNT(*) FROM restaurants').fetchone()[0] == 1
        assert connection.execute('SELECT COUNT(*) FROM fries').fetchone()[0] == 0


@pytest.mark.parametrize('change', ['duplicate', 'google_photo', 'missing_credit'])
def test_manifest_rejects_ambiguous_or_uncredited_content(tmp_path, change):
    import json
    manifest = load_manifest(ROOT / 'data/kenosha-catalogue.json')
    if change == 'duplicate':
        manifest['restaurants'].append(copy.deepcopy(manifest['restaurants'][0]))
    elif change == 'google_photo':
        manifest['restaurants'][0]['image_url'] = 'https://places.googleapis.com/v1/places/id/photos/name/media'
    else:
        manifest['restaurants'][0]['products'][0]['photo_source'] = ''
    path = tmp_path / 'bad.json'
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        load_manifest(path)
