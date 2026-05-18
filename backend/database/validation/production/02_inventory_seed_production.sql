-- =====================================================
-- AegisFlow Inventory-Specific Validation Checks
-- =====================================================
-- Detailed inventory health checks covering:
-- - Stock consistency across batch and current tables
-- - Inventory aging and expiry management
-- - Movement patterns and anomalies
-- - Facility-level inventory health
-- =====================================================

-- Section 1: BATCH INVENTORY HEALTH
-- =====================================================

-- Check 1: Expired batches still in inventory
SELECT 'HIGH: Expired batches in active inventory' AS check_name,
       COUNT(*) AS issues_found,
       STRING_AGG(DISTINCT batch_id::text, ', ') AS batch_ids
FROM inventory_batches
WHERE expiry_date < CURRENT_DATE
GROUP BY (SELECT 1);

-- Check 2: Batches expiring within 30 days (early warning)
SELECT 'MEDIUM: Batches expiring within 30 days' AS check_name,
       COUNT(*) AS issues_found,
       STRING_AGG(DISTINCT batch_id::text, ', ') AS batch_ids
FROM inventory_batches
WHERE expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
GROUP BY (SELECT 1);

-- Check 3: Batches with zero available quantity but reserved stock
SELECT 'HIGH: Reserved stock in empty batches' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE quantity_available = 0 AND quantity_reserved > 0;

-- Check 4: Batches with mismatched quantities
SELECT 'CRITICAL: Batch quantity math error' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE (quantity_received - quantity_available - quantity_reserved) != 0
  AND quantity_reserved = 0;

-- Check 5: Oldest batches (not rotated recently)
SELECT 'MEDIUM: Old batches not rotated' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE created_at < CURRENT_DATE - INTERVAL '6 months'
  AND quantity_available > 0;

-- Check 6: Batches received but never updated
SELECT 'MEDIUM: Stale batch records' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_batches
WHERE updated_at IS NULL OR updated_at = created_at;


-- Section 2: CURRENT INVENTORY HEALTH
-- =====================================================

-- Check 7: Below minimum threshold items (stock-out risk)
SELECT 'HIGH: Items below minimum threshold' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE available_stock < minimum_threshold;

-- Check 8: Items at or below reorder point
SELECT 'HIGH: Items at reorder point' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE available_stock <= reorder_threshold
  AND available_stock > 0;

-- Check 9: Stock-out conditions (zero available)
SELECT 'CRITICAL: Stock-out items' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE available_stock = 0 AND total_stock = 0;

-- Check 10: Items with high shortage scores but haven't triggered alerts
SELECT 'HIGH: High shortage score without recent alert' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current ic
LEFT JOIN alert_events ae ON ic.facility_id = ae.facility_id 
  AND ic.medicine_id = ae.medicine_id
WHERE ic.shortage_score > 75
  AND (ae.alert_id IS NULL OR ae.triggered_at < CURRENT_TIMESTAMP - INTERVAL '24 hours');

-- Check 11: Reserved stock percentage > 80%
SELECT 'MEDIUM: High reservation percentage' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE total_stock > 0
  AND (reserved_stock::DECIMAL / total_stock) > 0.8;

-- Check 12: Inconsistent inventory severity levels
SELECT 'MEDIUM: Severity mismatch with shortage score' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE (shortage_score >= 75 AND severity != 'EMERGENCY')
   OR (shortage_score BETWEEN 50 AND 74 AND severity != 'CRITICAL')
   OR (shortage_score BETWEEN 25 AND 49 AND severity != 'WARNING')
   OR (shortage_score < 25 AND severity != 'SAFE');

-- Check 13: Zero consumption rate for active medicines
SELECT 'MEDIUM: Zero daily consumption for stocked items' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE daily_consumption_rate = 0
  AND available_stock > 0
  AND (last_updated IS NULL OR last_updated < CURRENT_TIMESTAMP - INTERVAL '30 days');

-- Check 14: Extreme lead time values
SELECT 'HIGH: Unrealistic lead time values' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE lead_time_days > 365 OR lead_time_days < 1;


