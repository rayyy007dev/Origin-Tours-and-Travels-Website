-- ORIGIN database schema. Safe to run more than once.

CREATE TABLE IF NOT EXISTS tours (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL CHECK (category IN ('domestic', 'international', 'umrah')),
    name TEXT NOT NULL,
    region TEXT NOT NULL DEFAULT '',
    duration TEXT NOT NULL DEFAULT '',
    price INTEGER CHECK (price IS NULL OR price >= 0),
    image TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL,
    features TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    cta_label TEXT NOT NULL DEFAULT 'Explore Package',
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE tours ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE tours ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_tours_category_sort
    ON tours (category, sort_order, id);

CREATE TABLE IF NOT EXISTS destinations (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    duration TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0),
    image TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL,
    link TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE destinations ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE destinations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_destinations_name
    ON destinations (name);

CREATE TABLE IF NOT EXISTS contact_messages (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    subject TEXT,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contact_messages_created_at
    ON contact_messages (created_at DESC);
