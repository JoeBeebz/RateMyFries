"""Discovery and moderated business workflows introduced in Sprint 3."""
import re
import sqlite3
from urllib.parse import quote

import click
from flask import abort, flash, g, jsonify, redirect, render_template, request, url_for

from app import (STYLES, InvalidForm, admin_required, db, distance, login_required,
                 normalize, numeric, one, price, rows, text_value)
from locations import LocationUnavailable


def install(app, restaurant_sql, fry_sql):
    def places():
        return app.extensions['places']

    def resolve_restaurant(record):
        item = dict(record)
        item['attributions'] = []
        if item.get('google_place_id'):
            details = places().details(item['google_place_id'])
            item.update(name=details.get('displayName', {}).get('text', 'Google business'),
                        address=details.get('formattedAddress', ''),
                        latitude=details.get('location', {}).get('latitude'),
                        longitude=details.get('location', {}).get('longitude'),
                        attributions=[a.get('provider', '') for a in details.get('attributions', [])],
                        maps_url='https://www.google.com/maps/search/?api=1&query=Google&query_place_id=' + quote(item['google_place_id']))
        return item

    app.extensions['resolve_restaurant'] = resolve_restaurant

    @app.get('/privacy')
    def policies():
        return render_template('policies.html')

    @app.route('/search', methods=['GET', 'POST'])
    def search():
        values = request.form if request.method == 'POST' else request.args
        filters = {key: values.get(key, '').strip() for key in
                   ('q', 'style', 'min_price', 'max_price', 'min_rating', 'sort', 'radius')}
        filters['q'] = filters['q'][:100]
        # Private address and device location are accepted only in POST bodies.
        address = values.get('address', '').strip() if request.method == 'POST' else ''
        saved = request.method == 'POST' and values.get('use_saved') == '1'
        error, restaurants, fries = None, [], []
        try:
            if len(address) > 240:
                raise InvalidForm('Address must be 240 characters or fewer.')
            origin = None
            if saved:
                if not g.user:
                    abort(403)
                if not g.user['address']:
                    raise InvalidForm('Save an address in your profile first.')
                address = g.user['address']
            if address:
                origin = places().geocode(address)
            elif request.method == 'POST' and (values.get('lat') or values.get('lon')):
                origin = (numeric(values.get('lat'), 'Location latitude', -90, 90),
                          numeric(values.get('lon'), 'Location longitude', -180, 180))
            radius = numeric(filters['radius'] or 10, 'Radius in miles', 0.1, 100) if origin else None
            if filters['radius'] and not origin:
                raise InvalidForm('Enter an address, use your saved address, or choose your current location for a radius search.')
            minimum = numeric(filters['min_rating'] or 0, 'Minimum rating', 0, 5)
            low, high = price(filters['min_price']), price(filters['max_price'])
            if low is not None and high is not None and low > high:
                raise InvalidForm('Minimum price cannot exceed maximum price.')
            if filters['style'] and filters['style'] not in STYLES:
                raise InvalidForm('Choose a listed fry style.')
            if filters['sort'] not in ('', 'name', 'highest', 'lowest', 'nearest'):
                raise InvalidForm('Choose a listed sort order.')
            if filters['sort'] == 'nearest' and not origin:
                raise InvalidForm('Choose a location before sorting by distance.')
            listings = [resolve_restaurant(r) for r in rows(restaurant_sql + 'GROUP BY r.id')]
            by_id = {r['id']: r for r in listings}
            options = [dict(f) for f in rows(fry_sql + 'GROUP BY f.id')]
            q = normalize(filters['q'])
            matching = []
            for f in options:
                r = by_id[f['restaurant_id']]
                f['restaurant_name'] = r['name']
                if q and not any(q in normalize(v) for v in (r['name'], f['name'], f['style'])):
                    continue
                if filters['style'] and f['style'] != filters['style']:
                    continue
                if low is not None and (f['price_cents'] is None or f['price_cents'] < low):
                    continue
                if high is not None and (f['price_cents'] is None or f['price_cents'] > high):
                    continue
                if minimum and (f['average'] is None or f['average'] < minimum):
                    continue
                matching.append(f)
            match_ids = {f['restaurant_id'] for f in matching}
            fry_filter = bool(filters['style'] or low is not None or high is not None)
            for r in listings:
                if (fry_filter or q) and r['id'] not in match_ids and (fry_filter or q not in normalize(r['name'])):
                    continue
                if minimum and (r['average'] is None or r['average'] < minimum):
                    continue
                r['miles'] = None
                if origin:
                    coords = (r['latitude'], r['longitude'])
                    if None in coords:
                        coords = places().geocode(r['address'])
                    r['miles'] = distance(*origin, *coords)
                    if r['miles'] > radius:
                        continue
                restaurants.append(r)
            visible = {r['id'] for r in restaurants}
            fries = [f for f in matching if f['restaurant_id'] in visible]

            def sort_key(item):
                if filters['sort'] == 'nearest':
                    miles = item.get('miles', by_id.get(item.get('restaurant_id'), {}).get('miles'))
                    return (miles is None, miles or 0, normalize(item['name']))
                average = item['average']
                if filters['sort'] in ('highest', 'lowest'):
                    return (average is None, (-(average or 0) if filters['sort'] == 'highest' else average or 0), normalize(item['name']))
                return (False, 0, normalize(item['name']))

            restaurants.sort(key=sort_key)
            fries.sort(key=sort_key)
        except (InvalidForm, LocationUnavailable) as exc:
            error = str(exc)
            restaurants, fries = [], []
        return render_template('search.html', filters=filters, restaurants=restaurants, fries=fries,
                               error=error, used_saved=saved), 400 if error else 200

    @app.post('/api/address-suggestions')
    def suggest_addresses():
        try:
            text = text_value('input', 240)
            token = text_value('token', 36, True)
            if not re.fullmatch(r'[A-Za-z0-9-]{16,36}', token):
                raise InvalidForm('Invalid suggestion session.')
            suggestions = places().suggest(text, token) if len(text) >= 3 else []
            return jsonify(suggestions=suggestions)
        except InvalidForm as exc:
            return jsonify(error=str(exc)), 400
        except LocationUnavailable as exc:
            return jsonify(error=str(exc)), 503

    @app.route('/business-requests/new', methods=['GET', 'POST'])
    @login_required
    def submit_business():
        error = None
        if request.method == 'POST':
            try:
                name, address = text_value('name', 120, True), text_value('address', 240, True)
                description = text_value('description', 2000)
                keys = (normalize(name), normalize(address))
                if one('SELECT id FROM restaurants WHERE name_key=? AND address_key=?', keys):
                    raise InvalidForm('That business is already listed.')
                if one("SELECT id FROM business_requests WHERE user_id=? AND created_at>datetime('now','-1 hour') GROUP BY user_id HAVING COUNT(*)>=5", (g.user['id'],)):
                    raise InvalidForm('You can submit up to five business requests per hour. Please try again later.')
                db().execute('INSERT INTO business_requests(user_id,name,address,name_key,address_key,description) VALUES(?,?,?,?,?,?)',
                             (g.user['id'], name, address, *keys, description))
                db().commit()
                flash('Business submitted. An administrator will review it before publication.', 'success')
                return redirect(url_for('my_requests'))
            except sqlite3.IntegrityError:
                db().rollback()
                error = 'A request for that business is already awaiting review.'
            except InvalidForm as exc:
                error = str(exc)
        return render_template('business_form.html', error=error), 400 if error else 200

    @app.get('/business-requests')
    @login_required
    def my_requests():
        return render_template('requests.html', requests=rows('SELECT * FROM business_requests WHERE user_id=? ORDER BY id DESC', (g.user['id'],)), admin=False)

    @app.get('/admin/inbox')
    @admin_required
    def admin_inbox():
        return render_template('requests.html', requests=rows('SELECT b.*,u.username FROM business_requests b LEFT JOIN users u ON b.user_id=u.id ORDER BY b.status=\'pending\' DESC,b.id DESC'), admin=True)

    @app.post('/admin/requests/<int:request_id>/review')
    @admin_required
    def review_business(request_id):
        try:
            decision = request.form.get('decision')
            if decision not in ('approved', 'rejected'):
                raise InvalidForm('Choose approve or reject.')
            note = text_value('review_note', 1000)
            # Serialize the read/decision/insert; a second reviewer sees the final status.
            with db():
                db().execute('BEGIN IMMEDIATE')
                item = one('SELECT * FROM business_requests WHERE id=?', (request_id,)) or abort(404)
                if item['status'] != 'pending':
                    abort(409)
                rid = None
                if decision == 'approved':
                    existing = one('SELECT id FROM restaurants WHERE name_key=? AND address_key=?', (item['name_key'], item['address_key']))
                    if existing:
                        rid = existing['id']
                    else:
                        rid = db().execute('INSERT INTO restaurants(owner_id,name,address,name_key,address_key,description) VALUES(?,?,?,?,?,?)',
                                           (g.user['id'], item['name'], item['address'], item['name_key'], item['address_key'], item['description'])).lastrowid
                db().execute("UPDATE business_requests SET status=?,review_note=?,reviewed_by=?,restaurant_id=?,reviewed_at=strftime('%Y-%m-%d %H:%M:%f','now') WHERE id=?",
                             (decision, note, g.user['id'], rid, request_id))
            flash('Business request ' + decision + '.', 'success')
        except InvalidForm as exc:
            return render_template('error.html', code=400, message=str(exc)), 400
        return redirect(url_for('admin_inbox'))

    @app.route('/admin/accounts', methods=['GET', 'POST'])
    @admin_required
    def admin_accounts():
        error = None
        if request.method == 'POST':
            try:
                username = text_value('username', 30, True)
                person = one('SELECT id,role FROM users WHERE username_key=?', (normalize(username),))
                if not person:
                    raise InvalidForm('Ask this person to register a regular account first.')
                with db():
                    changed = db().execute("UPDATE users SET role='admin' WHERE id=? AND role='user'", (person['id'],)).rowcount
                    if changed:
                        db().execute("INSERT INTO admin_audit(actor_id,target_id,action) VALUES(?,?,'promote')", (g.user['id'], person['id']))
                flash('Account is now an administrator.' if changed else 'This account is already an administrator.', 'success')
                return redirect(url_for('admin_accounts'))
            except InvalidForm as exc:
                error = str(exc)
        return render_template('admins.html', admins=rows("SELECT username FROM users WHERE role='admin' ORDER BY username"), error=error), 400 if error else 200

    @app.cli.command('bootstrap-admin')
    @click.argument('username')
    def bootstrap_admin(username):
        """Operator-only initial setup; later admins must be authorized by an admin."""
        with db():
            db().execute('BEGIN IMMEDIATE')
            if one("SELECT id FROM users WHERE role='admin'"):
                raise click.ClickException('An administrator already exists. Use the admin accounts page.')
            user = one('SELECT id FROM users WHERE username_key=?', (normalize(username),))
            if not user:
                raise click.ClickException('Register this account before bootstrapping it.')
            db().execute("UPDATE users SET role='admin' WHERE id=?", (user['id'],))
            db().execute("INSERT INTO admin_audit(target_id,action) VALUES(?,'operator-bootstrap')", (user['id'],))
        click.echo('Initial administrator configured. Subsequent admins require administrator authorization.')

    @app.cli.command('import-kenosha')
    def import_kenosha():
        """Discover Kenosha restaurants; persist only Google place IDs."""
        try:
            results = places().kenosha()
            ids = list(dict.fromkeys(p['id'] for p in results if re.fullmatch(r'[A-Za-z0-9_-]{1,255}', p.get('id', ''))))
            if len(ids) < 3:
                raise LocationUnavailable('Google returned fewer than three businesses. No import was performed.')
            with db():
                for pid in ids:
                    db().execute('INSERT OR IGNORE INTO restaurants(name,address,name_key,address_key,google_place_id) VALUES(?,?,?,?,?)',
                                 ('Google business', '', 'google:' + pid, '', pid))
            click.echo(f'{len(ids)} Google place IDs available. Names and addresses are fetched live; no reviews or menus were invented.')
        except LocationUnavailable as exc:
            raise click.ClickException(str(exc)) from None
