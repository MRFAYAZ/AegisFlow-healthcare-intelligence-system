CREATE TABLE alert_events (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID REFERENCES facilities(facility_id),
    medicine_id UUID REFERENCES medicine_master(medicine_id),
    alert_type VARCHAR(100),
    severity severity_enum,
    alert_message TEXT,
    alert_status alert_status_enum DEFAULT 'ACTIVE',
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);