-- Section 3: BATCH TO CURRENT INVENTORY SYNC
-- =====================================================

-- Check 15: Current inventory total vs sum of batches
SELECT 'CRITICAL: Current inventory total mismatch' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current ic
LEFT JOIN (
    SELECT facility_id, medicine_id, SUM(quantity_received) AS batch_total
    FROM inventory_batches
    GROUP BY facility_id, medicine_id
) ib ON ib.facility_id = ic.facility_id
    AND ib.medicine_id = ic.medicine_id
WHERE ic.total_stock > 0
  AND ib.batch_total IS NOT NULL
  AND ic.total_stock != ib.batch_total;

-- Check 16: Facility-medicine without any batch records
SELECT 'HIGH: Current inventory without batch records' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current ic
LEFT JOIN inventory_batches ib ON ic.facility_id = ib.facility_id 
  AND ic.medicine_id = ib.medicine_id
WHERE ib.batch_id IS NULL
  AND ic.total_stock > 0;

-- Check 17: Multiple current inventory records per facility-medicine
SELECT 'CRITICAL: Duplicate inventory records' AS check_name,
       COUNT(*) AS issues_found
FROM (
    SELECT facility_id, medicine_id, COUNT(*) as cnt
    FROM inventory_current
    GROUP BY facility_id, medicine_id
    HAVING COUNT(*) > 1
) duplicates;


-- Section 4: INVENTORY MOVEMENT & AGING
-- =====================================================

-- Check 18: Never restocked items (stuck inventory)
SELECT 'MEDIUM: Never restocked items' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE last_restocked_at IS NULL
  AND last_updated < CURRENT_TIMESTAMP - INTERVAL '90 days';

-- Check 19: Recently updated inventory (within 24 hours)
SELECT 'INFORMATIONAL: Recent inventory updates' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE last_updated > CURRENT_TIMESTAMP - INTERVAL '24 hours';

-- Check 20: Inventory with no adjustment history
SELECT 'MEDIUM: Inventory without adjustment records' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current ic
LEFT JOIN inventory_adjustments ia ON ic.inventory_id = ia.inventory_id
WHERE ia.adjustment_id IS NULL;


-- Section 5: FACILITY-LEVEL INVENTORY HEALTH
-- =====================================================

-- Check 21: Facilities with all items in stock-out
SELECT 'CRITICAL: Facility-wide stock-out' AS check_name,
       COUNT(DISTINCT f.facility_id) AS issues_found
FROM facilities f
WHERE f.is_active = TRUE
  AND f.facility_id NOT IN (
    SELECT DISTINCT facility_id
    FROM inventory_current
    WHERE available_stock > 0
  );

-- Check 22: Facilities with high average shortage score
SELECT 'HIGH: Facility with critical shortage situation' AS check_name,
       COUNT(DISTINCT facility_id) AS issues_found
FROM inventory_current
GROUP BY facility_id
HAVING AVG(shortage_score) > 70;

-- Check 23: Facilities with imbalanced inventory (80%+ of items critical)
SELECT 'HIGH: Facility with critical inventory imbalance' AS check_name,
       COUNT(DISTINCT facility_id) AS issues_found
FROM (
    SELECT facility_id,
           COUNT(*) as total_items,
           SUM(CASE WHEN shortage_score >= 75 THEN 1 ELSE 0 END) as critical_items
    FROM inventory_current
    WHERE total_stock > 0
    GROUP BY facility_id
    HAVING (SUM(CASE WHEN shortage_score >= 75 THEN 1 ELSE 0 END)::DECIMAL / 
            COUNT(*)) > 0.8
) imbalance;

-- Check 24: Facilities with zero inventory records
SELECT 'MEDIUM: Active facility with no inventory' AS check_name,
       COUNT(*) AS issues_found
FROM facilities f
WHERE f.is_active = TRUE
  AND f.facility_id NOT IN (
    SELECT DISTINCT facility_id FROM inventory_current
  );


-- Section 6: SNAPSHOT CONSISTENCY
-- =====================================================

