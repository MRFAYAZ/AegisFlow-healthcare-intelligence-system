-- =====================================================
-- AegisFlow SANITY VALIDATION CHECKS (Operational)
-- =====================================================
-- CRITICAL: Validates operational realism before FastAPI development
-- Tests business logic, relationships, and calculations
-- =====================================================

-- =====================================================
-- SECTION 1: INVENTORY INTEGRITY & OPERATIONAL REALISM
-- =====================================================

-- Sanity 1: Verify NO negative stock anywhere in system
SELECT 'CRITICAL: Negative stock found' AS sanity_check,
       COUNT(*) AS violations
FROM (
    SELECT 1 FROM inventory_batches WHERE quantity_available < 0
    UNION ALL
    SELECT 1 FROM inventory_batches WHERE quantity_reserved < 0
    UNION ALL
    SELECT 1 FROM inventory_current WHERE available_stock < 0
    UNION ALL
    SELECT 1 FROM inventory_current WHERE reserved_stock < 0
    UNION ALL
    SELECT 1 FROM inventory_current WHERE total_stock < 0
) neg_stock;

-- Sanity 2: Verify stock relationships (reserved <= available <= total)
SELECT 'CRITICAL: Stock relationship violated' AS sanity_check,
       COUNT(*) AS violations
FROM (
    SELECT 1 FROM inventory_batches 
    WHERE quantity_reserved > quantity_available
    
    UNION ALL
    
    SELECT 1 FROM inventory_current 
    WHERE reserved_stock > available_stock
    
    UNION ALL
    
    SELECT 1 FROM inventory_current 
    WHERE available_stock > total_stock
) stock_violations;

-- Sanity 3: Batch inventory consistency (quantity math)
SELECT 'HIGH: Batch quantity inconsistency' AS sanity_check,
       COUNT(*) AS violations
FROM inventory_batches ib
WHERE (ib.quantity_received - ib.quantity_available - ib.quantity_reserved) != 0
  AND ib.quantity_reserved > 0;

-- Sanity 4: Verify all active medicines have facility mappings
SELECT 'HIGH: Medicine with no facility inventory' AS sanity_check,
       COUNT(*) AS violations
FROM medicine_master mm
WHERE is_Active = TRUE 
  AND NOT EXISTS (
    SELECT 1 FROM inventory_current ic 
    WHERE ic.medicine_id = mm.medicine_id
  );

-- Sanity 5: Verify thresholds are logically ordered
SELECT 'MEDIUM: Reorder < Minimum threshold' AS sanity_check,
       COUNT(*) AS violations
FROM inventory_current
WHERE reorder_threshold < minimum_threshold;

-- Sanity 6: Batch expiry dates are realistic
SELECT 'MEDIUM: Batch expired or invalid expiry' AS sanity_check,
       COUNT(*) AS violations
FROM inventory_batches
WHERE expiry_date < CURRENT_DATE
  AND quantity_available > 0;


-- =====================================================
-- SECTION 2: EMERGENCY LOGIC VALIDATION
-- =====================================================

-- Sanity 7: Emergency facilities are ACTIVE hospitals
SELECT 'HIGH: Emergency triggered for inactive facility' AS sanity_check,
       COUNT(*) AS violations
FROM emergency_cases ec
LEFT JOIN facilities f ON ec.facility_id = f.facility_id
WHERE f.is_active = FALSE OR f.facility_type != 'HOSPITAL';

-- Sanity 8: Emergency medicines exist and are critical
SELECT 'MEDIUM: Emergency for non-critical medicine' AS sanity_check,
       COUNT(*) AS violations
FROM emergency_cases ec
LEFT JOIN medicine_master mm ON ec.medicine_id = mm.medicine_id
WHERE mm.is_critical = FALSE;

-- Sanity 9: Emergency source matches reference valid facilities
SELECT 'HIGH: Emergency match source facility invalid' AS sanity_check,
       COUNT(*) AS violations
FROM emergency_source_matches esm
LEFT JOIN facilities f ON esm.source_facility_id = f.facility_id
WHERE f.facility_id IS NULL OR f.is_active = FALSE;

-- Sanity 10: Emergency source matches have reasonable distances
SELECT 'MEDIUM: Emergency source distance unrealistic' AS sanity_check,
       COUNT(*) AS violations
FROM emergency_source_matches
WHERE distance_km < 0 OR distance_km > 1000;

-- Sanity 11: Source facility has available stock for emergency match
SELECT 'CRITICAL: Emergency match without source stock' AS sanity_check,
       COUNT(*) AS violations
