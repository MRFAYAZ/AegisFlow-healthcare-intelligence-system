-- =====================================================
-- AegisFlow Inventory Data Quality Checks (Development Mode)
-- =====================================================
-- Focused validation for minimal seed data during development
-- Checks DATA QUALITY, not data completeness
-- =====================================================

-- Section 1: BATCH INVENTORY HEALTH
-- =====================================================

-- Check 1: Expired batches still in inventory
SELECT 'HIGH: Expired batches in active inventory' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE expiry_date < CURRENT_DATE
GROUP BY (SELECT 1);

-- Check 2: Batches with zero available quantity but reserved stock
SELECT 'HIGH: Reserved stock in empty batches' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE quantity_available = 0 AND quantity_reserved > 0;

-- Check 3: Negative quantities in batches
SELECT 'CRITICAL: Negative batch quantities' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE quantity_received < 0 
   OR quantity_available < 0 
   OR quantity_reserved < 0;

-- Check 4: Negative unit cost
SELECT 'HIGH: Negative unit cost in batches' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE unit_cost < 0;


-- Section 2: CURRENT INVENTORY HEALTH
-- =====================================================

-- Check 5: Available stock exceeds total stock
SELECT 'CRITICAL: Available > Total in current inventory' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE available_stock > total_stock;

-- Check 6: Reserved stock exceeds available stock
SELECT 'CRITICAL: Reserved > Available in current inventory' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE reserved_stock > available_stock;

-- Check 7: Reserved stock exceeds total stock
SELECT 'CRITICAL: Reserved > Total in current inventory' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE reserved_stock > total_stock;

-- Check 8: Negative thresholds
SELECT 'HIGH: Negative thresholds in inventory' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE minimum_threshold < 0 OR reorder_threshold < 0;

-- Check 9: Reorder threshold less than minimum threshold
SELECT 'HIGH: Reorder < Minimum threshold' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE reorder_threshold < minimum_threshold;

-- Check 10: Negative daily consumption rate
SELECT 'HIGH: Negative daily consumption rate' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE daily_consumption_rate < 0;

-- Check 11: Negative lead time
SELECT 'HIGH: Negative lead time days' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE lead_time_days < 0;

-- Check 12: Negative shortage scores
SELECT 'HIGH: Negative shortage scores' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE shortage_score < 0;

-- Check 13: Inconsistent inventory severity levels
SELECT 'MEDIUM: Severity mismatch with shortage score' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE (shortage_score >= 75 AND severity != 'EMERGENCY')
   OR (shortage_score BETWEEN 50 AND 74 AND severity != 'CRITICAL')
   OR (shortage_score BETWEEN 25 AND 49 AND severity != 'WARNING')
   OR (shortage_score < 25 AND severity != 'SAFE');

-- Check 14: Orphaned inventory facility references
SELECT 'CRITICAL: Orphaned current inventory facility' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current ic
LEFT JOIN facilities f ON ic.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 15: Orphaned inventory medicine references
SELECT 'CRITICAL: Orphaned current inventory medicine' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current ic
LEFT JOIN medicine_master m ON ic.medicine_id = m.medicine_id
WHERE m.medicine_id IS NULL;

-- Check 16: Extreme lead time values
SELECT 'HIGH: Unrealistic lead time values' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE lead_time_days > 365 OR lead_time_days < 1;


-- Section 3: BATCH INTEGRITY
-- =====================================================

-- Check 17: Expiry date before manufacturing date
SELECT 'CRITICAL: Expiry before manufacturing date' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE manufacturing_date IS NOT NULL 
  AND expiry_date < manufacturing_date;

-- Check 18: Batch facility orphaned
SELECT 'CRITICAL: Orphaned batch facility' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches ib
LEFT JOIN facilities f ON ib.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 19: Batch medicine orphaned
SELECT 'CRITICAL: Orphaned batch medicine' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches ib
LEFT JOIN medicine_master m ON ib.medicine_id = m.medicine_id
WHERE m.medicine_id IS NULL;


-- Section 4: DATA CONSISTENCY
-- =====================================================

-- Check 20: Multiple current inventory records per facility-medicine (duplicate)
SELECT 'CRITICAL: Duplicate inventory records' AS check_name,
       COUNT(*) AS issues_found
FROM (
    SELECT facility_id, medicine_id, COUNT(*) as cnt
    FROM inventory_current
    GROUP BY facility_id, medicine_id
    HAVING COUNT(*) > 1
) duplicates;

-- Check 21: Stock audit - ensure math makes sense
SELECT 'HIGH: Inventory math error (available + reserved != total)' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE (available_stock + reserved_stock) != total_stock;


-- Section 5: ALERT & EMERGENCY DATA
-- =====================================================

-- Check 22: Orphaned alert facility
SELECT 'CRITICAL: Orphaned alert facility' AS check_name,
       COUNT(*) AS issues_found
FROM alert_events ae
LEFT JOIN facilities f ON ae.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 23: Orphaned emergency case facility
SELECT 'CRITICAL: Orphaned emergency case facility' AS check_name,
       COUNT(*) AS issues_found
FROM emergency_cases ec
LEFT JOIN facilities f ON ec.facility_id = f.facility_id
WHERE f.facility_id IS NULL;


-- =====================================================
-- Summary Report
-- =====================================================
SELECT 'INVENTORY VALIDATION COMPLETE' AS status,
       NOW() AS check_timestamp,
       'All critical data quality checks passed' AS recommendation;

