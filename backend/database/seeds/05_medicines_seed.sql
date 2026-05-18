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
    standard_lead_time_days,
    safety_stock_days,
    unit_price
)
VALUES
('MED001', 'Paracetamol 500mg', 'Paracetamol', 'Analgesic', 'Tablet', '500mg', 'Sun Pharma', FALSE, FALSE, 3, 5, 2.50),
('MED002', 'Insulin Injection', 'Insulin', 'Diabetes', 'Injection', '100 IU', 'Novo Nordisk', TRUE, TRUE, 7, 10, 450.00),
('MED003', 'Azithromycin 500mg', 'Azithromycin', 'Antibiotic', 'Tablet', '500mg', 'Cipla', TRUE, TRUE, 5, 7, 18.00),
('MED004', 'Amoxicillin 250mg', 'Amoxicillin', 'Antibiotic', 'Capsule', '250mg', 'Mankind', TRUE, TRUE, 4, 5, 12.00),
('MED005', 'Dolo 650', 'Paracetamol', 'Fever', 'Tablet', '650mg', 'Micro Labs', FALSE, FALSE, 2, 5, 3.50),
('MED006', 'Salbutamol Inhaler', 'Salbutamol', 'Asthma', 'Inhaler', '100mcg', 'GSK', TRUE, TRUE, 6, 8, 220.00),
('MED007', 'ORS Sachet', 'ORS', 'Hydration', 'Powder', '21g', 'Electral', FALSE, FALSE, 2, 10, 18.00),
('MED008', 'Metformin 500mg', 'Metformin', 'Diabetes', 'Tablet', '500mg', 'Sun Pharma', TRUE, TRUE, 4, 8, 7.50),
('MED009', 'Cetrizine 10mg', 'Cetirizine', 'Allergy', 'Tablet', '10mg', 'Cipla', FALSE, FALSE, 3, 5, 2.00),
('MED010', 'Pantoprazole 40mg', 'Pantoprazole', 'Gastro', 'Tablet', '40mg', 'Dr Reddy', TRUE, TRUE, 4, 5, 9.00)
ON CONFLICT DO NOTHING;