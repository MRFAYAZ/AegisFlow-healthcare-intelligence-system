-- =====================================================
-- AegisFlow Geographic & Spatial Validation (Development)
-- =====================================================
-- Simplified validation for geographic and distance data
-- Focus on coordinate validity and spatial consistency
-- =====================================================

-- Section 1: LOCATION COORDINATE VALIDATION
-- =====================================================

-- Check 1: Invalid latitude values (outside -90 to 90)
SELECT 'Invalid latitude values' AS issue_type,
       COUNT(*) AS count
FROM locations
WHERE latitude < -90 OR latitude > 90;

-- Check 2: Invalid longitude values (outside -180 to 180)
SELECT 'Invalid longitude values' AS issue_type,
       COUNT(*) AS count
FROM locations
WHERE longitude < -180 OR longitude > 180;

-- Check 3: Missing geographic coordinates
SELECT 'Missing geographic coordinates' AS issue_type,
       COUNT(*) AS count
FROM locations
WHERE latitude IS NULL OR longitude IS NULL;

-- Check 4: Missing state in locations
SELECT 'Missing state in locations' AS issue_type,
       COUNT(*) AS count
FROM locations
WHERE state IS NULL OR state = '';

-- Check 5: Missing city in locations
SELECT 'Missing city in locations' AS issue_type,
       COUNT(*) AS count
FROM locations
WHERE city IS NULL OR city = '';


-- Section 2: FACILITY LOCATION INTEGRITY
-- =====================================================

-- Check 6: Active facilities without location references
SELECT 'Active facility without location' AS issue_type,
       COUNT(*) AS count
FROM facilities f
WHERE f.is_active = TRUE AND f.location_id IS NULL;

-- Check 7: Facilities with invalid location references
SELECT 'Facility with orphaned location reference' AS issue_type,
       COUNT(*) AS count
FROM facilities f
LEFT JOIN locations l ON f.location_id = l.location_id
WHERE f.location_id IS NOT NULL AND l.location_id IS NULL;


-- Section 3: TRANSFER DISTANCE VALIDATION
-- =====================================================

-- Check 8: Negative transfer distances
SELECT 'Negative transfer distance' AS issue_type,
       COUNT(*) AS count
FROM transfer_requests
WHERE transfer_distance_km < 0;

-- Check 9: Negative redistribution distances
SELECT 'Negative redistribution distance' AS issue_type,
       COUNT(*) AS count
FROM redistribution_recommendations
WHERE transfer_distance_km < 0;


-- Section 4: EMERGENCY GEOGRAPHIC VALIDATION
-- =====================================================

-- Check 10: Invalid emergency radius (outside 1-50 km)
SELECT 'Invalid emergency radius' AS issue_type,
       COUNT(*) AS count
FROM emergency_cases
WHERE emergency_radius_km < 1 OR emergency_radius_km > 50;

-- Check 11: Negative distance in emergency source matches
SELECT 'Negative distance in emergency matches' AS issue_type,
       COUNT(*) AS count
FROM emergency_source_matches
WHERE distance_km < 0;


-- Section 5: REGIONAL DATA CONSISTENCY
-- =====================================================

-- Check 12: Duplicate state-district-city combinations
SELECT 'Duplicate state-district-city' AS issue_type,
       COUNT(*) AS count
FROM (
    SELECT state, district, city
    FROM locations
    WHERE state IS NOT NULL AND city IS NOT NULL
    GROUP BY state, district, city
    HAVING COUNT(*) > 1
) duplicates;

-- Check 13: Locations with missing district
SELECT 'Location missing district' AS issue_type,
       COUNT(*) AS count
FROM locations
WHERE state IS NOT NULL AND city IS NOT NULL AND (district IS NULL OR district = '');

-- Check 14: Invalid country (not India)
SELECT 'Non-India location' AS issue_type,
       COUNT(*) AS count
FROM locations
WHERE country IS NOT NULL AND country != 'India';
