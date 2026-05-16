-- =====================================================
-- AegisFlow Audit & Event Domain
-- =====================================================

CREATE TABLE event_log (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    event_type event_type_enum NOT NULL,

    entity_type VARCHAR(100) NOT NULL,

    entity_id UUID,

    event_payload JSONB,

    triggered_by UUID
        REFERENCES users(user_id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================

CREATE TABLE audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID
        REFERENCES users(user_id),

    action_type VARCHAR(100) NOT NULL,

    entity_type VARCHAR(100) NOT NULL,

    entity_id UUID,

    old_value JSONB,

    new_value JSONB,

    ip_address VARCHAR(100),

    user_agent TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);