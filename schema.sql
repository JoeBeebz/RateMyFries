PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, username TEXT NOT NULL, username_key TEXT NOT NULL UNIQUE,
 email TEXT NOT NULL, email_key TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
 role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user','admin')), address TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS sessions (
 token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 expires INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS login_attempts (key TEXT PRIMARY KEY, attempts INTEGER NOT NULL, expires INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS restaurants (
 id INTEGER PRIMARY KEY, owner_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
 name TEXT NOT NULL, address TEXT NOT NULL, name_key TEXT NOT NULL, address_key TEXT NOT NULL,
 description TEXT NOT NULL DEFAULT '', image_url TEXT NOT NULL DEFAULT '',
 latitude REAL CHECK(latitude BETWEEN -90 AND 90), longitude REAL CHECK(longitude BETWEEN -180 AND 180),
 UNIQUE(name_key,address_key), CHECK ((latitude IS NULL) = (longitude IS NULL))
);
CREATE TABLE IF NOT EXISTS fries (
 id INTEGER PRIMARY KEY, restaurant_id INTEGER NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
 name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', image_url TEXT NOT NULL DEFAULT '',
 style TEXT NOT NULL CHECK(style IN ('shoestring','steak','waffle','curly','crinkle-cut','straight-cut','other')),
 seasoned INTEGER NOT NULL CHECK(seasoned IN (0,1)), price_cents INTEGER CHECK(price_cents >= 0)
);
CREATE TABLE IF NOT EXISTS reviews (
 id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 fry_id INTEGER NOT NULL REFERENCES fries(id) ON DELETE CASCADE,
 rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
 body TEXT CHECK(body IS NULL OR length(trim(body)) BETWEEN 1 AND 2000),
 context TEXT CHECK(context IN ('dine-in','takeout','delivery') OR context IS NULL),
 crispiness INTEGER CHECK(crispiness BETWEEN 1 AND 5), seasoning INTEGER CHECK(seasoning BETWEEN 1 AND 5),
 texture INTEGER CHECK(texture BETWEEN 1 AND 5), freshness INTEGER CHECK(freshness BETWEEN 1 AND 5),
 portion INTEGER CHECK(portion BETWEEN 1 AND 5), value INTEGER CHECK(value BETWEEN 1 AND 5),
 sauce INTEGER CHECK(sauce BETWEEN 1 AND 5), created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f','now')),
 UNIQUE(user_id,fry_id)
);
CREATE INDEX IF NOT EXISTS reviews_fry ON reviews(fry_id);
CREATE INDEX IF NOT EXISTS fries_restaurant ON fries(restaurant_id);

CREATE TABLE IF NOT EXISTS business_requests (
 id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
 name TEXT NOT NULL, address TEXT NOT NULL, name_key TEXT NOT NULL, address_key TEXT NOT NULL,
 description TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
 review_note TEXT NOT NULL DEFAULT '', reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
 restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE SET NULL,
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f','now')), reviewed_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS pending_business ON business_requests(name_key,address_key) WHERE status='pending';
CREATE TABLE IF NOT EXISTS admin_audit (
 id INTEGER PRIMARY KEY, actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
 target_id INTEGER REFERENCES users(id) ON DELETE SET NULL, action TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f','now'))
);
CREATE TABLE IF NOT EXISTS location_limits (key TEXT PRIMARY KEY, count INTEGER NOT NULL, expires INTEGER NOT NULL);
