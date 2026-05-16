CREATE TABLE locations (
    location_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country VARCHAR(100) DEFAULT 'India',
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    address_line TEXT,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    geo_point GEOGRAPHY(Point, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);