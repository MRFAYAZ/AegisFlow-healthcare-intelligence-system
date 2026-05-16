-- =====================================================
-- AegisFlow Emergency Intelligence Domain
-- =====================================================

CREATE TABLE emergency_cases (
    emergency_case_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID NOT NULL REFERENCES facilities(facility_id),
    medicine_id UUID NOT NULL REFERENCES medicine_master(medicine_id),
    shortage_score DECIMAL(5,2) NOT NULL CHECK (shortage_score >= 0),
    severity severity_enum NOT NULL,
    emergency_radius_km INTEGER DEFAULT 5 CHECK (emergency_radius_km BETWEEN 1 AND 50),
    required_quantity INTEGER CHECK (required_quantity > 0),
    available_quantity INTEGER DEFAULT 0
        CHECK (available_quantity >= 0),

    emergency_status VARCHAR(50) DEFAULT 'ACTIVE'
        CHECK (
            emergency_status IN (
                'ACTIVE',
                'MATCHING',
                'PARTIALLY_RESOLVED',
                'RESOLVED',
                'CLOSED'
            )
        ),

    triggered_by UUID
        REFERENCES users(user_id),

    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    resolved_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================

CREATE TABLE emergency_source_matches (
    match_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    emergency_case_id UUID NOT NULL
        REFERENCES emergency_cases(emergency_case_id)
        ON DELETE CASCADE,

    source_facility_id UUID NOT NULL
        REFERENCES facilities(facility_id),

    medicine_id UUID NOT NULL
        REFERENCES medicine_master(medicine_id),

    available_quantity INTEGER
        CHECK (available_quantity >= 0),

    transferable_quantity INTEGER
        CHECK (transferable_quantity >= 0),

    distance_km DECIMAL(10,2)
        CHECK (distance_km >= 0),

    donor_shortage_score DECIMAL(5,2),

    ranking_score DECIMAL(5,2),

    is_selected BOOLEAN DEFAULT FALSE,

    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);