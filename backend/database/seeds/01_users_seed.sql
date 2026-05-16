INSERT INTO users (
    full_name,
    email,
    phone_number,
    password_hash,
    role
)
VALUES 
(
    'Arjun Mehta',
    'admin@aegisflow.com',
    '9876543210',
    '$2b$12$hashedpassword1',
    'SYSTEM_ADMIN'
),
(
    'DR. Priya Sharma',
    'priya.sharma@apollohealth.com',
    '9876543211',
    '$2b$12$hashedpassword2',
    'HOSPITAL_ADMIN'
),
(
    'Dr. Viram Rao',
    'vikram.rao@fortishealth.com',
    '9876543212',
    '$2b$12$hashedpassword3',
    'HOSPITAL_ADMIN'
),
(
    'Aisha Khan',
    'aisha.khan@medplus.com',
    '9876543214',
    '$2b$12$hashedpassword4',
    'SHOP_OWNER'
),
(
    'Ravi Kumar',
    'ravi.kumar@apollohealth.com',
    '9876543213',
    '$2b$12$hashedpassword4',
    'PHARMACIST'
),
(
    'Sanjay Patel',
    'sanjay.patel@wellcare.com',
    '9876543215',
    '$2b$12$hashedpassword6',
    'SHOP_OWNER'
),
(
    'Nisha Reddy',
    'nisha.reddy@emergencyops.com',
    '9876543216',
    '$2b$12$hashedpassword7',
    'EMERGENCY_OPERATOR'
),
(
    'Karthik Iyer',
    'karthik.iyer@supplierhub.com',
    '9876543217',
    '$2b$12$hashedpassword8',
    'SUPPLIER_MANAGER'
)
ON CONFLICT DO NOTHING;