-- =====================================================
-- AegisFlow Database Integrity Checks
-- =====================================================
-- This file contains critical data validation queries
-- to ensure database consistency and data quality
-- =====================================================

-- Section 1: USER & AUTHENTICATION INTEGRITY
-- =====================================================

-- Check 1: Session expiry must be after creation
SELECT 'CRITICAL: Session expiry before creation' AS check_name, 
       COUNT(*) AS issues_found
FROM user_sessions 
WHERE expires_at <= created_at;

-- Check 2: Sessions reference active users only
SELECT 'CRITICAL: Orphaned sessions' AS check_name,
       COUNT(*) AS issues_found
FROM user_sessions s
LEFT JOIN users u ON s.user_id = u.user_id
WHERE u.user_id IS NULL;

-- Check 3: Email uniqueness violation (active users)
SELECT 'HIGH: Duplicate active emails' AS check_name,
       COUNT(*) AS issues_found
FROM (
    SELECT email, COUNT(*) as cnt
    FROM users 
    WHERE is_active = TRUE
    GROUP BY email 
    HAVING COUNT(*) > 1
) duplicates;

-- Check 4: Duplicate active phone numbers
SELECT 'HIGH: Duplicate active phone numbers' AS check_name,
       COUNT(*) AS issues_found
FROM (
    SELECT phone_number, COUNT(*) as cnt
    FROM users 
    WHERE is_active = TRUE AND phone_number IS NOT NULL
    GROUP BY phone_number 
    HAVING COUNT(*) > 1
) duplicates;


-- Section 2: LOCATION & FACILITY INTEGRITY
-- =====================================================

-- Check 5: Geographic coordinates out of valid range
SELECT 'HIGH: Invalid geographic coordinates' AS check_name,
       COUNT(*) AS issues_found
FROM locations 
WHERE latitude < -90 OR latitude > 90 
   OR longitude < -180 OR longitude > 180;

-- Check 6: Facilities with invalid location references
SELECT 'CRITICAL: Orphaned facility locations' AS check_name,
       COUNT(*) AS issues_found
FROM facilities f
LEFT JOIN locations l ON f.location_id = l.location_id
WHERE f.location_id IS NOT NULL AND l.location_id IS NULL;

-- Check 7: Active facilities with missing locations
SELECT 'HIGH: Active facilities without locations' AS check_name,
       COUNT(*) AS issues_found
FROM facilities f
WHERE f.is_active = TRUE AND f.location_id IS NULL;

-- Check 8: Facility-user associations with invalid references
SELECT 'CRITICAL: Invalid facility-user associations' AS check_name,
       COUNT(*) AS issues_found
FROM facility_users fu
LEFT JOIN facilities f ON fu.facility_id = f.facility_id
LEFT JOIN users u ON fu.user_id = u.user_id
WHERE f.facility_id IS NULL OR u.user_id IS NULL;


-- Section 3: INVENTORY BATCH INTEGRITY (CRITICAL)
-- =====================================================

-- Check 9: Available quantity exceeds received quantity
SELECT 'CRITICAL: Available > Received in batches' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE quantity_available > quantity_received;

-- Check 10: Reserved quantity exceeds available quantity
SELECT 'CRITICAL: Reserved > Available in batches' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE quantity_reserved > quantity_available;

-- Check 11: Expiry date before manufacturing date
SELECT 'CRITICAL: Expiry before manufacturing date' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE manufacturing_date IS NOT NULL 
  AND expiry_date < manufacturing_date;

-- Check 12: Negative quantities in batches
SELECT 'CRITICAL: Negative batch quantities' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE quantity_received < 0 
   OR quantity_available < 0 
   OR quantity_reserved < 0;

-- Check 13: Negative unit cost
SELECT 'HIGH: Negative unit cost in batches' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE unit_cost < 0;

-- Check 14: Batches with orphaned facility references
SELECT 'CRITICAL: Orphaned batch facility references' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches ib
LEFT JOIN facilities f ON ib.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 15: Batches with orphaned medicine references
SELECT 'CRITICAL: Orphaned batch medicine references' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches ib
LEFT JOIN medicine_master m ON ib.medicine_id = m.medicine_id
WHERE m.medicine_id IS NULL;


