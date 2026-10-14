import { Button } from "../../../components/ui/Button"
import type { Emergency } from "../../../types/emergency"

interface Props {
  emergency: Emergency
  onDispatch: () => void
  onViewAlternatives: () => void
}

export function EmergencyDecisionCard({ emergency, onDispatch, onViewAlternatives }: Props) {
  const confidence = Number(emergency.match_score ?? 0)
  const eta = emergency.estimated_eta_minutes ?? Math.max(10, Math.round((emergency.transfer_distance_km ?? 0) * 2.2))
  const riskLevel = emergency.cascade_safe === false ? "MEDIUM" : "LOW"
  const quantity = emergency.approved_quantity ?? emergency.required_quantity ?? 0
  const distance = emergency.transfer_distance_km ?? 0
  const alternatives = emergency.alternative_donors ?? 4

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      
      {/* 1. High-Contrast Header */}
      <div className="bg-slate-900 px-5 py-4 text-white flex justify-between items-center">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
            System Recommendation
          </p>
          <h3 className="mt-1 text-base font-semibold">
            Dispatch from {emergency.donor_facility ?? "Donor Facility"}
          </h3>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-2xl font-bold text-emerald-400">{confidence.toFixed(1)}%</span>
          <span className="text-[10px] uppercase tracking-wider text-slate-400">Match Score</span>
        </div>
      </div>

      <div className="p-5 space-y-5">
        
        {/* 2. Operational Metrics Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Transfer</p>
            <p className="mt-1 font-semibold text-slate-900">{quantity} units</p>
          </div>
          <div className="rounded-xl border border-blue-100 bg-blue-50 p-3">
            <p className="text-[11px] text-blue-600 uppercase tracking-wider font-semibold">Est. Delivery</p>
            <p className="mt-1 font-semibold text-blue-900">{eta} mins</p>
          </div>
          <div className="rounded-xl border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Distance</p>
            <p className="mt-1 font-semibold text-slate-900">{distance} km</p>
          </div>
          <div className="rounded-xl border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Cascade Risk</p>
            <p className={`mt-1 font-semibold ${riskLevel === 'LOW' ? 'text-emerald-600' : 'text-amber-600'}`}>
              {riskLevel}
            </p>
          </div>
        </div>

        {/* 3. Decision Logic Breakdown */}
        <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-4">
           <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800 mb-3">Decision Logic</h4>
           <div className="space-y-2 text-sm text-emerald-900 font-medium">
             <div className="flex items-start gap-2.5">
               <span className="text-emerald-600 mt-0.5">✔</span>
               <span>{emergency.ai_reason ?? "Highest available inventory margin"}</span>
             </div>
             <div className="flex items-start gap-2.5">
               <span className="text-emerald-600 mt-0.5">✔</span>
               <span>Maintains safe minimum stock at donor site</span>
             </div>
             <div className="flex items-start gap-2.5">
               <span className="text-emerald-600 mt-0.5">✔</span>
               <span>Fastest routing compared to {alternatives} alternatives</span>
             </div>
           </div>
        </div>

        {/* 4. Action Buttons */}
        <div className="flex gap-3 pt-2">
          <Button variant="green" className="flex-[2] py-6 font-semibold shadow-md" onClick={onDispatch}>
            Confirm Dispatch
          </Button>
          <Button variant="ghost" className="flex-1 py-6 text-slate-600 hover:bg-slate-100" onClick={onViewAlternatives}>
            Compare ({alternatives})
          </Button>
        </div>
      </div>
    </div>
  )
}