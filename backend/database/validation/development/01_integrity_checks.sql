-- =====================================================
-- AegisFlow Database Integrity Checks (Development)
-- =====================================================
-- Simplified integrity validation for development environment
-- Focus on critical data consistency and foreign key relationships
-- =====================================================

-- Section 1: FOREIGN KEY INTEGRITY
-- =====================================================

-- Check 1: Orphaned sessions (no user reference)
SELECT 'Orphaned sessions' AS issue_type,
       COUNT(*) AS count
FROM user_sessions s
LEFT JOIN users u ON s.user_id = u.user_id
WHERE u.user_id IS NULL;

-- Check 2: Orphaned facility locations
SELECT 'Orphaned facility locations' AS issue_type,
       COUNT(*) AS count
FROM facilities f
LEFT JOIN locations l ON f.location_id = l.location_id
WHERE f.location_id IS NOT NULL AND l.location_id IS NULL;

-- Check 3: Invalid facility-user associations
SELECT 'Invalid facility-user associations' AS issue_type,
       COUNT(*) AS count
FROM facility_users fu
LEFT JOIN facilities f ON fu.facility_id = f.facility_id
LEFT JOIN users u ON fu.user_id = u.user_id
WHERE f.facility_id IS NULL OR u.user_id IS NULL;

-- Check 4: Orphaned batch facility references
SELECT 'Orphaned batch facility references' AS issue_type,
       COUNT(*) AS count
FROM inventory_batches ib
LEFT JOIN facilities f ON ib.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 5: Orphaned batch medicine references
SELECT 'Orphaned batch medicine references' AS issue_type,
       COUNT(*) AS count
FROM inventory_batches ib
LEFT JOIN medicine_master m ON ib.medicine_id = m.medicine_id
WHERE m.medicine_id IS NULL;

-- Check 6: Orphaned inventory facility references
SELECT 'Orphaned inventory facility references' AS issue_type,
       COUNT(*) AS count
FROM inventory_current ic
LEFT JOIN facilities f ON ic.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 7: Orphaned inventory medicine references
SELECT 'Orphaned inventory medicine references' AS issue_type,
       COUNT(*) AS count
FROM inventory_current ic
LEFT JOIN medicine_master m ON ic.medicine_id = m.medicine_id
WHERE m.medicine_id IS NULL;


-- Section 2: QUANTITY & AMOUNT VALIDATION
-- =====================================================

-- Check 8: Negative quantities in batches
SELECT 'Negative batch quantities' AS issue_type,
       COUNT(*) AS count
FROM inventory_batches
WHERE quantity_received < 0 OR quantity_available < 0 OR quantity_reserved < 0;

-- Check 9: Available exceeds received in batches
SELECT 'Available exceeds received (batches)' AS issue_type,
       COUNT(*) AS count
FROM inventory_batches
WHERE quantity_available > quantity_received;

-- Check 10: Reserved exceeds available in batches
SELECT 'Reserved exceeds available (batches)' AS issue_type,
       COUNT(*) AS count
FROM inventory_batches
WHERE quantity_reserved > quantity_available;

-- Check 11: Available exceeds total in current inventory
SELECT 'Available exceeds total (current inventory)' AS issue_type,
       COUNT(*) AS count
FROM inventory_current
WHERE available_stock > total_stock;

-- Check 12: Reserved exceeds total in current inventory
SELECT 'Reserved exceeds total (current inventory)' AS issue_type,
       COUNT(*) AS count
FROM inventory_current
WHERE reserved_stock > total_stock;

-- Check 13: Negative thresholds in inventory
SELECT 'Negative thresholds' AS issue_type,
       COUNT(*) AS count
FROM inventory_current
WHERE minimum_threshold < 0 OR reorder_threshold < 0;


-- Section 3: DATE & TIME VALIDATION
-- =====================================================

-- Check 14: Session expiry before creation
SELECT 'Session expiry before creation' AS issue_type,
       COUNT(*) AS count
FROM user_sessions
WHERE expires_at <= created_at;

-- Check 15: Expiry before manufacturing date
SELECT 'Expiry before manufacturing date' AS issue_type,
       COUNT(*) AS count
FROM inventory_batches
WHERE manufacturing_date IS NOT NULL AND expiry_date < manufacturing_date;


-- Section 4: BASIC UNIQUENESS VALIDATION
-- =====================================================

-- Check 16: Duplicate active user emails
SELECT 'Duplicate active emails' AS issue_type,
       COUNT(*) AS count
FROM (
    SELECT email
    FROM users
    WHERE is_active = TRUE
    GROUP BY email
    HAVING COUNT(*) > 1
) duplicates;

-- Check 17: Duplicate active phone numbers
SELECT 'Duplicate active phone numbers' AS issue_type,
       COUNT(*) AS count
FROM (
    SELECT phone_number
    FROM users
    WHERE is_active = TRUE AND phone_number IS NOT NULL
    GROUP BY phone_number
    HAVING COUNT(*) > 1
) duplicates;


-- Section 5: GEOGRAPHIC VALIDATION
-- =====================================================

-- Check 18: Invalid geographic coordinates
SELECT 'Invalid geographic coordinates' AS issue_type,
       COUNT(*) AS count
FROM locations
WHERE latitude < -90 OR latitude > 90 OR longitude < -180 OR longitude > 180;