-- Section 4: INVENTORY CURRENT STOCK INTEGRITY (CRITICAL)
-- =====================================================

-- Check 16: Available stock exceeds total stock
SELECT 'CRITICAL: Available > Total in current inventory' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE available_stock > total_stock;

-- Check 17: Reserved stock exceeds available stock
SELECT 'CRITICAL: Reserved > Available in current inventory' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE reserved_stock > available_stock;

-- Check 18: Reserved stock exceeds total stock
SELECT 'CRITICAL: Reserved > Total in current inventory' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE reserved_stock > total_stock;

-- Check 19: Negative thresholds
SELECT 'HIGH: Negative thresholds in inventory' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE minimum_threshold < 0 OR reorder_threshold < 0;

-- Check 20: Reorder threshold less than minimum threshold
SELECT 'HIGH: Reorder < Minimum threshold' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE reorder_threshold < minimum_threshold;

-- Check 21: Negative daily consumption rate
SELECT 'HIGH: Negative daily consumption rate' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE daily_consumption_rate < 0;

-- Check 22: Negative lead time
SELECT 'HIGH: Negative lead time days' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE lead_time_days < 0;

-- Check 23: Negative shortage scores
SELECT 'HIGH: Negative shortage scores' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE shortage_score < 0;

-- Check 24: Orphaned inventory facility references
SELECT 'CRITICAL: Orphaned current inventory facility' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current ic
LEFT JOIN facilities f ON ic.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 25: Orphaned inventory medicine references
SELECT 'CRITICAL: Orphaned current inventory medicine' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current ic
LEFT JOIN medicine_master m ON ic.medicine_id = m.medicine_id
WHERE m.medicine_id IS NULL;


-- Section 5: PURCHASE TRANSACTION INTEGRITY
-- =====================================================

-- Check 26: Invalid quantities in purchases
SELECT 'HIGH: Invalid purchase quantities' AS check_name,
       COUNT(*) AS issues_found
FROM purchase_transactions
WHERE quantity <= 0;

-- Check 27: Negative unit price in purchases
SELECT 'HIGH: Negative purchase unit price' AS check_name,
       COUNT(*) AS issues_found
FROM purchase_transactions
WHERE unit_price < 0;

-- Check 28: Negative total amount in purchases
SELECT 'HIGH: Negative purchase total amount' AS check_name,
       COUNT(*) AS issues_found
FROM purchase_transactions
WHERE total_amount < 0;

-- Check 29: Invalid purchase status value
SELECT 'HIGH: Invalid purchase status' AS check_name,
       COUNT(*) AS issues_found
FROM purchase_transactions
WHERE purchase_status::text NOT IN ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED');

-- Check 31: Orphaned purchase facility references
SELECT 'CRITICAL: Orphaned purchase facility' AS check_name,
       COUNT(*) AS issues_found
FROM purchase_transactions pt
LEFT JOIN facilities f ON pt.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 32: Orphaned purchase medicine references
SELECT 'CRITICAL: Orphaned purchase medicine' AS check_name,
       COUNT(*) AS issues_found
FROM purchase_transactions pt
LEFT JOIN medicine_master m ON pt.medicine_id = m.medicine_id
WHERE m.medicine_id IS NULL;


-- Section 6: TRANSFER & REDISTRIBUTION INTEGRITY
-- =====================================================

-- Check 32: Transfer quantity negative or zero
SELECT 'HIGH: Invalid transfer quantities' AS check_name,
       COUNT(*) AS issues_found
FROM transfer_requests
WHERE requested_quantity <= 0;

-- Check 33: Transfer source and destination same facility
SELECT 'HIGH: Transfer source = destination' AS check_name,
       COUNT(*) AS issues_found
FROM transfer_requests
WHERE from_facility_id = to_facility_id;

-- Check 34: Orphaned transfer source facility
SELECT 'CRITICAL: Orphaned transfer source facility' AS check_name,
       COUNT(*) AS issues_found
FROM transfer_requests tr
LEFT JOIN facilities f ON tr.from_facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 35: Orphaned transfer destination facility
SELECT 'CRITICAL: Orphaned transfer destination facility' AS check_name,
       COUNT(*) AS issues_found