FROM emergency_source_matches esm
LEFT JOIN inventory_current ic ON esm.source_facility_id = ic.facility_id 
  AND esm.medicine_id = ic.medicine_id
WHERE esm.available_quantity > 0 
  AND (ic.available_stock IS NULL OR ic.available_stock = 0);

-- Sanity 12: Emergency radius is within valid range
SELECT 'HIGH: Invalid emergency radius' AS sanity_check,
       COUNT(*) AS violations
FROM emergency_cases
WHERE emergency_radius_km < 1 OR emergency_radius_km > 50;

-- Sanity 13: Emergency status transitions make sense
SELECT 'MEDIUM: Emergency with resolved_at but ACTIVE status' AS sanity_check,
       COUNT(*) AS violations
FROM emergency_cases
WHERE resolved_at IS NOT NULL 
  AND emergency_status IN ('ACTIVE', 'MATCHING');


-- =====================================================
-- SECTION 3: REDISTRIBUTION & TRANSFER LOGIC
-- =====================================================

-- Sanity 14: Transfer requests are between DIFFERENT facilities
SELECT 'CRITICAL: Transfer source = destination' AS sanity_check,
       COUNT(*) AS violations
FROM transfer_requests
WHERE from_facility_id = to_facility_id;

-- Sanity 15: Both source and destination facilities are active
SELECT 'HIGH: Transfer involves inactive facility' AS sanity_check,
       COUNT(*) AS violations
FROM transfer_requests tr
LEFT JOIN facilities f_from ON tr.from_facility_id = f_from.facility_id
LEFT JOIN facilities f_to ON tr.to_facility_id = f_to.facility_id
WHERE f_from.is_active = FALSE OR f_to.is_active = FALSE;

-- Sanity 16: Source facility has available stock for transfer
SELECT 'CRITICAL: Transfer without source stock' AS sanity_check,
       COUNT(*) AS violations
FROM transfer_requests tr
LEFT JOIN inventory_current ic ON tr.from_facility_id = ic.facility_id 
  AND tr.medicine_id = ic.medicine_id
WHERE tr.transfer_status = 'APPROVED' 
  AND tr.approved_quantity > 0
  AND (ic.available_stock IS NULL OR ic.available_stock < tr.approved_quantity);

-- Sanity 17: Transfer distances are calculated and reasonable
SELECT 'MEDIUM: Transfer distance missing or unrealistic' AS sanity_check,
       COUNT(*) AS violations
FROM transfer_requests
WHERE transfer_distance_km IS NULL 
  OR transfer_distance_km < 0 
  OR transfer_distance_km > 2000;

-- Sanity 18: Donor facilities have surplus stock
SELECT 'HIGH: Recommendation from facility without surplus' AS sanity_check,
       COUNT(*) AS violations
FROM redistribution_recommendations rr
LEFT JOIN inventory_current ic_donor ON rr.donor_facility_id = ic_donor.facility_id 
  AND rr.medicine_id = ic_donor.medicine_id
WHERE rr.donor_surplus > 0 
  AND (ic_donor.available_stock IS NULL 
    OR ic_donor.available_stock < rr.donor_surplus);

-- Sanity 19: Redistribution recommendations have valid distances
SELECT 'MEDIUM: Redistribution distance unrealistic' AS sanity_check,
       COUNT(*) AS violations
FROM redistribution_recommendations
WHERE transfer_distance_km IS NULL 
  OR transfer_distance_km < 0 
  OR transfer_distance_km > 2000;

-- Sanity 20: Cascade safety logic is set
SELECT 'MEDIUM: Transfer missing cascade safety indicator' AS sanity_check,
       COUNT(*) AS violations
FROM transfer_requests
WHERE cascade_safe IS NULL;


-- =====================================================
-- SECTION 4: ANALYTICS & SCORING INTEGRITY
-- =====================================================

-- Sanity 21: Shortage scores are in valid range (0-100)
SELECT 'HIGH: Shortage score out of range' AS sanity_check,
       COUNT(*) AS violations
FROM (
    SELECT 1 FROM inventory_current WHERE shortage_score < 0 OR shortage_score > 100
    UNION ALL
    SELECT 1 FROM shortage_scores WHERE calculated_score < 0 OR calculated_score > 100
    UNION ALL
    SELECT 1 FROM regional_shortage_index WHERE average_shortage_score < 0 OR average_shortage_score > 100
) score_violations;

-- Sanity 22: Severity levels match shortage score ranges
SELECT 'MEDIUM: Severity mismatch with shortage score' AS sanity_check,
       COUNT(*) AS violations
