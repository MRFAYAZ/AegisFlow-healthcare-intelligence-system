CREATE TABLE purchase_transactions (
    purchase_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID REFERENCES facilities(facility_id),
    medicine_id UUID REFERENCES medicine_master(medicine_id),
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    purchase_status purchase_status_enum DEFAULT 'PENDING',
    stock_reduced BOOLEAN DEFAULT FALSE,
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE digital_receipts (
    receipt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    purchase_id UUID REFERENCES purchase_transactions(purchase_id),
    receipt_number VARCHAR(100) UNIQUE NOT NULL,
    qr_code_url TEXT,
    pdf_url TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);