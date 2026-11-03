"""Operator-only, backed-up content import. Does not change application source/schema.

Run with --database PATH for a rolled-back preview; add --apply --backup-dir PATH
to save. Uses only Python's standard library and the existing application schema.
"""
import argparse
from collections import Counter
from datetime import date, datetime, timezone
import json
from pathlib import Path
import sqlite3
import unicodedata
from urllib.parse import urlsplit


def normalize(value):
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def public_url(value, optional=False):
    if optional and not value:
        return
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Sources and images must be public HTTPS URLs without credentials')
    if any(host in parsed.hostname for host in ('googleapis.com', 'googleusercontent.com')):
        raise ValueError('Do not persist Google content URLs in the catalogue')


def load_manifest(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if data['version'] != 1:
        raise ValueError('Unsupported catalogue version')
    date.fromisoformat(data['verified_on'])
    slugs, identities, places = set(), set(), set()
    styles = {'shoestring', 'steak', 'waffle', 'curly', 'crinkle-cut', 'straight-cut', 'other'}
    for item in data['restaurants']:
        slug = item['slug']
        identity = (normalize(item['name']), normalize(item['address']))
        place = item.get('google_place_id')
        if not all(identity) or slug in slugs or identity in identities or (place and place in places):
            raise ValueError('Empty or duplicate restaurant identity')
        slugs.add(slug)
        identities.add(identity)
        if place:
            places.add(place)
        for field in ('location_source', 'menu_source', 'photo_source', 'image_url'):
            public_url(item[field])
        if not item['photo_kind'].strip():
            raise ValueError('Restaurant photo needs a credit/context')
        names = set()
        for product in item['products']:
            name = normalize(product['name'])
            if not name or name in names or product['style'] not in styles:
                raise ValueError('Empty/duplicate product or invalid style')
            names.add(name)
            if type(product['seasoned']) is not bool:
                raise ValueError('seasoned must be a boolean')
            public_url(product['image_url'], optional=True)
            public_url(product['photo_source'], optional=not product['image_url'])
    return data


def restaurant_description(item, checked):
    return (f"{item['description']} Menu checked {checked}; availability may change. "
            f"Menu source: {source_label(item['menu_source'])} "
            f"Location source: {source_label(item['location_source'])} "
            f"Photo credit: {item['name']} — {item['photo_kind']} Source: {source_label(item['photo_source'])}")


def source_label(url):
    # Existing descriptions are plain text. Long ordering URLs force the mobile
    # grid beyond the viewport; retain full URLs in the manifest, show the host.
    return urlsplit(url).hostname


def product_description(item, restaurant, checked):
    text = (f"{item['description']} Menu checked {checked}; availability may change. "
            f"Menu source: {source_label(restaurant['menu_source'])}")
    if item['image_url']:
        text += (f" Photo credit: {restaurant['name']} (official menu image). "
                 f"Source: {source_label(item['photo_source'])}")
    return text


def import_catalogue(database, manifest, *, apply=False, backup_dir=None):
    """Insert missing content; fill blank metadata, preserving user-owned records.

    Match by durable place ID or normalized name/address, never integer IDs.
    Existing fry records are retained, including their IDs and attached reviews.
    """
    database = Path(database).resolve(strict=True)
    if apply and backup_dir is None:
        raise ValueError('--backup-dir is required when applying content')
    connection = sqlite3.connect(database, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys=ON')
    stats = Counter()
    backup = None
    try:
        # Validate the target before creating backups or mutating it.
        columns = {r['name'] for r in connection.execute('PRAGMA table_info(restaurants)')}
        if 'google_place_id' not in columns:
            raise ValueError('Run the application migrations before importing')
        if connection.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise ValueError('Database integrity check failed')
        if connection.execute('PRAGMA foreign_key_check').fetchone():
            raise ValueError('Existing foreign-key violation')
        if apply:
            folder = Path(backup_dir).resolve()
            folder.mkdir(parents=True, exist_ok=True)
            folder.chmod(0o700)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = folder / f'catalogue-{stamp}.sqlite3'
            backup.touch(mode=0o600, exist_ok=False)
            with sqlite3.connect(backup) as destination:
                connection.backup(destination)
            backup.chmod(0o600)
        connection.execute('BEGIN IMMEDIATE')
        for item in manifest['restaurants']:
            keys = (normalize(item['name']), normalize(item['address']))
            matches = connection.execute(
                'SELECT * FROM restaurants WHERE google_place_id=? OR (name_key=? AND address_key=?)',
                (item.get('google_place_id'), *keys)).fetchall()
            if len(matches) > 1:
                raise ValueError(f"Ambiguous existing restaurant: {item['name']}")
            description = restaurant_description(item, manifest['verified_on'])
            if not matches:
                restaurant_id = connection.execute(
                    'INSERT INTO restaurants(name,address,name_key,address_key,description,image_url,google_place_id) '
                    'VALUES(?,?,?,?,?,?,?)',
                    (item['name'], item['address'], *keys, description, item['image_url'], item.get('google_place_id'))
                ).lastrowid
                stats['restaurants_added'] += 1
            else:
                existing = matches[0]
                restaurant_id = existing['id']
                if existing['owner_id'] is not None:
                    raise ValueError(f"Refusing to edit an owned listing: {item['name']}")
                updates = {}
                # Replace the prior IDs-only import placeholders using independently sourced facts.
                if existing['name'] == 'Google business':
                    updates.update(name=item['name'], address=item['address'], name_key=keys[0], address_key=keys[1])
                for field, value in [('description', description), ('image_url', item['image_url']),
                                     ('google_place_id', item.get('google_place_id'))]:
                    if not existing[field] and value:
                        updates[field] = value
                if updates:
                    setters = ','.join(f'{field}=?' for field in updates)
                    connection.execute(f'UPDATE restaurants SET {setters} WHERE id=?', (*updates.values(), restaurant_id))
                    stats['restaurants_enriched'] += 1
            existing_names = {normalize(row['name']) for row in connection.execute(
                'SELECT name FROM fries WHERE restaurant_id=?', (restaurant_id,))}
            for product in item['products']:
                name_key = normalize(product['name'])
                if name_key in existing_names:
                    stats['products_existing'] += 1
                    continue
                connection.execute(
                    'INSERT INTO fries(restaurant_id,name,description,image_url,style,seasoned) VALUES(?,?,?,?,?,?)',
                    (restaurant_id, product['name'], product_description(product, item, manifest['verified_on']),
                     product['image_url'], product['style'], int(product['seasoned'])))
                existing_names.add(name_key)
                stats['products_added'] += 1
        if connection.execute('PRAGMA foreign_key_check').fetchone():
            raise ValueError('Import caused a foreign-key violation')
        if apply:
            connection.commit()
        else:
            connection.rollback()
        return {'applied': apply, 'backup': str(backup) if backup else None, **dict(stats)}
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, default=Path(__file__).resolve().parents[1] / 'data/kenosha-catalogue.json')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--backup-dir', type=Path)
    args = parser.parse_args()
    print(json.dumps(import_catalogue(args.database, load_manifest(args.manifest), apply=args.apply, backup_dir=args.backup_dir)))


if __name__ == '__main__':
    main()
