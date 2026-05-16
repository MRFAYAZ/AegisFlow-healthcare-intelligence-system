CREATE TABLE inventory_batches (
    batch_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID REFERENCES facilities(facility_id),
    medicine_id UUID REFERENCES medicine_master(medicine_id),
    batch_number VARCHAR(100) NOT NULL,
    supplier_name VARCHAR(255),
    manufacturing_date DATE,
    expiry_date DATE NOT NULL,
    quantity_received INTEGER NOT NULL CHECK (quantity_received >= 0),
    quantity_available INTEGER NOT NULL CHECK (quantity_available >= 0),
    quantity_reserved INTEGER DEFAULT 0 CHECK (quantity_reserved >= 0),
    unit_cost DECIMAL(10,2) CHECK (unit_cost >= 0),
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_current (
    inventory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID REFERENCES facilities(facility_id),
    medicine_id UUID REFERENCES medicine_master(medicine_id),
    total_stock INTEGER NOT NULL CHECK (total_stock >= 0),
    available_stock INTEGER NOT NULL CHECK (available_stock >= 0),
    reserved_stock INTEGER DEFAULT 0 CHECK (reserved_stock >= 0),
    minimum_threshold INTEGER DEFAULT 0,
    reorder_threshold INTEGER DEFAULT 0,
    daily_consumption_rate DECIMAL(10,2) DEFAULT 0,
    lead_time_days INTEGER DEFAULT 0,
    shortage_score DECIMAL(5,2),
    severity severity_enum DEFAULT 'SAFE',
    last_restocked_at TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(facility_id, medicine_id)
);

CREATE TABLE inventory_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID REFERENCES facilities(facility_id),
    medicine_id UUID REFERENCES medicine_master(medicine_id),
    total_stock INTEGER,
    shortage_score DECIMAL(5,2),
    severity severity_enum,
    snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_adjustments (
    adjustment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventory_id UUID REFERENCES inventory_current(inventory_id),
    adjusted_by UUID REFERENCES users(user_id),
    adjustment_type VARCHAR(100),
    quantity_before INTEGER,
    quantity_after INTEGER,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);