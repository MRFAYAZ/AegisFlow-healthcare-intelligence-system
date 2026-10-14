import { useMemo, useState } from 'react'
import { useAssignDispatch, useDispatchDashboard, useDispatchTransfer, useMarkDelivered } from '../../hooks/useDispatch'
import { useAppStore } from '../../store/useAppStore'

type TransferStatus =
  | 'PENDING'
  | 'APPROVED'
  | 'REJECTED'
  | 'IN_TRANSIT'
  | 'COMPLETED'
  | 'CANCELLED'

interface TransferRow {
  transfer_id: string
  emergency_case_id?: string | null
  from_facility_name: string
  to_facility_name: string
  medicine_name: string
  approved_quantity: number
  transfer_status: TransferStatus
  transfer_distance_km?: number | null
  dispatch_status?: string | null
  dispatch_id?: string | null
  vehicle_reference?: string | null
  transport_type?: string | null
  dispatched_at?: string | null
  delivered_at?: string | null
}

const statusTone: Record<string, string> = {
  PENDING: 'bg-amber-100 text-amber-800 border border-amber-200',
  APPROVED: 'bg-blue-100 text-blue-800 border border-blue-200',
  IN_TRANSIT: 'bg-violet-100 text-violet-800 border border-violet-200',
  COMPLETED: 'bg-emerald-100 text-emerald-800 border border-emerald-200',
  REJECTED: 'bg-red-100 text-red-800 border border-red-200',
  CANCELLED: 'bg-slate-200 text-slate-700 border border-slate-300',
  ASSIGNED: 'bg-cyan-100 text-cyan-800 border border-cyan-200',
  DELIVERED: 'bg-emerald-100 text-emerald-800 border border-emerald-200',
  UNASSIGNED: 'bg-slate-100 text-slate-700 border border-slate-200',
}

const statusLabel: Record<string, string> = {
  PENDING: 'Pending',
  APPROVED: 'Approved',
  REJECTED: 'Rejected',
  IN_TRANSIT: 'In transit',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
  ASSIGNED: 'Assigned',
  DELIVERED: 'Delivered',
  UNASSIGNED: 'Unassigned',
}

