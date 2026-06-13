-- =====================================================
-- AEGISFLOW
-- USERS SEED DATA
-- =====================================================

INSERT INTO users (
    full_name,
    email,
    phone_number,
    password_hash,
    role
)
VALUES

(
    'Shahid khan',
    'admin@aegisflow.com',
    '9000000001',
    '$2b$12$seedadminhash',
    'SYSTEM_ADMIN'
),

(
    'Dr. Ravi Kumar',
    'ravi.kumar@apollohospital.com',
    '9000000002',
    '$2b$12$seedhash',
    'HOSPITAL_ADMIN'
),

(
    'Dr. Meena Narayanan',
    'meena.narayanan@ggh.in',
    '9000000003',
    '$2b$12$seedhash',
    'HOSPITAL_ADMIN'
),

(
    'Arjun Pharmacist',
    'arjun@apollo-pharmacy.in',
    '9000000004',
    '$2b$12$seedhash',
    'PHARMACIST'
),

(
    'Sathish Kumar',
    'sathish@medplus.in',
    '9000000005',
    '$2b$12$seedhash',
    'SHOP_OWNER'
),

(
    'Priya Reddy',
    'priya@netmedspartner.in',
    '9000000006',
    '$2b$12$seedhash',
    'SHOP_OWNER'
),

(
    'Karthik Operations',
    'karthik@aegisflow.com',
    '9000000007',
    '$2b$12$seedhash',
    'EMERGENCY_OPERATOR'
),

(
    'Vignesh Supplier',
    'vignesh@astersupplier.com',
    '9000000008',
    '$2b$12$seedhash',
    'SUPPLIER_MANAGER'
),

(
    'Lavanya Supplier',
    'lavanya@astersupplier.com',
    '9000000009',
    '$2b$12$seedhash',
    'SUPPLIER_MANAGER'
),

(
    'Warehouse Supervisor',
    'warehouse@aegisflow.com',
    '9000000010',
    '$2b$12$seedhash',
    'SUPPLIER_MANAGER'
);