import type { Emergency, Transfer, Shortage, Medicine, Alert, Facility } from '../types'

export const mockEmergencies: Emergency[] = [
  { id:'E001', medicine:'Epinephrine 1mg', facility:'City General Hospital', units:0, severity:'emergency', donor:'Fortis BBT', donorUnits:24, distance:'2.1 km', eta:'22 min', status:'pending' },
  { id:'E002', medicine:'Insulin Glargine', facility:'Apollo, Koramangala', units:8, severity:'critical', donor:'Manipal Hosp.', donorUnits:50, distance:'3.8 km', eta:'35 min', status:'in_transit' },
  { id:'E003', medicine:'Dialysis Fluid 5L', facility:'Jayanagar Regional', units:12, severity:'critical', donor:'Narayana Health', donorUnits:30, distance:'4.2 km', eta:'40 min', status:'sourcing' },
]

export const mockInventory: Medicine[] = [
  { id:'M001', name:'Insulin Glargine', details:'100IU/mL · 10mL', category:'Endocrine', stock:8, maxStock:200, expiry:'Jun 2025', status:'critical', unit:'vials' },
  { id:'M002', name:'Epinephrine 1mg', details:'Auto-injector', category:'Emergency', stock:0, maxStock:50, expiry:'Sep 2025', status:'emergency', unit:'units' },
  { id:'M003', name:'Amoxicillin 500mg', details:'Capsules · strip', category:'Antibiotic', stock:420, maxStock:600, expiry:'Dec 2025', status:'adequate', unit:'strips' },
  { id:'M004', name:'Paracetamol IV', details:'1g/100mL infusion', category:'Analgesic', stock:64, maxStock:150, expiry:'Mar 2025', status:'warning', unit:'bottles' },
  { id:'M005', name:'Metformin 1000mg', details:'Extended release', category:'Endocrine', stock:310, maxStock:400, expiry:'Jan 2026', status:'adequate', unit:'strips' },
  { id:'M006', name:'Atorvastatin 20mg', details:'Film-coated tablets', category:'Cardiac', stock:180, maxStock:300, expiry:'Aug 2025', status:'adequate', unit:'strips' },
  { id:'M007', name:'Azithromycin 500mg', details:'Oral suspension', category:'Antibiotic', stock:45, maxStock:200, expiry:'Apr 2025', status:'warning', unit:'bottles' },
]

export const mockTransfers: Transfer[] = [
  { id:'#TF-2844', medicine:'Epinephrine 1mg', from:'Fortis BBT', to:'City General', quantity:'10 units', status:'in_transit', eta:'~22 min', createdAt:'2024-01-15 09:30' },
  { id:'#TF-2843', medicine:'Insulin Glargine', from:'Manipal Hosp.', to:'Apollo KMG', quantity:'50 units', status:'pending', eta:'—', createdAt:'2024-01-15 08:45' },
  { id:'#TF-2841', medicine:'Amoxicillin 500mg', from:"St. John's", to:'Fortis BBT', quantity:'200 units', status:'delivered', eta:'Done', createdAt:'2024-01-14 14:00' },
  { id:'#TF-2839', medicine:'Dialysis Fluid', from:'Narayana Health', to:'Jayanagar Reg.', quantity:'30 units', status:'sourcing', eta:'TBD', createdAt:'2024-01-14 11:20' },
]

export const mockShortages: Shortage[] = [
  { id:'S001', medicine:'Epinephrine', facility:'City General', severity:'emergency', stock:'0 units', daysLeft:0, nearestSource:'Fortis (2.1 km)' },
  { id:'S002', medicine:'Insulin Glargine', facility:'Apollo KMG', severity:'critical', stock:'8 units', daysLeft:2, nearestSource:'Transfer active' },
  { id:'S003', medicine:'Dialysis Fluid', facility:'Jayanagar Reg.', severity:'critical', stock:'12 units', daysLeft:3, nearestSource:'Manipal (4.2 km)' },
  { id:'S004', medicine:'Paracetamol IV', facility:"St. John's", severity:'warning', stock:'64 units', daysLeft:8, nearestSource:'Multiple' },
  { id:'S005', medicine:'Atorvastatin 40mg', facility:'Victoria Hosp.', severity:'warning', stock:'90 units', daysLeft:12, nearestSource:'MedPlus (1.8 km)' },
]

export const mockAlerts: Alert[] = [
  { id:'A001', type:'emergency', message:'City General Hospital: zero Epinephrine stock. Sourcing initiated.', time:'2m ago' },
  { id:'A002', type:'critical', message:'Apollo KMG: Insulin below 5-unit threshold.', time:'18m ago' },
  { id:'A003', type:'warning', message:'Transfer #TF-2841 awaiting approval from Manipal Hospital.', time:'1h ago' },
  { id:'A004', type:'resolved', message:'Amoxicillin shortage at Fortis Bannerghatta resolved via redistribution.', time:'3h ago' },
]

export const mockFacilities: Facility[] = [
  { id:'F001', name:'City General Hospital', type:'hospital', lat:12.9716, lng:77.5946, status:'emergency', address:'MG Road, Bengaluru' },
  { id:'F002', name:'Apollo KMG', type:'hospital', lat:12.9352, lng:77.6245, status:'critical', address:'Koramangala, Bengaluru' },
  { id:'F003', name:'Fortis Bannerghatta', type:'hospital', lat:12.8934, lng:77.5967, status:'stocked', address:'Bannerghatta Rd, Bengaluru' },
  { id:'F004', name:'Narayana Health', type:'hospital', lat:12.9120, lng:77.6090, status:'stocked', address:'Rajajinagar, Bengaluru' },
  { id:'F005', name:'MedPlus JP Nagar', type:'pharmacy', lat:12.9082, lng:77.5850, status:'stocked', address:'JP Nagar, Bengaluru' },
  { id:'F006', name:'Manipal Hospital', type:'hospital', lat:12.9590, lng:77.6470, status:'stocked', address:'Whitefield, Bengaluru' },
  { id:'F007', name:'Jayanagar Regional', type:'hospital', lat:12.9250, lng:77.5838, status:'low', address:'Jayanagar, Bengaluru' },
]
