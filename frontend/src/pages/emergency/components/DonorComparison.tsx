import { useQuery } from "@tanstack/react-query"
import { emergencyAPI } from "../../../services/api"
import { Button } from "../../../components/ui/Button"
import type { EmergencyMatch } from "../../../types/match"
import type { Emergency } from "../../../types/emergency"
import { useCurrentUser } from "../../../hooks/useCurrentUser"

interface Props {
  emergency: Emergency
  onRequestTransfer: () => void
  requestDisabled: boolean
  requestLabel: string
}

export function DonorComparison({
  emergency,
  onRequestTransfer,
  requestDisabled,
  requestLabel,
}: Props) {
  const { data: user } = useCurrentUser()
  const {
    data: donors = [],
    isLoading,
    isError,
    error,
  } = useQuery<EmergencyMatch[]>({
    queryKey: ["emergency-matches", user?.id ?? "anonymous", emergency.emergency_case_id],
    queryFn: async () => {
      const response = await emergencyAPI.getMatches(emergency.emergency_case_id)
      return response.data
    },
    enabled: Boolean(user?.id && emergency.emergency_case_id),
    staleTime: 15_000,
  })

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Network donor recommendations</h3>
          <p className="mt-1 text-sm text-slate-500">
            Backend-ranked candidates across active facilities, using transferable inventory, donor stock protection and geographic distance.
          </p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
          {isLoading ? "Loading" : `${donors.length} candidates`}
        </span>
      </div>

      <p className="mt-3 rounded-lg border border-blue-100 bg-blue-50 p-3 text-xs text-blue-800">
        Distance is a straight-line geographic estimate, not a driving route or guaranteed delivery ETA.
        Recommendations do not authorize stock movement. The destination hospital must review each generated request.
      </p>

      {isLoading && (
        <div className="mt-4 animate-pulse rounded-xl bg-slate-100 p-5 text-sm text-slate-500">
          Evaluating available facilities…
        </div>
      )}

      {isError && (
        <div role="alert" className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          Unable to load donor recommendations. {(error as Error).message}
        </div>
      )}

      {!isLoading && !isError && donors.length === 0 && (
        <div className="mt-4 rounded-xl border border-dashed border-slate-300 p-6 text-center">
          <p className="font-semibold text-slate-800">No eligible donor found</p>
          <p className="mt-1 text-sm text-slate-500">
            No active facility with safe transferable stock was found within the emergency's configured radius.
          </p>
        </div>
      )}

      <div className="mt-4 space-y-3">
        {donors.map((donor) => (
          <article key={donor.facility_id} className="rounded-xl border border-slate-200 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-md bg-slate-900 px-2 py-1 text-xs font-semibold text-white">
                    #{donor.rank}
                  </span>
                  <h4 className="font-semibold text-slate-900">{donor.facility_name}</h4>
                </div>
                <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">
                  {donor.facility_type.replaceAll("_", " ")}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xl font-semibold text-slate-900">{donor.ranking_score.toFixed(1)}</p>
                <p className="text-xs text-slate-500">Match score / 100</p>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-3 gap-2">
              <Metric label="Safe transferable" value={`${donor.transferable_quantity} units`} />
              <Metric label="Suggested" value={`${donor.suggested_quantity} units`} />
              <Metric label="Distance" value={`${donor.distance_km.toFixed(1)} km`} />
              <Metric label="Verified batches" value={String(donor.eligible_batch_count)} />
              <Metric label="Nearest expiry" value={donor.nearest_expiry_date} />
              <Metric label="Cold-chain capability" value={donor.cold_chain_capable ? "Verified" : "Not declared"} />
            </div>

            <div className="mt-3 rounded-lg border border-emerald-100 bg-emerald-50 p-3 text-xs text-emerald-900">
              Expiry verified: {donor.eligible_batch_count} unexpired batch(es) available; nearest expiry {donor.nearest_expiry_date}. Allocation reserves eligible lots FEFO.
              {donor.requires_cold_chain ? " Cold-chain capability is required and verified for this donor." : " No cold-chain requirement is recorded for this medicine."}
            </div>

            <details className="mt-3 rounded-lg bg-slate-50 p-3">
              <summary className="cursor-pointer text-sm font-medium text-slate-800">
                Why this facility was ranked #{donor.rank}
              </summary>
              <p className="mt-2 text-sm text-slate-600">{donor.recommendation_reason}</p>
              <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                <Metric label="Distance factor" value={donor.score_breakdown.distance_score.toFixed(3)} />
                <Metric label="Inventory factor" value={donor.score_breakdown.inventory_score.toFixed(3)} />
                <Metric label="Donor health" value={donor.score_breakdown.donor_health_score.toFixed(3)} />
              </div>
              <p className="mt-2 text-xs text-slate-500">
                Weights — distance {(donor.score_breakdown.distance_weight * 100).toFixed(0)}%,
                inventory {(donor.score_breakdown.inventory_weight * 100).toFixed(0)}%,
                donor health {(donor.score_breakdown.donor_health_weight * 100).toFixed(0)}%.
              </p>
            </details>
          </article>
        ))}
      </div>

      <div className="mt-5 border-t border-slate-200 pt-4">
        <Button
          className="w-full"
          variant="primary"
          onClick={onRequestTransfer}
          disabled={requestDisabled || isLoading || isError || donors.length === 0}
        >
          {requestLabel}
        </Button>
        <p className="mt-2 text-xs text-slate-500">
          The request builder may create several donor transfer legs to cover the remaining demand. Inventory is reserved only after approval.
        </p>
      </div>
    </section>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-2">
      <p className="text-[10px] uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-slate-900">{value}</p>
    </div>
  )
}
