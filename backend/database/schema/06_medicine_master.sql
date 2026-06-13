CREATE TABLE medicine_master (
    medicine_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medicine_code VARCHAR(50) UNIQUE NOT NULL,
    medicine_name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    category VARCHAR(100),
    dosage_form VARCHAR(50),
    strength VARCHAR(50),
    manufacturer VARCHAR(255),
    prescription_required BOOLEAN DEFAULT FALSE,
    is_critical BOOLEAN DEFAULT FALSE,
    storage_conditions TEXT,
    standard_lead_time_days INTEGER CHECK (standard_lead_time_days >= 0),
    safety_stock_days INTEGER DEFAULT 3,
    unit_price DECIMAL(10,2) CHECK (unit_price >= 0),
    expiry_alert_days INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE medicine_generic_mapping (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branded_medicine_id UUID REFERENCES medicine_master(medicine_id),
    generic_medicine_id UUID REFERENCES medicine_master(medicine_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);