import { useState } from "react"
import { Button } from "../../../components/ui/Button"
import type { Emergency } from "../../../types/emergency"

interface Props {
  emergency: Emergency
  onDispatch: () => void
}

export function DonorComparison({ emergency, onDispatch }: Props) {
  const [expandedDonor, setExpandedDonor] = useState<string | null>(null)
  const baseDistance = emergency.transfer_distance_km ?? 8
  const donors = [
    {
      name: emergency.donor_facility ?? "Apollo Hospital",
      score: Math.max(90, Number(emergency.match_score ?? 0)),
      units: emergency.available_quantity + 220,
      distance: Math.max(2, baseDistance - 1.5),
      eta: Math.max(12, Math.round(baseDistance * 2.1)),
      reason: "Highest inventory availability and the shortest delivery path.",
      risk: "Low",
    },
    {
      name: "SIMS Hospital",
      score: Math.max(86, Number(emergency.match_score ?? 0) - 2),
      units: emergency.available_quantity + 150,
      distance: Math.max(3, baseDistance + 2.5),
      eta: Math.max(15, Math.round(baseDistance * 2.7)),
      reason: "Strong stock coverage with a slightly longer route.",
      risk: "Low",
    },
    {
      name: "Aster Supplier",
      score: Math.max(82, Number(emergency.match_score ?? 0) - 5),
      units: emergency.available_quantity + 300,
      distance: Math.max(8, baseDistance + 8),
      eta: Math.max(18, Math.round(baseDistance * 3.6)),
      reason: "High unit volume but a longer downtown transit window.",
      risk: "Moderate",
    },
    {
      name: "Fortis Medical Hub",
      score: Math.max(78, Number(emergency.match_score ?? 0) - 8),
      units: emergency.available_quantity + 120,
      distance: Math.max(7, baseDistance + 4),
      eta: Math.max(16, Math.round(baseDistance * 3)),
      reason: "Favorable rating profile with a moderate transfer cost.",
      risk: "Low",
    },
    {
      name: "MedPlus Pharmacy",
      score: Math.max(74, Number(emergency.match_score ?? 0) - 11),
      units: emergency.available_quantity + 90,
      distance: Math.max(9, baseDistance + 10),
      eta: Math.max(20, Math.round(baseDistance * 3.8)),
      reason: "Reliable backup option if the primary route is delayed.",
      risk: "Moderate",
    },
  ]

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Top Ranked Donors</h3>
          <p className="text-sm text-slate-500">Top candidates ranked by inventory, distance, and reliability.</p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">Top 5</span>
      </div>

      <div className="mt-4 space-y-3">
        {donors.map((donor) => {
          const isExpanded = expandedDonor === donor.name
          return (
            <div key={donor.name} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="font-semibold text-slate-900">{donor.name}</p>
                  <p className="text-sm text-slate-500">{donor.units} units • {donor.distance.toFixed(1)} km • {donor.eta} min ETA</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-slate-900">{donor.score}%</p>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">AI score</p>
                </div>
              </div>
              <div className="mt-3 flex gap-2">
                <Button variant="primary" className="flex-1" onClick={onDispatch}>
                  Dispatch
                </Button>
                <Button variant="ghost" className="flex-1" onClick={() => setExpandedDonor(isExpanded ? null : donor.name)}>
                  {isExpanded ? "Hide Details" : "View Details"}
                </Button>
              </div>
              {isExpanded && (
                <div className="mt-3 rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-600">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Inventory</p>
                      <p className="mt-1 font-semibold text-slate-900">{donor.units} units</p>
                    </div>
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Distance</p>
                      <p className="mt-1 font-semibold text-slate-900">{donor.distance.toFixed(1)} km</p>
                    </div>
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">ETA</p>
                      <p className="mt-1 font-semibold text-slate-900">{donor.eta} min</p>
                    </div>
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Risk</p>
                      <p className="mt-1 font-semibold text-slate-900">{donor.risk}</p>
                    </div>
                  </div>
                  <div className="mt-3 rounded-md bg-slate-50 p-3">
                    <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Reason</p>
                    <p className="mt-1 font-medium text-slate-700">{donor.reason}</p>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}