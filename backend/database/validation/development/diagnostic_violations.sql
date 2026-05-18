-- =====================================================
-- DIAGNOSTIC QUERIES TO IDENTIFY SPECIFIC VIOLATIONS
-- =====================================================

-- Find transfers without source stock
SELECT 'TRANSFER WITHOUT SOURCE STOCK' AS violation_type,
       tr.transfer_id,
       tr.from_facility_id,
       tr.medicine_id,
       tr.approved_quantity,
       ic.available_stock,
       tr.transfer_status
FROM transfer_requests tr
LEFT JOIN inventory_current ic ON tr.from_facility_id = ic.facility_id 
  AND tr.medicine_id = ic.medicine_id
WHERE tr.transfer_status = 'APPROVED' 
  AND tr.approved_quantity > 0
  AND (ic.available_stock IS NULL OR ic.available_stock < tr.approved_quantity);

-- Find recommendations without surplus
SELECT 'RECOMMENDATION WITHOUT SURPLUS' AS violation_type,
       rr.recommendation_id,
       rr.donor_facility_id,
       rr.medicine_id,
       rr.donor_surplus,
       ic.available_stock
FROM redistribution_recommendations rr
LEFT JOIN inventory_current ic ON rr.donor_facility_id = ic.facility_id 
  AND rr.medicine_id = ic.medicine_id
WHERE rr.donor_surplus > 0 
  AND (ic.available_stock IS NULL 
    OR ic.available_stock < rr.donor_surplus);

-- Find shortage scores out of range
SELECT 'SHORTAGE SCORE OUT OF RANGE' AS violation_type,
       inventory_id,
       facility_id,
       medicine_id,
       shortage_score,
       severity
FROM inventory_current
WHERE shortage_score < 0 OR shortage_score > 100;

-- Find prescription medicines not marked critical
SELECT 'PRESCRIPTION MEDICINE NOT CRITICAL' AS violation_type,
       medicine_id,
       medicine_code,
       medicine_name,
       prescription_required,
       is_critical
FROM medicine_master
WHERE prescription_required = TRUE AND is_critical = FALSE;