FROM transfer_requests tr
LEFT JOIN facilities f ON tr.to_facility_id = f.facility_id
WHERE f.facility_id IS NULL;


-- Section 7: ALERT & EMERGENCY INTEGRITY
-- =====================================================

-- Check 36: Invalid alert status value
SELECT 'HIGH: Invalid alert status' AS check_name,
       COUNT(*) AS issues_found
FROM alert_events
WHERE alert_status::text NOT IN ('ACTIVE', 'APPROVED', 'REJECTED', 'IN_TRANSIT', 'COMPLETED', 'CANCELLED');

-- Check 37: Orphaned alert facility references
SELECT 'CRITICAL: Orphaned alert facility' AS check_name,
       COUNT(*) AS issues_found
FROM alert_events ae
LEFT JOIN facilities f ON ae.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 38: Emergency case with invalid required quantity
SELECT 'HIGH: Emergency case with invalid required quantity' AS check_name,
       COUNT(*) AS issues_found
FROM emergency_cases
WHERE required_quantity IS NOT NULL AND required_quantity <= 0;

-- Check 39: Orphaned emergency case facility
SELECT 'CRITICAL: Orphaned emergency case facility' AS check_name,
       COUNT(*) AS issues_found
FROM emergency_cases ec
LEFT JOIN facilities f ON ec.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 40: Orphaned emergency case medicine
SELECT 'CRITICAL: Orphaned emergency case medicine' AS check_name,
       COUNT(*) AS issues_found
FROM emergency_cases ec
LEFT JOIN medicine_master m ON ec.medicine_id = m.medicine_id
WHERE m.medicine_id IS NULL;


-- Section 8: ANALYTICS INTEGRITY
-- =====================================================

-- Check 41: Negative inventory metrics
SELECT 'HIGH: Negative available stock in metrics' AS check_name,
       COUNT(*) AS issues_found
FROM fact_inventory_metrics
WHERE available_stock < 0;

-- Check 42: Negative counts in inventory metrics
SELECT 'HIGH: Negative counts in inventory metrics' AS check_name,
       COUNT(*) AS issues_found
FROM fact_inventory_metrics
WHERE transfer_requests_count < 0 OR emergency_count < 0;

-- Check 43: Orphaned fact inventory metrics facility
SELECT 'CRITICAL: Orphaned fact inventory metrics facility' AS check_name,
       COUNT(*) AS issues_found
FROM fact_inventory_metrics fim
LEFT JOIN facilities f ON fim.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 44: Invalid regional shortage index values
SELECT 'HIGH: Invalid regional shortage index' AS check_name,
       COUNT(*) AS issues_found
FROM regional_shortage_index
WHERE average_shortage_score < 0 OR average_shortage_score > 100;

-- Check 44: Orphaned outbreak signals medicine
SELECT 'CRITICAL: Orphaned outbreak signals medicine' AS check_name,
       COUNT(*) AS issues_found
FROM outbreak_signals os
LEFT JOIN medicine_master m ON os.medicine_id = m.medicine_id
WHERE os.medicine_id IS NOT NULL AND m.medicine_id IS NULL;


-- Section 9: AUDIT & COMPLIANCE
-- =====================================================

-- Check 45: Event log with missing event type
SELECT 'MEDIUM: Event log with missing event type' AS check_name,
       COUNT(*) AS issues_found
FROM event_log
WHERE event_type IS NULL OR entity_type IS NULL;

-- Check 46: Audit logs with missing entity type
SELECT 'HIGH: Audit log with missing entity type' AS check_name,
       COUNT(*) AS issues_found
FROM audit_logs
WHERE entity_type IS NULL OR entity_type = '';

-- Check 47: Audit logs with invalid user references
SELECT 'HIGH: Orphaned audit log user' AS check_name,
       COUNT(*) AS issues_found
FROM audit_logs al
LEFT JOIN users u ON al.user_id = u.user_id
WHERE al.user_id IS NOT NULL AND u.user_id IS NULL;


-- =====================================================
-- Summary Report
-- =====================================================
-- Run all checks and provide summary
SELECT 'INTEGRITY CHECK COMPLETE' AS status,
       NOW() AS check_timestamp,
       'Review any findings with CRITICAL severity immediately' AS recommendation;
