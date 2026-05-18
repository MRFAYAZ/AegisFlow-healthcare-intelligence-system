-- =====================================================
-- AegisFlow Development Inventory Seed Validations
-- =====================================================
-- PURPOSE:
-- Validate seed ecosystem usability for:
-- - backend development
-- - API development
-- - frontend integration
-- - operational workflows
--
-- NOT intended for strict production auditing.
-- =====================================================


-- =====================================================
-- SECTION 1: BASIC INVENTORY EXISTENCE
-- =====================================================

SELECT
    'Inventory records exist' AS validation_name,
    COUNT(*) AS inventory_records
FROM inventory_current;


-- =====================================================
-- Ensure hospitals have inventory
-- =====================================================

SELECT
    'Hospitals with inventory' AS validation_name,
    COUNT(DISTINCT ic.facility_id) AS hospitals_with_inventory
FROM inventory_current ic
JOIN facilities f
    ON ic.facility_id = f.facility_id
WHERE f.facility_type = 'HOSPITAL';


-- =====================================================
-- Ensure medicines exist in inventory
-- =====================================================

SELECT
    'Medicines mapped into inventory' AS validation_name,
    COUNT(DISTINCT medicine_id) AS medicines_available
FROM inventory_current;


-- =====================================================
-- SECTION 2: OPERATIONAL STOCK CONSISTENCY
-- =====================================================

-- Check negative stock conditions

SELECT
    'Negative stock validation' AS validation_name,
    COUNT(*) AS invalid_records
FROM inventory_current
WHERE total_stock < 0
   OR available_stock < 0
   OR reserved_stock < 0;


-- =====================================================
-- Ensure available stock <= total stock
-- =====================================================

SELECT
    'Available stock consistency' AS validation_name,
    COUNT(*) AS invalid_records
FROM inventory_current
WHERE available_stock > total_stock;


-- =====================================================
-- Ensure reserved stock <= total stock
-- =====================================================

SELECT
    'Reserved stock consistency' AS validation_name,
    COUNT(*) AS invalid_records
FROM inventory_current
WHERE reserved_stock > total_stock;


-- =====================================================
-- Ensure minimum threshold <= reorder threshold
-- =====================================================

SELECT
    'Threshold consistency' AS validation_name,
    COUNT(*) AS invalid_records
FROM inventory_current
WHERE minimum_threshold > reorder_threshold;


-- =====================================================
-- SECTION 3: SHORTAGE INTELLIGENCE VALIDATION
-- =====================================================

-- Validate shortage score range

SELECT
    'Shortage score range validation' AS validation_name,
    COUNT(*) AS invalid_records
FROM inventory_current
WHERE shortage_score < 0
   OR shortage_score > 130;


-- =====================================================
-- Validate severity alignment
-- =====================================================

SELECT
    'Severity-score consistency' AS validation_name,
    COUNT(*) AS mismatched_records
FROM inventory_current
WHERE
    (shortage_score < 25 AND severity != 'SAFE')
 OR (shortage_score BETWEEN 25 AND 49 AND severity != 'WARNING')
 OR (shortage_score BETWEEN 50 AND 74 AND severity != 'CRITICAL')
 OR (shortage_score >= 75 AND severity != 'EMERGENCY');


-- =====================================================
-- SECTION 4: EMERGENCY INVENTORY VALIDATION
-- =====================================================

-- Ensure emergency medicines exist

SELECT
    'Emergency inventory availability' AS validation_name,
    COUNT(*) AS emergency_records
FROM inventory_current
WHERE severity = 'EMERGENCY';


-- =====================================================
-- Critical medicine availability
-- =====================================================

SELECT
    'Critical medicine availability' AS validation_name,
    COUNT(*) AS critical_medicine_records
FROM inventory_current ic
JOIN medicine_master m
    ON ic.medicine_id = m.medicine_id
WHERE m.is_critical = TRUE;


-- =====================================================
-- SECTION 5: FACILITY INVENTORY COVERAGE
-- =====================================================

-- Facilities without inventory

SELECT
    'Facilities without inventory' AS validation_name,
    COUNT(*) AS facilities_missing_inventory
FROM facilities f
WHERE f.is_active = TRUE
  AND f.facility_id NOT IN (
        SELECT DISTINCT facility_id
        FROM inventory_current
  );


-- =====================================================
-- Inventory distribution by facility
-- =====================================================

SELECT
    f.facility_name,
    COUNT(ic.inventory_id) AS inventory_records
FROM facilities f
LEFT JOIN inventory_current ic
    ON f.facility_id = ic.facility_id
GROUP BY f.facility_name
ORDER BY inventory_records DESC;


-- =====================================================
-- SECTION 6: MEDICINE COVERAGE
-- =====================================================

-- Medicines not mapped into inventory

SELECT
    'Medicines missing from inventory' AS validation_name,
    COUNT(*) AS medicines_not_seeded
FROM medicine_master m
WHERE m.medicine_id NOT IN (
    SELECT DISTINCT medicine_id
    FROM inventory_current
);


-- =====================================================
-- SECTION 7: GEO-OPERATIONAL VALIDATION
-- =====================================================

-- Facilities with valid geo coordinates

SELECT
    'Geo-enabled facilities' AS validation_name,
    COUNT(*) AS geo_facilities
FROM facilities f
JOIN locations l
    ON f.location_id = l.location_id
WHERE l.latitude IS NOT NULL
  AND l.longitude IS NOT NULL;


-- =====================================================
-- SECTION 8: DEVELOPMENT REDISTRIBUTION READINESS
-- =====================================================

-- Surplus inventory candidates

SELECT
    'Redistribution candidates' AS validation_name,
    COUNT(*) AS surplus_candidates
FROM inventory_current
WHERE available_stock > reorder_threshold
  AND shortage_score < 25;


-- =====================================================
-- Emergency shortage candidates

SELECT
    'Emergency shortage candidates' AS validation_name,
    COUNT(*) AS shortage_candidates
FROM inventory_current
WHERE shortage_score >= 75;


-- =====================================================
-- SECTION 9: FRONTEND/API READINESS
-- =====================================================

-- Inventory records usable for APIs

SELECT
    'Frontend/API ready inventory' AS validation_name,
    COUNT(*) AS api_ready_records
FROM inventory_current
WHERE total_stock IS NOT NULL
  AND available_stock IS NOT NULL
  AND severity IS NOT NULL;


-- =====================================================
-- SECTION 10: DEVELOPMENT SUMMARY
-- =====================================================

SELECT
    'DEVELOPMENT INVENTORY VALIDATION COMPLETE' AS validation_status,
    CURRENT_TIMESTAMP AS validated_at,
    'Seed ecosystem operational for backend and frontend development' AS remarks;