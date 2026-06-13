INSERT INTO medicine_master (
    medicine_code,
    medicine_name,
    generic_name,
    category,
    dosage_form,
    strength,
    manufacturer,
    prescription_required,
    is_critical,
    storage_conditions,
    standard_lead_time_days,
    safety_stock_days,
    unit_price,
    expiry_alert_days
)
VALUES

('PCM500','Paracetamol','Acetaminophen','Analgesic','Tablet','500mg','Sun Pharma',FALSE,FALSE,'Store Below 25C',7,15,2.50,90),

('DOLO650','Dolo 650','Paracetamol','Analgesic','Tablet','650mg','Micro Labs',FALSE,FALSE,'Store Below 25C',7,15,3.00,90),

('AMX500','Amoxicillin','Amoxicillin','Antibiotic','Capsule','500mg','Cipla',TRUE,FALSE,'Store Below 25C',10,20,12.50,120),

('AZI250','Azithromycin','Azithromycin','Antibiotic','Tablet','250mg','Sun Pharma',TRUE,FALSE,'Store Below 25C',10,20,15.00,120),

('MET500','Metformin','Metformin','Diabetes','Tablet','500mg','Dr Reddys',TRUE,TRUE,'Store Below 25C',14,30,8.50,180),

('INS100','Insulin','Human Insulin','Diabetes','Injection','100IU','Novo Nordisk',TRUE,TRUE,'Cold Storage',21,45,550.00,180),

('ORS001','ORS Sachet','ORS','Electrolyte','Powder','21g','FDC',FALSE,FALSE,'Dry Storage',5,20,18.00,365),

('SAL100','Salbutamol Inhaler','Salbutamol','Respiratory','Inhaler','100mcg','Cipla',TRUE,TRUE,'Store Below 25C',14,20,220.00,180),

('ATOR10','Atorvastatin','Atorvastatin','Cardiac','Tablet','10mg','Pfizer',TRUE,FALSE,'Store Below 25C',14,20,12.00,180),

('CEF200','Cefixime','Cefixime','Antibiotic','Tablet','200mg','Lupin',TRUE,FALSE,'Store Below 25C',10,20,25.00,180);