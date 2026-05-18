-- =====================================================
-- AegisFlow Emergency & Alert Checks (Development)
-- =====================================================
-- Simplified validation for emergency and alert scenarios
-- Focus on data consistency and referential integrity
-- =====================================================

-- Section 1: TRANSFER & REDISTRIBUTION VALIDATION
-- =====================================================

-- Check 1: Invalid transfer quantities (zero or negative)
SELECT 'Invalid transfer quantities' AS issue_type,
       COUNT(*) AS count
FROM transfer_requests
WHERE requested_quantity <= 0;

-- Check 2: Transfer source and destination are the same
SELECT 'Transfer source equals destination' AS issue_type,
       COUNT(*) AS count
FROM transfer_requests
WHERE from_facility_id = to_facility_id;

-- Check 3: Orphaned transfer source facility
SELECT 'Orphaned transfer source facility' AS issue_type,
       COUNT(*) AS count
FROM transfer_requests tr
LEFT JOIN facilities f ON tr.from_facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 4: Orphaned transfer destination facility
SELECT 'Orphaned transfer destination facility' AS issue_type,
       COUNT(*) AS count
FROM transfer_requests tr
LEFT JOIN facilities f ON tr.to_facility_id = f.facility_id
WHERE f.facility_id IS NULL;


-- Section 2: ALERT EVENTS VALIDATION
-- =====================================================

-- Check 5: Invalid alert status values
SELECT 'Invalid alert status' AS issue_type,
       COUNT(*) AS count
FROM alert_events
WHERE alert_status::text NOT IN ('ACTIVE', 'APPROVED', 'REJECTED', 'IN_TRANSIT', 'COMPLETED', 'CANCELLED');

-- Check 6: Orphaned alert facility references
SELECT 'Orphaned alert facility' AS issue_type,
       COUNT(*) AS count
FROM alert_events ae
LEFT JOIN facilities f ON ae.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 7: Orphaned alert medicine references
SELECT 'Orphaned alert medicine' AS issue_type,
       COUNT(*) AS count
FROM alert_events ae
LEFT JOIN medicine_master m ON ae.medicine_id = m.medicine_id
WHERE ae.medicine_id IS NOT NULL AND m.medicine_id IS NULL;


-- Section 3: EMERGENCY CASES VALIDATION
-- =====================================================

-- Check 8: Emergency case with invalid required quantity
SELECT 'Emergency case with invalid required quantity' AS issue_type,
       COUNT(*) AS count
FROM emergency_cases
WHERE required_quantity IS NOT NULL AND required_quantity <= 0;

-- Check 9: Orphaned emergency case facility references
SELECT 'Orphaned emergency case facility' AS issue_type,
       COUNT(*) AS count
FROM emergency_cases ec
LEFT JOIN facilities f ON ec.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 10: Orphaned emergency case medicine references
SELECT 'Orphaned emergency case medicine' AS issue_type,
       COUNT(*) AS count
FROM emergency_cases ec
LEFT JOIN medicine_master m ON ec.medicine_id = m.medicine_id
WHERE m.medicine_id IS NULL;


-- Section 4: EMERGENCY CASE QUANTITY VALIDATION
-- =====================================================

-- Check 11: Emergency cases with no quantity specified
SELECT 'Emergency case missing required quantity' AS issue_type,
       COUNT(*) AS count
FROM emergency_cases
WHERE required_quantity IS NULL;

-- Check 12: Alerts with no facility reference
SELECT 'Alert missing facility reference' AS issue_type,
       COUNT(*) AS count
FROM alert_events
WHERE facility_id IS NULL;

-- Check 13: Alerts with no medicine reference
SELECT 'Alert missing medicine reference' AS issue_type,
       COUNT(*) AS count
FROM alert_events
WHERE medicine_id IS NULL;


-- Section 5: TRANSFER REQUEST CONSISTENCY
-- =====================================================

-- Check 14: Transfer requests with invalid status
SELECT 'Transfer request with invalid status' AS issue_type,
       COUNT(*) AS count
FROM transfer_requests
WHERE transfer_status::text NOT IN ('PENDING', 'APPROVED', 'IN_TRANSIT', 'COMPLETED', 'REJECTED', 'CANCELLED');

-- Check 15: Transfer with requester not from source facility
SELECT 'Transfer requester not from source facility' AS issue_type,
       COUNT(*) AS count
FROM transfer_requests tr
LEFT JOIN facility_users fu ON tr.requested_by = fu.user_id AND tr.from_facility_id = fu.facility_id
WHERE fu.user_id IS NULL AND tr.requested_by IS NOT NULL;

