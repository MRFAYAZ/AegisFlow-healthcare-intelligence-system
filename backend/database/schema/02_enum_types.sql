CREATE TYPE facility_type_enum AS ENUM (
    'HOSPITAL',
    'MEDICAL_SHOP',
    'SUPPLIER',
    'WAREHOUSE'
);

CREATE TYPE severity_enum AS ENUM (
    'SAFE',
    'WARNING',
    'CRITICAL',
    'EMERGENCY'
);

CREATE TYPE alert_status_enum AS ENUM (
    'ACTIVE',
    'APPROVED',
    'REJECTED',
    'IN_TRANSIT',
    'COMPLETED',
    'CANCELLED'
);

CREATE TYPE transfer_status_enum AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED',
    'IN_TRANSIT',
    'COMPLETED',
    'CANCELLED'
);

CREATE TYPE user_role_enum AS ENUM (
    'SYSTEM_ADMIN',
    'HOSPITAL_ADMIN',
    'PHARMACIST',
    'SHOP_OWNER',
    'EMERGENCY_OPERATOR',
    'SUPPLIER_MANAGER'
);

CREATE TYPE purchase_status_enum AS ENUM (
    'PENDING',
    'COMPLETED',
    'FAILED',
    'REFUNDED'
);

CREATE TYPE event_type_enum AS ENUM (
    'PURCHASE',
    'TRANSFER',
    'ALERT',
    'EMERGENCY',
    'OUTBREAK',
    'INVENTORY_UPDATE',
    'LOGIN',
    'SYSTEM' 
);