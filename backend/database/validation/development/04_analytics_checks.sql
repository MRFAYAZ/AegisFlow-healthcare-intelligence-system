-- =====================================================
-- AegisFlow Analytics Validation Checks (Development)
-- =====================================================
-- Simplified validation for analytics and metrics tables
-- Focus on data integrity and logical consistency
-- =====================================================

-- Section 1: SHORTAGE SCORES VALIDATION
-- =====================================================

-- Check 1: Negative shortage scores
SELECT 'Negative shortage scores' AS issue_type,
       COUNT(*) AS count
FROM shortage_scores
WHERE calculated_score < 0;

-- Check 2: Negative current stock in shortage scores
SELECT 'Negative current stock in scores' AS issue_type,
       COUNT(*) AS count
FROM shortage_scores
WHERE current_stock < 0;

-- Check 3: Orphaned shortage score facility references
SELECT 'Orphaned shortage score facility' AS issue_type,
       COUNT(*) AS count
FROM shortage_scores ss
LEFT JOIN facilities f ON ss.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 4: Orphaned shortage score medicine references
SELECT 'Orphaned shortage score medicine' AS issue_type,
       COUNT(*) AS count
FROM shortage_scores ss
LEFT JOIN medicine_master m ON ss.medicine_id = m.medicine_id
WHERE m.medicine_id IS NULL;


-- Section 2: INVENTORY METRICS VALIDATION
-- =====================================================

-- Check 5: Negative available stock in metrics
SELECT 'Negative available stock in metrics' AS issue_type,
       COUNT(*) AS count
FROM fact_inventory_metrics
WHERE available_stock < 0;

-- Check 6: Negative counts in inventory metrics
SELECT 'Negative counts in metrics' AS issue_type,
       COUNT(*) AS count
FROM fact_inventory_metrics
WHERE transfer_requests_count < 0 OR emergency_count < 0;

-- Check 7: Orphaned fact inventory metrics facility
SELECT 'Orphaned metrics facility reference' AS issue_type,
       COUNT(*) AS count
FROM fact_inventory_metrics fim
LEFT JOIN facilities f ON fim.facility_id = f.facility_id
WHERE f.facility_id IS NULL;

-- Check 8: Orphaned fact inventory metrics medicine
SELECT 'Orphaned metrics medicine reference' AS issue_type,
       COUNT(*) AS count
FROM fact_inventory_metrics fim
LEFT JOIN medicine_master m ON fim.medicine_id = m.medicine_id
WHERE fim.medicine_id IS NOT NULL AND m.medicine_id IS NULL;


-- Section 3: REGIONAL SHORTAGE INDEX VALIDATION
-- =====================================================

-- Check 9: Invalid regional shortage index scores
SELECT 'Invalid regional shortage score' AS issue_type,
       COUNT(*) AS count
FROM regional_shortage_index
WHERE average_shortage_score < 0 OR average_shortage_score > 100;

-- Check 10: Negative affected facilities count
SELECT 'Negative affected facilities count' AS issue_type,
       COUNT(*) AS count
FROM regional_shortage_index
WHERE affected_facilities < 0;

-- Check 11: Negative emergency facilities count
SELECT 'Negative emergency facilities count' AS issue_type,
       COUNT(*) AS count
FROM regional_shortage_index
WHERE emergency_facilities < 0;

-- Check 12: Orphaned regional shortage index medicine
SELECT 'Orphaned regional shortage medicine' AS issue_type,
       COUNT(*) AS count
FROM regional_shortage_index rsi
LEFT JOIN medicine_master m ON rsi.medicine_id = m.medicine_id
WHERE rsi.medicine_id IS NOT NULL AND m.medicine_id IS NULL;


-- Section 4: OUTBREAK SIGNALS VALIDATION
-- =====================================================

-- Check 13: Invalid outbreak status values
SELECT 'Invalid outbreak status' AS issue_type,
       COUNT(*) AS count
FROM outbreak_signals
WHERE outbreak_status NOT IN ('DETECTED', 'UNDER_REVIEW', 'CONFIRMED', 'RESOLVED');

-- Check 14: Invalid confidence scores (outside 0-100)
SELECT 'Invalid outbreak confidence score' AS issue_type,
       COUNT(*) AS count
FROM outbreak_signals
WHERE confidence_score < 0 OR confidence_score > 100;

-- Check 15: Negative affected facilities in outbreak
SELECT 'Negative affected facilities in outbreak' AS issue_type,
       COUNT(*) AS count
FROM outbreak_signals
WHERE affected_facilities < 0;

-- Check 16: Negative consumption values in outbreak
SELECT 'Negative consumption in outbreak' AS issue_type,
       COUNT(*) AS count
FROM outbreak_signals
WHERE baseline_consumption < 0 OR current_consumption < 0 OR spike_percentage < 0;

-- Check 17: Orphaned outbreak signals medicine
SELECT 'Orphaned outbreak signals medicine' AS issue_type,
       COUNT(*) AS count
FROM outbreak_signals os
LEFT JOIN medicine_master m ON os.medicine_id = m.medicine_id
WHERE os.medicine_id IS NOT NULL AND m.medicine_id IS NULL;
