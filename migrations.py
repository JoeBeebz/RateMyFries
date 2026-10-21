"""Additive, restart-safe upgrades for databases created before Sprint 3."""


def migrate(connection):
    columns = {row[1] for row in connection.execute('PRAGMA table_info(users)')}
    if 'role' not in columns:
        connection.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user','admin'))")
    if 'address' not in columns:
        connection.execute("ALTER TABLE users ADD COLUMN address TEXT NOT NULL DEFAULT ''")
    columns = {row[1] for row in connection.execute('PRAGMA table_info(restaurants)')}
    if 'google_place_id' not in columns:
        connection.execute('ALTER TABLE restaurants ADD COLUMN google_place_id TEXT')
    connection.execute('CREATE UNIQUE INDEX IF NOT EXISTS restaurant_google_place ON restaurants(google_place_id)')
