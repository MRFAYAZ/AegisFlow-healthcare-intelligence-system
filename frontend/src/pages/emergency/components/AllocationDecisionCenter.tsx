import { useEffect, useMemo, useState } from "react"
import { AlertTriangle, CheckCircle2, Loader2, XCircle } from "lucide-react"
import { Button } from "../../../components/ui/Button"
import { useAllocationDecision, useAllocationPlan } from "../../../hooks/useAllocationPlan"
import { useEmergencyMatches } from "../../../hooks/useEmergencyMatches"
import type { Emergency } from "../../../types/emergency"

type Props = { emergency: Emergency }
type Approval = { allocation_line_id: string; approved_quantity: number }

export function AllocationDecisionCenter({ emergency }: Props) {
  const planQuery = useAllocationPlan(emergency.emergency_case_id)
  const matchesQuery = useEmergencyMatches(emergency.emergency_case_id)
  const { approve, reject } = useAllocationDecision(emergency.emergency_case_id)
  const [quantities, setQuantities] = useState<Record<string, number>>({})

  const plan = planQuery.data
  const lines = plan?.allocation_lines ?? []
  const donorNames = useMemo<Map<string, string>>(() => {
    return new Map(
      (matchesQuery.data ?? []).map((match: any) => [match.match_id, match.facility_name])
    )
  }, [matchesQuery.data])

  useEffect(() => {
    setQuantities(
      Object.fromEntries(
        lines.map((line: any) => [line.allocation_line_id, line.recommended_quantity])
      )
    )
  }, [plan?.allocation_plan_id])

  if (planQuery.isLoading) {
    return <Panel><Loader2 className="h-5 w-5 animate-spin" /> Loading allocation recommendation...</Panel>
  }

  if (planQuery.isError) {
    return (
      <Panel>
        <AlertTriangle className="h-5 w-5 text-amber-600" />
        Allocation recommendation is not available for this emergency.
      </Panel>
    )
  }

  const approvedTotal = lines.reduce(
    (total: number, line: any) => total + (quantities[line.allocation_line_id] ?? 0),
    0
  )

  const submitApproval = () => {
    const approvals: Approval[] = lines
      .map((line: any) => ({
        allocation_line_id: line.allocation_line_id,
        approved_quantity: quantities[line.allocation_line_id] ?? 0,
      }))
      .filter((line: Approval) => line.approved_quantity > 0)
    approve.mutate(approvals)
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Allocation Plan</p>
          <h3 className="mt-1 text-xl font-bold text-slate-900">AI allocation recommendation</h3>
        </div>
        <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-bold text-amber-800">{plan.status}</span>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        <Summary label="Required" value={`${plan.requested_quantity} units`} />
        <Summary label="Recommended" value={`${plan.recommended_quantity} units`} />
        <Summary label="Fulfillment" value={`${Number(plan.fulfillment_percentage).toFixed(1)}%`} />
      </div>

      <div className="mt-5 space-y-3">
        {lines.map((line: any) => (
          <div key={line.allocation_line_id} className="rounded-lg border border-slate-200 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-semibold text-slate-900">
                  {donorNames.get(line.match_id) ?? "Donor facility"}
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  {line.distance_km} km · Safe transferable: {line.source_safe_transferable_quantity} · Score: {line.allocation_score}
                </p>
              </div>
              <label className="text-right text-xs font-semibold uppercase tracking-wider text-slate-500">
                Approve quantity
                <input
                  className="mt-1 block w-24 rounded-md border border-slate-300 px-2 py-1 text-right text-base text-slate-900"
                  type="number"
                  min={0}
                  max={line.recommended_quantity}
                  value={quantities[line.allocation_line_id] ?? 0}
                  onChange={(event) => setQuantities((current) => ({
                    ...current,
                    [line.allocation_line_id]: Math.min(
                      line.recommended_quantity,
                      Math.max(0, Number(event.target.value))
                    ),
                  }))}
                />
              </label>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-5 flex items-center justify-between border-t border-slate-200 pt-4">
        <p className="font-semibold text-slate-900">Approved total: {approvedTotal} / {plan.requested_quantity}</p>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={() => reject.mutate()} disabled={reject.isPending}>
            <XCircle className="mr-2 h-4 w-4" /> Reject
          </Button>
          <Button variant="green" onClick={submitApproval} disabled={approve.isPending || approvedTotal === 0}>
            <CheckCircle2 className="mr-2 h-4 w-4" /> Approve allocation
          </Button>
        </div>
      </div>
      {(approve.isError || reject.isError) && (
        <p className="mt-3 text-sm text-red-600">The decision could not be saved. Check your permissions and try again.</p>
      )}
    </section>
  )
}

function Panel({ children }: { children: React.ReactNode }) {
  return <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600 shadow-sm">{children}</div>
}

function Summary({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg bg-slate-50 p-3"><p className="text-xs uppercase tracking-wider text-slate-500">{label}</p><p className="mt-1 font-bold text-slate-900">{value}</p></div>
}