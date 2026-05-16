-- =====================================================
-- AegisFlow Analytics & Intelligence Domain
-- =====================================================

CREATE TABLE shortage_scores (
    score_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    facility_id UUID NOT NULL
        REFERENCES facilities(facility_id),

    medicine_id UUID NOT NULL
        REFERENCES medicine_master(medicine_id),

    current_stock INTEGER NOT NULL
        CHECK (current_stock >= 0),

    daily_consumption_rate DECIMAL(10,2)
        CHECK (daily_consumption_rate >= 0),

    lead_time_days INTEGER
        CHECK (lead_time_days >= 0),

    safety_stock INTEGER
        CHECK (safety_stock >= 0),

    calculated_score DECIMAL(5,2) NOT NULL
        CHECK (calculated_score >= 0),

    severity severity_enum NOT NULL,

    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================

CREATE TABLE regional_shortage_index (
    rsi_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    state VARCHAR(100),

    district VARCHAR(100),

    city VARCHAR(100),

    medicine_id UUID
        REFERENCES medicine_master(medicine_id),

    average_shortage_score DECIMAL(5,2),

    affected_facilities INTEGER,

    emergency_facilities INTEGER DEFAULT 0,

    calculated_risk_level severity_enum,

    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================

CREATE TABLE outbreak_signals (
    outbreak_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    city VARCHAR(100),

    medicine_id UUID
        REFERENCES medicine_master(medicine_id),

    baseline_consumption DECIMAL(10,2),

    current_consumption DECIMAL(10,2),

    spike_percentage DECIMAL(10,2),

    affected_facilities INTEGER,

    confidence_score DECIMAL(5,2)
        CHECK (
            confidence_score BETWEEN 0 AND 100
        ),

    outbreak_status VARCHAR(50)
        DEFAULT 'DETECTED'
        CHECK (
            outbreak_status IN (
                'DETECTED',
                'UNDER_REVIEW',
                'CONFIRMED',
                'RESOLVED'
            )
        ),

    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================

CREATE TABLE seasonal_alerts (
    seasonal_alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    disease_name VARCHAR(255) NOT NULL,

    season_month INTEGER
        CHECK (
            season_month BETWEEN 1 AND 12
        ),

    medicine_id UUID
        REFERENCES medicine_master(medicine_id),

    recommended_stock_multiplier DECIMAL(5,2)
        CHECK (
            recommended_stock_multiplier > 0
        ),

    alert_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- STAR SCHEMA DIMENSIONS
-- =====================================================

CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,

    day INTEGER,

    month INTEGER,

    quarter INTEGER,

    year INTEGER,

    weekday VARCHAR(20),

    is_weekend BOOLEAN,

    season VARCHAR(50)
);

-- =====================================================
-- FACT TABLE
-- =====================================================

CREATE TABLE fact_inventory_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    date_id DATE
        REFERENCES dim_date(date_id),

    facility_id UUID
        REFERENCES facilities(facility_id),

    medicine_id UUID
        REFERENCES medicine_master(medicine_id),

    shortage_score DECIMAL(5,2),

    available_stock INTEGER,

    transfer_requests_count INTEGER DEFAULT 0,

    emergency_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);