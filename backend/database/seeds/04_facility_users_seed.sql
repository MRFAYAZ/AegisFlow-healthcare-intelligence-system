INSERT INTO facility_users (
    facility_id,
    user_id,
    assigned_role
)

SELECT
    f.facility_id,
    u.user_id,
    'HOSPITAL_ADMIN'::user_role_enum
FROM facilities f
JOIN users u
ON u.email='ravi.kumar@apollohospital.com'
WHERE f.facility_name='Apollo Hospital Chennai'

UNION ALL

SELECT
    f.facility_id,
    u.user_id,
    'HOSPITAL_ADMIN'::user_role_enum
FROM facilities f
JOIN users u
ON u.email='meena.narayanan@ggh.in'
WHERE f.facility_name='Government General Hospital';