FROM inventory_current
WHERE (shortage_score >= 75 AND severity NOT IN ('EMERGENCY', 'CRITICAL'))
   OR (shortage_score BETWEEN 50 AND 74 AND severity NOT IN ('CRITICAL', 'WARNING'))
   OR (shortage_score < 50 AND severity NOT IN ('WARNING', 'SAFE'));

-- Sanity 23: Regional shortage index aggregation is correct
SELECT 'MEDIUM: RSI affected facilities mismatch' AS sanity_check,
       COUNT(*) AS violations
FROM regional_shortage_index rsi
WHERE rsi.affected_facilities != (
    SELECT COUNT(DISTINCT facility_id)
    FROM inventory_current
    WHERE state = rsi.state 
      AND district = rsi.district 
      AND city = rsi.city
      AND medicine_id = rsi.medicine_id
      AND shortage_score > 0
);

-- Sanity 24: Outbreak signal confidence is in valid range
SELECT 'MEDIUM: Outbreak confidence out of range' AS sanity_check,
       COUNT(*) AS violations
FROM outbreak_signals
WHERE confidence_score < 0 OR confidence_score > 100;

-- Sanity 25: Outbreak consumption patterns are logical
SELECT 'MEDIUM: Outbreak spike <= 0' AS sanity_check,
       COUNT(*) AS violations
FROM outbreak_signals
WHERE outbreak_status = 'CONFIRMED' AND spike_percentage <= 0;

-- Sanity 26: Daily consumption rate is non-negative
SELECT 'HIGH: Negative daily consumption rate' AS sanity_check,
       COUNT(*) AS violations
FROM inventory_current
WHERE daily_consumption_rate < 0;

-- Sanity 27: Lead time days are reasonable
SELECT 'MEDIUM: Lead time unrealistic' AS sanity_check,
       COUNT(*) AS violations
FROM inventory_current
WHERE lead_time_days < 0 OR lead_time_days > 365;


-- =====================================================
-- SECTION 5: BUSINESS LOGIC CONSISTENCY
-- =====================================================

-- Sanity 28: Medicines with prescription requirements are critical
SELECT 'MEDIUM: Prescription medicine not marked critical' AS sanity_check,
       COUNT(*) AS violations
FROM medicine_master
WHERE prescription_required = TRUE AND is_critical = FALSE;

-- Sanity 29: Active facilities have valid facility users
SELECT 'HIGH: Active facility with no assigned users' AS sanity_check,
       COUNT(*) AS violations
FROM facilities f
WHERE f.is_active = TRUE
  AND NOT EXISTS (
    SELECT 1 FROM facility_users fu 
    WHERE fu.facility_id = f.facility_id
  );

-- Sanity 30: Alert events are for active medicines
SELECT 'MEDIUM: Alert for inactive medicine' AS sanity_check,
       COUNT(*) AS violations
FROM alert_events ae
LEFT JOIN medicine_master mm ON ae.medicine_id = mm.medicine_id
WHERE mm.is_Active = FALSE;

-- Sanity 31: Purchase transactions have valid status
SELECT 'HIGH: Invalid purchase status' AS sanity_check,
       COUNT(*) AS violations
FROM purchase_transactions
WHERE purchase_status::text NOT IN ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED');


-- Sanity 32: Geographic consistency check
-- Sanity 33: Facilities are in valid geographic locations
SELECT 'MEDIUM: Facility location has invalid coordinates' AS sanity_check,
       COUNT(*) AS violations
FROM facilities f
LEFT JOIN locations l ON f.location_id = l.location_id
WHERE (l.latitude < -90 OR l.latitude > 90 
    OR l.longitude < -180 OR l.longitude > 180);

-- Sanity 34: Emergency radius respects geographic boundaries
SELECT 'MEDIUM: Emergency radius extends beyond India' AS sanity_check,
       COUNT(*) AS violations
FROM emergency_cases ec
LEFT JOIN facilities f ON ec.facility_id = f.facility_id
LEFT JOIN locations l ON f.location_id = l.location_id
WHERE (ABS(l.latitude) + ec.emergency_radius_km / 111) > 90
   OR (ABS(l.longitude) + ec.emergency_radius_km / (111 * COS(RADIANS(l.latitude)))) > 180;


-- =====================================================
-- SUMMARY REPORT
-- =====================================================
SELECT '=== SANITY CHECK COMPLETE ===' AS status,
       CURRENT_TIMESTAMP AS check_time,
       'Review any violations above - they indicate operational problems' AS action;