-- Check 25: Snapshot stock greater than current inventory
SELECT 'HIGH: Snapshot stock inconsistency' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_snapshots s
LEFT JOIN inventory_current ic ON s.facility_id = ic.facility_id 
  AND s.medicine_id = ic.medicine_id
WHERE s.total_stock > ic.total_stock;

-- Check 26: Snapshots older than 30 days
SELECT 'MEDIUM: Stale inventory snapshots' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_snapshots
WHERE snapshot_timestamp < CURRENT_TIMESTAMP - INTERVAL '30 days';

-- Check 27: Facility snapshots without current inventory
SELECT 'HIGH: Snapshot without current inventory record' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_snapshots s
LEFT JOIN inventory_current ic ON s.facility_id = ic.facility_id 
  AND s.medicine_id = ic.medicine_id
WHERE ic.inventory_id IS NULL;


-- Section 7: MEDICINE-LEVEL INVENTORY
-- =====================================================

-- Check 28: Essential medicines in critical shortage
SELECT 'CRITICAL: Essential medicine shortage' AS check_name,
       COUNT(DISTINCT ic.medicine_id) AS issues_found
FROM inventory_current ic
JOIN medicine_master m ON ic.medicine_id = m.medicine_id
WHERE m.is_critical = TRUE
  AND ic.shortage_score > 75;

-- Check 29: Medicines with extreme price variations across facilities
SELECT 'HIGH: Price variance anomaly' AS check_name,
       COUNT(*) AS issues_found
FROM (
    SELECT medicine_id,
           MIN(unit_cost) as min_cost,
           MAX(unit_cost) as max_cost
    FROM inventory_batches
    WHERE unit_cost > 0
    GROUP BY medicine_id
    HAVING (MAX(unit_cost) - MIN(unit_cost)) / MIN(unit_cost) > 0.5
) price_variance;

-- Check 30: Prescribed medicines not in any facility inventory
SELECT 'HIGH: Prescribed medicine stock-out everywhere' AS check_name,
       COUNT(DISTINCT medicine_id) AS issues_found
FROM medicine_master m
WHERE m.prescription_required = TRUE
  AND m.medicine_id NOT IN (
    SELECT DISTINCT medicine_id 
    FROM inventory_current 
    WHERE available_stock > 0
  );


-- Section 8: TRANSFER & REDISTRIBUTION READINESS
-- =====================================================

-- Check 31: Surplus inventory (over-stocked beyond 2x reorder threshold)
SELECT 'INFORMATIONAL: Over-stocked items' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE available_stock > (reorder_threshold * 2);

-- Check 32: Inventory available for redistribution (surplus to shortage gap)
SELECT 'INFORMATIONAL: Potential redistribution candidates' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE available_stock > (reorder_threshold * 1.5)
  AND shortage_score < 25;

-- Check 33: Items blocked for transfer (too low stock)
SELECT 'MEDIUM: Items too critical to transfer' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE available_stock < (minimum_threshold * 1.5)
  AND available_stock > 0;


-- Section 9: CONSUMPTION & FORECASTING
-- =====================================================

-- Check 34: Days of stock remaining (based on consumption)
SELECT 'INFORMATIONAL: Low days of supply' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE daily_consumption_rate > 0
  AND (available_stock / daily_consumption_rate) < 7;

-- Check 35: Inventory turnover analysis (slow-moving items)
SELECT 'MEDIUM: Slow-moving inventory' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current ic
WHERE ic.daily_consumption_rate < 1
  AND ic.total_stock > (minimum_threshold * 3);

-- Check 36: Lead time coverage (sufficient pre-order buffer)
SELECT 'MEDIUM: Insufficient lead time coverage' AS check_name,
       COUNT(*) AS issues_found
FROM inventory_current
WHERE (lead_time_days * daily_consumption_rate) > available_stock;


-- =====================================================
-- Summary Report
-- =====================================================
-- Inventory validation summary
SELECT 'INVENTORY VALIDATION COMPLETE' AS status,
       NOW() AS check_timestamp,
       'Focus on CRITICAL and HIGH severity items for operational continuity' AS recommendation;