export function DispatcherDashboardPage() {
  const currentUser = useAppStore((state) => state.user)
  const canDispatch = ['system_admin', 'emergency_operator', 'dispatcher'].includes(currentUser?.role ?? '')
  const { data, isLoading, isError, error } = useDispatchDashboard()
  const assignMutation = useAssignDispatch()
  const startMutation = useDispatchTransfer()
  const deliveredMutation = useMarkDelivered()
  const [assignment, setAssignment] = useState<TransferRow | null>(null)
  const [transportType, setTransportType] = useState('Hospital Delivery Van')
  const [vehicleReference, setVehicleReference] = useState('')
  const rows = (data?.transfers ?? []) as TransferRow[]

  const metrics = useMemo(() => {
    const all = rows.length
    const assigned = rows.filter((row) => {
      const status = row.dispatch_status ?? row.transfer_status
      return ['ASSIGNED', 'IN_TRANSIT', 'DELIVERED'].includes(String(status).toUpperCase())
    }).length
    const inTransit = rows.filter((row) => {
      const status = row.dispatch_status ?? row.transfer_status
      return String(status).toUpperCase() === 'IN_TRANSIT'
    }).length
    const completed = Number(data?.delivered_today ?? 0)
    const pending = Number(data?.awaiting_dispatch ?? 0)

    return { all, assigned, inTransit, completed, pending }
  }, [data, rows])

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="h-12 w-64 animate-pulse rounded bg-slate-200" />
        <div className="grid gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, idx) => (
            <div key={idx} className="h-28 animate-pulse rounded-xl bg-slate-200" />
          ))}
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
        Unable to load dispatcher data. {String((error as Error)?.message ?? 'Please check backend connectivity.')}
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6 bg-slate-50 min-h-screen">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Operations</p>
          <h1 className="mt-1 text-3xl font-bold text-slate-900">Dispatcher dashboard</h1>
        </div>
        <div className="flex items-center gap-3">
          <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600 shadow-sm">
            Live updates: {rows.length} transfer records
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-100 px-3 py-2 text-xs font-medium uppercase tracking-[0.2em] text-slate-600">
            {currentUser?.role ?? 'system_admin'}
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Active transfers</p>
          <p className="mt-3 text-3xl font-bold text-slate-900">{metrics.all}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Assigned</p>
          <p className="mt-3 text-3xl font-bold text-sky-700">{metrics.assigned}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">In transit</p>
          <p className="mt-3 text-3xl font-bold text-violet-700">{metrics.inTransit}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">Delivered</p>
          <p className="mt-3 text-3xl font-bold text-emerald-700">{metrics.completed}</p>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.7fr_1fr]">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Dispatch queue</h2>
            <span className="text-xs font-medium uppercase tracking-[0.22em] text-slate-500">Backend data</span>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500">
                  <th className="pb-3 font-medium">Transfer</th>
                  <th className="pb-3 font-medium">Medicine</th>
                  <th className="pb-3 font-medium">Route</th>
                  <th className="pb-3 font-medium">Qty</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => {
                  const transferStatus = String(row.transfer_status ?? 'PENDING').toUpperCase()
                  const dispatchStatus = String(row.dispatch_status ?? 'UNASSIGNED').toUpperCase()
                  const activeStatus = dispatchStatus === 'UNASSIGNED' ? transferStatus : dispatchStatus

                  return (
                    <tr key={row.transfer_id} className="border-b border-slate-100 last:border-b-0 align-top">
                      <td className="py-3 pr-3">
                        <div className="font-medium text-slate-900">{row.transfer_id.slice(0, 8).toUpperCase()}</div>
                        <div className="text-xs text-slate-500">{row.emergency_case_id ? 'Emergency transfer' : 'Operational transfer'}</div>
                      </td>
                      <td className="py-3 pr-3">
                        <div className="font-medium text-slate-800">{row.medicine_name}</div>
                        <div className="text-xs text-slate-500">{row.approved_quantity} approved</div>
                      </td>
                      <td className="py-3 pr-3 text-slate-600">
                        <div>{row.from_facility_name}</div>
                        <div className="text-xs text-slate-400">→ {row.to_facility_name}</div>
                      </td>
                      <td className="py-3 pr-3 text-slate-700">{row.approved_quantity}</td>
                      <td className="py-3 pr-3">
                        <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${statusTone[activeStatus] ?? statusTone.UNASSIGNED}`}>
                          {statusLabel[activeStatus] ?? activeStatus}
                        </span>
                        {row.vehicle_reference && (
                          <div className="mt-2 text-[11px] text-slate-500">Vehicle: {row.vehicle_reference}</div>
                        )}
                      </td>
                      <td className="py-3">
                        {transferStatus === 'APPROVED' && canDispatch && (
                          <button
                            onClick={() => {
                              setAssignment(row)
                              setVehicleReference('')
                            }}
                            className="rounded bg-sky-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-sky-700 disabled:opacity-60"
                            disabled={assignMutation.isPending}
                          >
                            Assign
                          </button>
                        )}
                        {dispatchStatus === 'ASSIGNED' && canDispatch && (
                          <button
                            onClick={() => startMutation.mutate(row.transfer_id)}
                            className="rounded bg-violet-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-violet-700 disabled:opacity-60"
                            disabled={startMutation.isPending}
                          >
                            Start
                          </button>
                        )}
                        {dispatchStatus === 'IN_TRANSIT' && canDispatch && (
                          <button
                            onClick={() => deliveredMutation.mutate(row.transfer_id)}
                            className="rounded bg-emerald-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
                            disabled={deliveredMutation.isPending}
                          >
                            Delivered
                          </button>
                        )}
                        {!canDispatch && (
                          <span className="text-xs text-slate-400">View only</span>
                        )}
                        {canDispatch && !['APPROVED', 'ASSIGNED', 'IN_TRANSIT'].includes(transferStatus) && !['APPROVED', 'ASSIGNED', 'IN_TRANSIT'].includes(dispatchStatus) && (
                          <span className="text-xs text-slate-400">No action</span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Operational summary</h2>
          <div className="space-y-3">
            {[
              { label: 'Pending approvals', value: metrics.pending, tone: 'bg-amber-50 text-amber-700' },
              { label: 'Assigned vehicles', value: metrics.assigned, tone: 'bg-sky-50 text-sky-700' },
              { label: 'En route', value: metrics.inTransit, tone: 'bg-violet-50 text-violet-700' },
              { label: 'Delivered', value: metrics.completed, tone: 'bg-emerald-50 text-emerald-700' },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                <span className="text-sm text-slate-600">{item.label}</span>
                <span className={`inline-flex min-w-10 justify-center rounded-full px-2 py-1 text-sm font-semibold ${item.tone}`}>
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {assignment && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Transport assignment</p>
                <h2 className="mt-1 text-xl font-semibold text-slate-900">{assignment.medicine_name}</h2>
              </div>
              <button type="button" onClick={() => setAssignment(null)} className="text-sm text-slate-500 hover:text-slate-900">Close</button>
            </div>
            <div className="mt-5 space-y-4">
              <label className="block text-sm font-medium text-slate-700">
                Transport type
                <select value={transportType} onChange={(event) => setTransportType(event.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
                  <option>Hospital Delivery Van</option>
                  <option>Authorized Staff Vehicle</option>
                  <option>Healthcare Logistics Partner</option>
                </select>
              </label>
              <label className="block text-sm font-medium text-slate-700">
                Vehicle reference
                <input value={vehicleReference} onChange={(event) => setVehicleReference(event.target.value)} placeholder="VH-204" className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
              </label>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button type="button" onClick={() => setAssignment(null)} className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700">Cancel</button>
              <button
                type="button"
                disabled={!vehicleReference.trim() || assignMutation.isPending}
                onClick={() => assignMutation.mutate({
                  transferId: assignment.transfer_id,
                  transportType,
                  vehicleReference: vehicleReference.trim(),
                }, { onSuccess: () => setAssignment(null) })}
                className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                {assignMutation.isPending ? 'Assigning...' : 'Assign'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
