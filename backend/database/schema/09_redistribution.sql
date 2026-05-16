CREATE TABLE transfer_requests (
    transfer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_facility_id UUID REFERENCES facilities(facility_id),
    to_facility_id UUID REFERENCES facilities(facility_id),
    medicine_id UUID REFERENCES medicine_master(medicine_id),
    requested_quantity INTEGER NOT NULL CHECK (requested_quantity > 0),
    approved_quantity INTEGER,
    transfer_status transfer_status_enum DEFAULT 'PENDING',
    cascade_safe BOOLEAN DEFAULT TRUE,
    match_score DECIMAL(5,2),
    transfer_distance_km DECIMAL(10,2),
    requested_by UUID REFERENCES users(user_id),
    approved_by UUID REFERENCES users(user_id),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE redistribution_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shortage_facility_id UUID REFERENCES facilities(facility_id),
    donor_facility_id UUID REFERENCES facilities(facility_id),
    medicine_id UUID REFERENCES medicine_master(medicine_id),
    recommended_quantity INTEGER,
    donor_surplus INTEGER,
    transfer_distance_km DECIMAL(10,2),
    redistribution_score DECIMAL(5,2),
    recommendation_reason TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);