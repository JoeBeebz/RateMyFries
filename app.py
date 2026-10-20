"""Rate My Fries: server-rendered Flask app backed by SQLite."""
import functools
import hashlib
import math
import os
import re
import secrets
import sqlite3
import time
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit

import click
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import CSRFProtect, generate_csrf
from locations import GooglePlaces, LocationUnavailable
from migrations import migrate

STYLES = ('shoestring', 'steak', 'waffle', 'curly', 'crinkle-cut', 'straight-cut', 'other')
QUALITIES = {'crispiness': 'Crispiness', 'seasoning': 'Seasoning', 'texture': 'Texture',
             'freshness': 'Freshness', 'portion': 'Portion size', 'value': 'Value for price', 'sauce': 'Sauce selection'}
CONTEXTS = ('dine-in', 'takeout', 'delivery')


def normalize(value):
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    a, b = math.radians(lat1), math.radians(lat2)
    h = math.sin((b-a)/2)**2 + math.cos(a)*math.cos(b)*math.sin(math.radians(lon2-lon1)/2)**2
    return 3958.7613 * 2 * math.asin(min(1, math.sqrt(max(0, h))))


def db():
    if 'db' not in g:
        from flask import current_app
        g.db = sqlite3.connect(current_app.config['DATABASE'], timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
        g.db.create_function('distance', 4, distance)
    return g.db


def rows(sql, params=()):
    return db().execute(sql, params).fetchall()


def one(sql, params=()):
    return db().execute(sql, params).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @functools.wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if g.user['role'] != 'admin':
            abort(403)
        return view(*args, **kwargs)
    return wrapped


class InvalidForm(ValueError):
    pass


def text_value(name, maximum, required=False):
    value = request.form.get(name, '').strip()
    label = name.replace('_', ' ').capitalize()
    if required and not value:
        raise InvalidForm(f'{label} is required.')
    if len(value) > maximum:
        raise InvalidForm(f'{label} must be {maximum} characters or fewer.')
    return value


def account_values():
    username = text_value('username', 30, True)
    email = text_value('email', 254, True)
    if not re.fullmatch(r'[A-Za-z0-9_]{3,30}', username):
        raise InvalidForm('Username must be 3–30 letters, numbers, or underscores.')
    local, separator, domain = email.partition('@')
    if (not separator or not local or '@' in domain or '.' not in domain
            or any(not part for part in domain.split('.')) or any(char.isspace() for char in email)):
        raise InvalidForm('Email must be a valid email address.')
    return username, email


def image_value():
    value = text_value('image_url', 1000)
    if value:
        parsed = urlsplit(value)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise InvalidForm('Image URL must be an HTTPS address without credentials.')
    return value


def numeric(value, label, low, high):
    try:
        result = float(value)
        if not math.isfinite(result) or not low <= result <= high:
            raise ValueError()
        return result
    except (ValueError, TypeError):
        raise InvalidForm(f'{label} must be between {low} and {high}.') from None


def price(value):
    if not value:
        return None
    try:
        amount = Decimal(value)
        if not amount.is_finite() or amount < 0 or amount > 10000 or amount * 100 != (amount * 100).to_integral_value():
            raise InvalidOperation()
        return int(amount * 100)
    except InvalidOperation:
        raise InvalidForm('Price must be 0–10000 with at most two decimal places.') from None


def score(name, required=False):
    value = request.form.get(name, '')
    if not value and not required:
        return None
    if value not in ('1', '2', '3', '4', '5'):
        raise InvalidForm(f'{name.capitalize()} must be a whole number from 1 to 5.')
    return int(value)


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    secret = os.environ.get('SECRET_KEY')
    if not secret:
        secret_path = Path(app.instance_path) / 'secret.key'
        try:
            with secret_path.open('x') as handle:
                handle.write(secrets.token_hex(32))
            secret_path.chmod(0o600)
        except FileExistsError:
            pass
        secret = secret_path.read_text()
    app.config.from_mapping(SECRET_KEY=secret, DATABASE=str(Path(app.instance_path)/'fries.sqlite3'),
                            SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                            SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE') == '1',
                            MAX_CONTENT_LENGTH=64*1024,
                            GOOGLE_PLACES_API_KEY=os.environ.get('GOOGLE_PLACES_API_KEY', ''),
                            WTF_CSRF_FIELD_NAME='csrf')
    if config:
        app.config.update(config)
    CSRFProtect(app)

    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop('db', None)
        if connection:
            connection.close()

    with app.app_context():
        db().executescript((Path(__file__).parent/'schema.sql').read_text())
        migrate(db())
        db().commit()

    app.extensions['places'] = GooglePlaces(app.config['GOOGLE_PLACES_API_KEY'])

    @app.before_request
    def load_identity_and_protect_forms():
        g.user = None
        token = session.get('auth')
        if token:
            g.user = one('SELECT u.* FROM users u JOIN sessions s ON u.id=s.user_id WHERE s.token=? AND s.expires>?',
                         (hashlib.sha256(token.encode()).hexdigest(), int(time.time())))
        if request.endpoint in ('search', 'suggest_addresses'):
            key = hashlib.sha256((request.remote_addr or 'local').encode()).hexdigest()
            now = int(time.time())
            db().execute('DELETE FROM location_limits WHERE expires<=?', (now,))
            db().execute('INSERT INTO location_limits VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=count+1', (key, now+60))
            db().commit()
            if one('SELECT count FROM location_limits WHERE key=?', (key,))['count'] > 60:
                abort(429)

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' https:; style-src 'self'; script-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
        if response.mimetype == 'text/html':
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.context_processor
    def context():
        return dict(csrf_token=generate_csrf, user=g.get('user'), styles=STYLES, qualities=QUALITIES, contexts=CONTEXTS)

    @app.template_filter('stars')
    def stars(value):
        return '★' * round(value or 0) + '☆' * (5-round(value or 0))

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        if g.get('db'):
            g.db.rollback()
        app.logger.error('Database operation failed (%s)', type(error).__name__)
        return render_template('error.html', code=503, message='We could not save or load this information. Please try again.'), 503

    for code in (400, 403, 404, 405, 409, 413, 429, 500):
        def handler(error, status=code):
            messages = {400: 'The request could not be accepted. Reload the page and try again.',
                        403: 'You do not have permission to change this content.', 404: 'This page or restaurant could not be found.',
                        409: 'This request has already been reviewed. Reload the inbox.', 405: 'That action is not available.', 413: 'That submission is too large.',
                        429: 'Too many attempts. Please try again in 15 minutes.', 500: 'Something went wrong. Please try again.'}
            return render_template('error.html', code=status, message=messages[status]), status
        app.register_error_handler(code, handler)

    def establish_session(user_id):
        session.clear()
        token = secrets.token_urlsafe(32)
        db().execute('DELETE FROM sessions WHERE expires<=?', (int(time.time()),))
        db().execute('INSERT INTO sessions VALUES (?,?,?)',
                     (hashlib.sha256(token.encode()).hexdigest(), user_id, int(time.time())+86400))
        db().commit()
        session['auth'] = token

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        error = None
        if request.method == 'POST':
            try:
                username, email = account_values()
                password = request.form.get('password', '')
                if not 12 <= len(password) <= 128:
                    raise InvalidForm('Password must be 12–128 characters.')
                if one('SELECT id FROM users WHERE username_key=? OR email_key=?', (normalize(username), normalize(email))):
                    raise InvalidForm('That username or email is already registered.')
                cursor = db().execute('INSERT INTO users(username,username_key,email,email_key,password_hash) VALUES(?,?,?,?,?)',
                                      (username, normalize(username), email, normalize(email), generate_password_hash(password)))
                db().commit()
                establish_session(cursor.lastrowid)
                flash('Your account is ready. Welcome to the fry club!', 'success')
                return redirect(url_for('profile'))
            except sqlite3.IntegrityError:
                db().rollback()
                error = 'That username or email is already registered.'
            except InvalidForm as exc:
                error = str(exc)
        return render_template('account.html', mode='register', error=error), 400 if error else 200

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            identity = normalize(request.form.get('identity', ''))[:254]
            key = hashlib.sha256((request.remote_addr or 'local').encode()).hexdigest()
            now = int(time.time())
            attempt = one('SELECT * FROM login_attempts WHERE key=?', (key,))
            if attempt and attempt['expires'] > now and attempt['attempts'] >= 10:
                abort(429)
            person = one('SELECT * FROM users WHERE username_key=? OR email_key=?', (identity, identity))
            password = request.form.get('password', '')
            # A real hash is checked for nonexistent accounts to reduce timing differences.
            hash_to_check = person['password_hash'] if person else app.config['DUMMY_HASH']
            valid = check_password_hash(hash_to_check, password[:129])
            if person and valid and len(password) <= 128:
                db().execute('DELETE FROM login_attempts WHERE key=?', (key,))
                establish_session(person['id'])
                return redirect(url_for('profile'))
            count = attempt['attempts']+1 if attempt and attempt['expires'] > now else 1
            expiry = attempt['expires'] if attempt and attempt['expires'] > now else now+900
            db().execute('INSERT OR REPLACE INTO login_attempts VALUES(?,?,?)', (key, count, expiry))
            db().commit()
            error = 'Email/username or password is incorrect.'
        return render_template('account.html', mode='login', error=error), 400 if error else 200

    app.config['DUMMY_HASH'] = generate_password_hash(secrets.token_urlsafe(24))

    @app.post('/logout')
    def logout():
        if session.get('auth'):
            db().execute('DELETE FROM sessions WHERE token=?', (hashlib.sha256(session['auth'].encode()).hexdigest(),))
            db().commit()
        session.clear()
        flash('You have logged out.', 'success')
        return redirect(url_for('home'))

    def review_list(where, params):
        return rows('SELECT v.*,u.username,f.name AS fry_name,f.restaurant_id FROM reviews v JOIN users u ON u.id=v.user_id '
                    'JOIN fries f ON f.id=v.fry_id WHERE '+where+' ORDER BY v.created_at DESC,v.id DESC', params)

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        error = None
        if request.method == 'POST':
            try:
                username, email = account_values()
                address = text_value('address', 240)
                db().execute('UPDATE users SET username=?,username_key=?,email=?,email_key=?,address=? WHERE id=?',
                             (username, normalize(username), email, normalize(email), address, g.user['id']))
                db().commit()
                flash('Profile saved.', 'success')
                return redirect(url_for('profile'))
            except sqlite3.IntegrityError:
                db().rollback()
                error = 'That username or email is already registered.'
            except InvalidForm as exc:
                error = str(exc)
        return render_template('profile.html', reviews=review_list('v.user_id=?', (g.user['id'],)), error=error), 400 if error else 200

    @app.route('/account/delete', methods=['GET', 'POST'])
    @login_required
    def delete_account():
        error = None
        if request.method == 'POST':
            if request.form.get('confirm') != 'yes' or not check_password_hash(g.user['password_hash'], request.form.get('password', '')[:129]):
                error = 'Enter your current password and confirm deletion.'
            elif g.user['role'] == 'admin' and one("SELECT COUNT(*) n FROM users WHERE role='admin'")['n'] == 1:
                error = 'Ask another administrator to take over before deleting the last administrator account.'
            else:
                db().execute('DELETE FROM users WHERE id=?', (g.user['id'],))
                db().commit()
                session.clear()
                flash('Your account, reviews, ratings, and sessions have been deleted.', 'success')
                return redirect(url_for('home'))
        return render_template('confirm.html', account=True, error=error), 400 if error else 200

    restaurant_sql = ('SELECT r.*,AVG(v.rating) AS average,COUNT(v.id) AS rating_count,MAX(v.created_at) AS latest '
                      'FROM restaurants r LEFT JOIN fries f ON f.restaurant_id=r.id LEFT JOIN reviews v ON v.fry_id=f.id ')
    fry_sql = ('SELECT f.*,r.name AS restaurant_name,AVG(v.rating) AS average,COUNT(v.id) AS rating_count, '
               'AVG(v.crispiness) AS crispiness_average,AVG(v.seasoning) AS seasoning_average '
               'FROM fries f JOIN restaurants r ON r.id=f.restaurant_id LEFT JOIN reviews v ON v.fry_id=f.id ')

    @app.get('/')
    def home():
        recent = rows(restaurant_sql+'WHERE v.body IS NOT NULL GROUP BY r.id ORDER BY latest DESC LIMIT 6')
        top = rows(fry_sql+'GROUP BY f.id HAVING COUNT(v.id)>0 ORDER BY average DESC,rating_count DESC,f.name LIMIT 6')
        return render_template('home.html', recent=[app.extensions['resolve_restaurant'](r) for r in recent], top=top)

    @app.get('/restaurants')
    def restaurants():
        return redirect(url_for('search', **request.args.to_dict()), code=302)

    def restaurant_or_404(restaurant_id):
        record = one(restaurant_sql+'WHERE r.id=? GROUP BY r.id', (restaurant_id,)) or abort(404)
        return app.extensions['resolve_restaurant'](record)

    @app.get('/restaurants/<int:restaurant_id>')
    def restaurant(restaurant_id):
        item = restaurant_or_404(restaurant_id)
        return render_template('restaurant.html', restaurant=item,
                               fries=rows(fry_sql+'WHERE f.restaurant_id=? GROUP BY f.id ORDER BY f.name', (restaurant_id,)),
                               reviews=review_list('f.restaurant_id=? AND v.body IS NOT NULL', (restaurant_id,)))

    @app.route('/restaurants/new', methods=['GET', 'POST'])
    @admin_required
    def add_restaurant():
        error = None
        duplicate = None
        if request.method == 'POST':
            try:
                name = text_value('name', 120, True)
                address = text_value('address', 240, True)
                description = text_value('description', 2000)
                image = image_value()
                latitude = longitude = None
                duplicate = one('SELECT id,name FROM restaurants WHERE name_key=? AND address_key=?', (normalize(name), normalize(address)))
                if duplicate:
                    raise InvalidForm('This restaurant is already listed. Open the existing restaurant below.')
                cursor = db().execute('INSERT INTO restaurants(owner_id,name,address,name_key,address_key,description,image_url,latitude,longitude) '
                                      'VALUES(?,?,?,?,?,?,?,?,?)', (g.user['id'],name,address,normalize(name),normalize(address),description,image,latitude,longitude))
                db().commit()
                flash('Restaurant added. Add its first fry option next.', 'success')
                return redirect(url_for('add_fry', restaurant_id=cursor.lastrowid))
            except sqlite3.IntegrityError:
                db().rollback()
                error = 'That restaurant is already listed.'
            except InvalidForm as exc:
                error = str(exc)
        return render_template('listing_form.html', mode='restaurant', error=error, duplicate=duplicate), 400 if error else 200

    @app.route('/restaurants/<int:restaurant_id>/fries/new', methods=['GET', 'POST'])
    @admin_required
    def add_fry(restaurant_id):
        item = restaurant_or_404(restaurant_id)
        error = None
        if request.method == 'POST':
            try:
                name = text_value('name', 120, True)
                description = text_value('description', 2000)
                style = request.form.get('style')
                seasoned = request.form.get('seasoned')
                if style not in STYLES or seasoned not in ('0','1'):
                    raise InvalidForm('Choose a fry style and seasoning option.')
                cursor = db().execute('INSERT INTO fries(restaurant_id,name,description,image_url,style,seasoned,price_cents) VALUES(?,?,?,?,?,?,?)',
                                      (restaurant_id,name,description,image_value(),style,int(seasoned),price(request.form.get('price',''))))
                db().commit()
                flash('Fry option added.', 'success')
                return redirect(url_for('fry', fry_id=cursor.lastrowid))
            except InvalidForm as exc:
                error = str(exc)
        return render_template('listing_form.html', mode='fry', restaurant=item, error=error), 400 if error else 200

    @app.get('/fries')
    def find_fries():
        return redirect(url_for('search', **request.args.to_dict()), code=302)

    def fry_or_404(fry_id):
        return one(fry_sql+'WHERE f.id=? GROUP BY f.id', (fry_id,)) or abort(404)

    @app.route('/fries/<int:fry_id>', methods=['GET','POST'])
    def fry(fry_id):
        item = fry_or_404(fry_id)
        existing = one('SELECT * FROM reviews WHERE fry_id=? AND user_id=?', (fry_id,g.user['id'])) if g.user else None
        error = None
        if request.method == 'POST':
            if not g.user:
                return redirect(url_for('login'))
            try:
                if existing and request.form.get('review_id') != str(existing['id']):
                    raise InvalidForm('You already rated these fries. Reload and use the edit form to update your existing rating.')
                rating = score('rating', True)
                mode = request.form.get('mode')
                if mode not in ('review', 'rating'):
                    raise InvalidForm('Choose Save review or Save rating only.')
                body = (text_value('body', 2000, True) if mode == 'review' else None)
                context = request.form.get('context') or None
                if context is not None and context not in CONTEXTS:
                    raise InvalidForm('Choose dine-in, takeout, or delivery.')
                values = [rating, body, context]+[score(k) for k in QUALITIES]
                if existing:
                    db().execute('UPDATE reviews SET rating=?,body=?,context=?,crispiness=?,seasoning=?,texture=?,freshness=?,portion=?,value=?,sauce=? WHERE id=? AND user_id=?',
                                 values+[existing['id'],g.user['id']])
                else:
                    db().execute('INSERT INTO reviews(rating,body,context,crispiness,seasoning,texture,freshness,portion,value,sauce,user_id,fry_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
                                 values+[g.user['id'],fry_id])
                db().commit()
                flash('Your review was saved.' if body else 'Your rating was saved.', 'success')
                return redirect(url_for('fry', fry_id=fry_id))
            except sqlite3.IntegrityError:
                db().rollback()
                error = 'A rating already exists. Reload to edit it.'
            except InvalidForm as exc:
                error = str(exc)
        return render_template('fry.html', fry=item, existing=existing, error=error,
                               reviews=review_list('v.fry_id=? AND v.body IS NOT NULL', (fry_id,))), 400 if error else 200

    @app.route('/reviews/<int:review_id>/delete', methods=['GET','POST'])
    @login_required
    def delete_review(review_id):
        item = one('SELECT * FROM reviews WHERE id=?', (review_id,)) or abort(404)
        if item['user_id'] != g.user['id']:
            abort(403)
        if request.method == 'POST':
            if request.form.get('confirm') != 'yes':
                return redirect(url_for('fry', fry_id=item['fry_id']))
            db().execute('DELETE FROM reviews WHERE id=? AND user_id=?', (review_id,g.user['id']))
            db().commit()
            flash('Your review and rating were removed.', 'success')
            return redirect(url_for('fry', fry_id=item['fry_id']))
        return render_template('confirm.html', account=False, review=item)

    @app.cli.command('seed-demo')
    def seed_demo():
        """Add clearly fictional, unrated demo listings; never creates user accounts."""
        with db():
            examples = [('Golden Hour Diner','100 Example Street, Demo City','A fictional neighborhood diner for trying out the app.','House shoestrings','shoestring',499),
                        ('The Fry Lab','200 Sample Avenue, Demo City','A fictional kitchen obsessed with the perfect crunch.','Waffle works','waffle',650),
                        ('Corner & Crisp','300 Practice Road, Demo City','A fictional counter-service spot with generous portions.','Curly classics','curly',575)]
            for name,address,description,fry_name,style,cost in examples:
                if one('SELECT id FROM restaurants WHERE name_key=? AND address_key=?',(normalize(name),normalize(address))):
                    continue
                cursor=db().execute('INSERT INTO restaurants(name,address,name_key,address_key,description) VALUES(?,?,?,?,?)',
                                    (name,address,normalize(name),normalize(address),description))
                db().execute('INSERT INTO fries(restaurant_id,name,description,style,seasoned,price_cents) VALUES(?,?,?,?,1,?)',
                             (cursor.lastrowid,fry_name,'Demo listing — add your own real restaurants to begin.',style,cost))
        click.echo('Fictional demo listings added. No reviews or ratings were fabricated.')

    from sprint import install
    install(app, restaurant_sql, fry_sql)

    @app.errorhandler(LocationUnavailable)
    def location_error(error):
        return render_template('error.html', code=503, message=str(error)), 503

    return app


if __name__ == '__main__':
    from waitress import serve
    serve(create_app(), host='127.0.0.1', port=int(os.environ.get('PORT', '5000')))
