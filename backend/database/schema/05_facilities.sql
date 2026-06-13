CREATE TABLE facilities (
    facility_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_name VARCHAR(255) NOT NULL,
    facility_type facility_type_enum NOT NULL,
    location_id UUID REFERENCES locations(location_id),
    license_number VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    emergency_contact VARCHAR(20),
    operating_hours VARCHAR(100),
    is_24x7 BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE facility_users (
    facility_user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID REFERENCES facilities(facility_id),
    user_id UUID REFERENCES users(user_id),
    assigned_role user_role_enum NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(facility_id, user_id)
);