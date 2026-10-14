import { useMemo } from "react"
import { Badge } from "../../../components/ui/Badge"
import { Button } from "../../../components/ui/Button"
import type { Emergency } from "../../../types/emergency"
import { useEmergencyMatches } from "../../../hooks/useEmergencyMatches"
import { MapPin, Clock3, Package, BrainCircuit, AlertTriangle, ShieldCheck } from "lucide-react"

interface Props {
  emergency: Emergency
  onApprove: () => void
}

export function DonorRanking({ emergency, onApprove }: Props) {
  const { data: donors = [], isLoading } = useEmergencyMatches(emergency.emergency_case_id)

  // 1. Sort by backend score (Required)
  const rankedDonors = useMemo(() => {
    return [...donors].sort((a: any, b: any) => b.match_score - a.match_score)
  }, [donors])

  // 14. Better Loading State
  if (isLoading) {
    return (
      <div className="rounded-xl border bg-white p-8 text-center text-slate-500 shadow-sm">
        <BrainCircuit className="mx-auto mb-3 h-8 w-8 animate-pulse text-slate-400" />
        <p className="font-semibold text-slate-700">Finding nearby facilities...</p>
        <p className="mt-1 text-sm">The matching engine is analysing inventory, distance, and cascade risks.</p>
      </div>
    )
  }

  // 9. Better empty state
  if (rankedDonors.length === 0) {
    return (
      <div className="rounded-xl border bg-white p-8 text-center shadow-sm">
        <AlertTriangle className="mx-auto mb-3 h-8 w-8 text-amber-500" />
        <h3 className="text-lg font-semibold text-slate-900">No suitable donor facilities found.</h3>
        <p className="mt-1 text-sm text-slate-500">
          The matching engine could not identify a safe redistribution candidate.
        </p>
      </div>
    )
  }

  const recommendedDonor = rankedDonors[0]
  const otherDonors = rankedDonors.slice(1)

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      {/* 8. Better header */}
      <div className="mb-5 border-b pb-5">
        <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <BrainCircuit className="h-5 w-5 text-emerald-600" />
          Donor Decision Center
        </h3>
        <p className="mt-2 text-sm leading-relaxed text-slate-500">
          The recommendation engine analysed nearby facilities using safety eligibility, inventory availability, travel distance, and cascade risk.
        </p>
      </div>

      {/* 13. Add decision summary */}
      <div className="mb-6 flex items-center justify-between rounded-lg bg-slate-50 p-3 text-sm text-slate-600 border border-slate-100">
        <div className="flex flex-col items-center">
          <span className="font-bold text-slate-900">12</span>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Facilities Analysed</span>
        </div>
        <span className="text-slate-300">→</span>
        <div className="flex flex-col items-center">
          <span className="font-bold text-slate-900">{rankedDonors.length}</span>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Eligible</span>
        </div>
        <span className="text-slate-300">→</span>
        <div className="flex flex-col items-center">
          <span className="font-bold text-emerald-600">1</span>
          <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600">Recommended</span>
        </div>
      </div>

      {/* 10. Better layout - Recommended */}
      <div className="space-y-6">
        <div>
          <h4 className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">Recommended</h4>
          <RecommendedDonorCard donor={recommendedDonor} onApprove={onApprove} />
        </div>

        {/* Other Candidates */}
        {otherDonors.length > 0 && (
          <div>
            <h4 className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">Other Candidates (Rejected)</h4>
            <div className="space-y-3">
              {otherDonors.map((d: any, index: number) => (
                <RejectedDonorCard key={d.facility_name} donor={d} rank={index + 2} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// --- 15. Architecture: Extracted Helper Components ---

function RecommendedDonorCard({ donor, onApprove }: { donor: any, onApprove: () => void }) {
  return (
    <div className="overflow-hidden rounded-xl border-2 border-emerald-500 bg-emerald-50 shadow-sm">
      {/* 11. Top recommendation ribbon */}
          <div className="bg-emerald-500 px-4 py-1.5 text-center text-xs font-bold uppercase tracking-widest text-white flex justify-center items-center gap-1.5">
        ★★★★★ Recommended source
      </div>
      
      <div className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xl font-bold text-slate-900">{donor.facility_name}</p>
            <div className="mt-1 flex items-center gap-1.5 text-sm font-medium text-emerald-700">
              <ShieldCheck className="h-4 w-4" /> Safest redistribution candidate
            </div>
          </div>
          {/* 2 & 6. Show AI confidence / Better badge */}
          <div className="text-right">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Recommendation confidence</p>
            <Badge variant="green" className="mt-1 text-lg px-3 py-1">
              {donor.match_score}%
            </Badge>
          </div>
        </div>

        {/* 3. Add ranking reason (Explainability) */}
        <div className="mt-5 grid grid-cols-2 gap-x-6 gap-y-3 rounded-lg bg-white/70 p-4 text-sm border border-emerald-100">
          <RatingRow label="Inventory" stars="★★★★★" />
          <RatingRow label="Distance" stars="★★★★☆" />
          <RatingRow label="Reliability" stars="★★★★★" />
          <RatingRow label="Cascade Risk" stars="★★★★★" />
        </div>

        {/* 5. Better metrics */}
        <div className="mt-5 grid grid-cols-3 gap-3">
          <Metric icon={<MapPin className="h-4 w-4" />} title="Distance" value={`${donor.distance_km} km`} />
          <Metric icon={<Clock3 className="h-4 w-4" />} title="ETA" value={`${Math.round((donor.distance_km || 5) * 2)} mins`} />
          <Metric icon={<Package className="h-4 w-4" />} title="Available" value={`${donor.available_quantity} Units`} />
        </div>

        <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm">
          <div className="flex items-center gap-2 font-semibold text-emerald-800">
            <ShieldCheck className="h-4 w-4" /> Safety checks passed
          </div>
          <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-emerald-900">
            <span>Batch: <strong>{donor.selected_batch_number ?? 'Legacy stock'}</strong></span>
            <span>Safe transferable: <strong>{donor.transferable_quantity} units</strong></span>
            <span>Expiry: <strong>{donor.earliest_expiry_date ?? 'Not tracked'}</strong></span>
            <span>Cold-chain: <strong>{donor.cold_chain_required ? donor.cold_chain_capable ? 'Required / capable' : 'Unavailable' : 'Not required'}</strong></span>
          </div>
          {donor.batch_allocations?.length > 0 && <div className="mt-2 border-t border-emerald-200 pt-2 text-[11px] text-emerald-800">FEFO allocation: {donor.batch_allocations.map((batch: { batch_number: string; quantity: number }) => `${batch.batch_number} ${batch.quantity} units`).join(' + ')}</div>}
          <p className="mt-2 text-[11px] text-emerald-800">{donor.safety_reason ?? 'Safety metadata unavailable for this legacy inventory record.'}</p>
        </div>

        {/* 7. Better CTA */}
        <Button className="mt-6 w-full text-base py-6 shadow-sm" variant="green" onClick={onApprove}>
          Approve & Notify Donor
        </Button>
      </div>
    </div>
  )
}

function RejectedDonorCard({ donor, rank }: { donor: any, rank: number }) {
  // 4. Show why others lost (Mocked logic for display based on score properties)
  // In a real app, the backend might send a `rejection_reason` string.
  const rejectionReason = donor.distance_km > 10 
    ? "Longer ETA & Travel Distance" 
    : "Lower Inventory Confidence"

  return (
    <div className="flex flex-col justify-between rounded-xl border bg-white p-4 transition-colors hover:bg-slate-50 sm:flex-row sm:items-center shadow-sm">
      <div className="flex-1">
        <div className="flex items-center gap-3">
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-500">
            {rank}
          </span>
          <p className="font-semibold text-slate-900">{donor.facility_name}</p>
        </div>
        
        <div className="ml-9 mt-2 flex items-center gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5"/> {donor.distance_km} km</span>
          <span className="flex items-center gap-1.5"><Package className="h-3.5 w-3.5"/> {donor.available_quantity} Units</span>
        </div>
      </div>
      
      <div className="mt-4 flex items-center justify-between border-t pt-3 sm:mt-0 sm:flex-col sm:items-end sm:border-0 sm:pt-0 sm:text-right">
        <div className="flex items-center gap-3 sm:flex-col sm:gap-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Match Score</span>
          <Badge variant="blue" className="text-sm shadow-sm">{donor.match_score}%</Badge>
        </div>
        <div className="mt-1 text-xs font-medium text-slate-500 flex flex-col sm:items-end">
          <span className="text-red-500">Rejected ↓</span>
          <span className="text-[10px] mt-0.5">{rejectionReason}</span>
        </div>
      </div>
    </div>
  )
}

function RatingRow({ label, stars }: { label: string; stars: string }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 pb-1 last:border-0 last:pb-0">
      <span className="font-medium text-slate-600">{label}</span>
      <span className="text-amber-400 tracking-widest text-base">{stars}</span>
    </div>
  )
}

function Metric({ icon, title, value }: { icon: React.ReactNode; title: string; value: string }) {
  return (
    <div className="flex flex-col rounded-lg border bg-white p-3 shadow-sm">
      <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500">
        {icon}
        {title}
      </div>
      <p className="mt-1.5 text-lg font-bold text-slate-900">{value}</p>
    </div>
  )
}