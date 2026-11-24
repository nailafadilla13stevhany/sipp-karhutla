CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'officer',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hotspots (
    id BIGSERIAL PRIMARY KEY,
    location_name VARCHAR(150) NOT NULL,
    geom GEOMETRY(Point, 4326) NOT NULL,
    hotspot_density_7d NUMERIC(8,3),
    consecutive_dry_days INTEGER,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patrols (
    id BIGSERIAL PRIMARY KEY,
    officer_id BIGINT REFERENCES users(id),
    officer_name VARCHAR(150) NOT NULL,
    location VARCHAR(150) NOT NULL,
    geom GEOMETRY(Point, 4326),
    patrol_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    location_name VARCHAR(150) NOT NULL,
    geom GEOMETRY(Point, 4326),
    hotspot_density_7d NUMERIC(8,3),
    consecutive_dry_days INTEGER,
    historical_fire_frequency NUMERIC(8,3),
    patrol_coverage_gap NUMERIC(8,3),
    ndvi_dryness_index NUMERIC(8,3),
    mean_temp_humidity_ratio NUMERIC(8,3),
    wind_speed_mean_3d NUMERIC(8,3),
    risk_level VARCHAR(20) NOT NULL,
    confidence NUMERIC(8,6),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recommendations (
    id BIGSERIAL PRIMARY KEY,
    prediction_id BIGINT REFERENCES predictions(id),
    location_name VARCHAR(150) NOT NULL,
    priority INTEGER NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    recommendation TEXT NOT NULL,
    reason TEXT,
    verification_status VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hotspots_geom ON hotspots USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_patrols_geom ON patrols USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_predictions_risk ON predictions (risk_level);
CREATE INDEX IF NOT EXISTS idx_recommendations_priority ON recommendations (priority);
