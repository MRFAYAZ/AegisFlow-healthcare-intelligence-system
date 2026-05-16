INSERT INTO facility_users (
    facility_id,
    user_id,
    assigned_role
)
SELECT
    f.facility_id,
    u.user_id,
    'HOSPITAL_ADMIN'
FROM facilities f
CROSS JOIN users u
WHERE f.facility_name = 'Apollo Hospital Chennai'
AND u.email = 'priya.sharma@apollohealth.com'
ON CONFLICT DO NOTHING;

INSERT INTO facility_users (
    facility_id,
    user_id,
    assigned_role
)
SELECT
    f.facility_id,
    u.user_id,
    'PHARMACIST'
FROM facilities f
CROSS JOIN users u
WHERE f.facility_name = 'Apollo Hospital Chennai'
AND u.email = 'ravi.kumar@apollohealth.com'
ON CONFLICT DO NOTHING;

INSERT INTO facility_users (
    facility_id,
    user_id,
    assigned_role
)
SELECT
    f.facility_id,
    u.user_id,
    'SHOP_OWNER'
FROM facilities f
CROSS JOIN users u
WHERE f.facility_name = 'MedPlus Pharmacy Chennai'
AND u.email = 'aisha.khan@medplus.com'
ON CONFLICT DO NOTHING;

