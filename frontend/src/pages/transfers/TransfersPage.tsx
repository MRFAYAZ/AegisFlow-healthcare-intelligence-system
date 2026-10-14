import { useMemo, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { transferAPI } from "../../services/api"
import { Badge } from "../../components/ui/Badge"
import { Button } from "../../components/ui/Button"
import { Modal } from "../../components/ui/Modal"
import type { TransferRecord, TransferStatus } from "../../types/transfer-record"
import { useCurrentUser } from "../../hooks/useCurrentUser"

function getErrorMessage(error: unknown): string {
  if (typeof error === "object" && error !== null && "response" in error) {
    const response = (error as { response?: { data?: { detail?: string } } }).response
    if (response?.data?.detail) return response.data.detail
  }
  if (error instanceof Error) return error.message
  return "The action could not be completed."
}

function displayStatus(status: TransferStatus) {
  return status.replaceAll("_", " ")
}

function transferVariant(status: TransferStatus): "blue" | "yellow" | "green" | "red" | "orange" {
  if (status === "COMPLETED") return "green"
  if (status === "IN_TRANSIT") return "blue"
  if (status === "PENDING") return "yellow"
  if (status === "REJECTED" || status === "CANCELLED") return "red"
  return "orange"
}

function time(value?: string | null) {
  return value ? new Date(value).toLocaleString() : "Not recorded"
}

export function TransfersPage() {
  const queryClient = useQueryClient()
  const { data: user } = useCurrentUser()
  const isNetworkOperations = user?.role === "system_admin" || user?.role === "emergency_operator"
  const canApproveTransfer = (transfer: TransferRecord) =>
    user?.role === "system_admin"
    || (user?.role === "hospital_admin" && Boolean(user.facilityIds?.includes(transfer.to_facility_id)))
  const { data: transfers = [], isLoading, isError, error } = useQuery<TransferRecord[]>({
    queryKey: ["transfers", "backend"],
    queryFn: async () => (await transferAPI.getAll()).data as TransferRecord[],
    refetchInterval: 10_000,
    refetchOnWindowFocus: true,
  })

  const [approveTarget, setApproveTarget] = useState<TransferRecord | null>(null)
  const [rejectTarget, setRejectTarget] = useState<TransferRecord | null>(null)
  const [assignTarget, setAssignTarget] = useState<TransferRecord | null>(null)
  const [trackTarget, setTrackTarget] = useState<TransferRecord | null>(null)
  const [approvalQuantity, setApprovalQuantity] = useState("1")
  const [rejectionReason, setRejectionReason] = useState("")
  const [transportType, setTransportType] = useState("Hospital vehicle")
  const [vehicleReference, setVehicleReference] = useState("")
  const [isSaving, setIsSaving] = useState(false)

  const summary = useMemo(() => ({
    total: transfers.length,
    awaitingDecision: transfers.filter((t) => t.transfer_status === "PENDING").length,
    awaitingDispatch: transfers.filter((t) => t.transfer_status === "APPROVED" && !t.dispatch_status).length,
    inTransit: transfers.filter((t) => t.transfer_status === "IN_TRANSIT").length,
    completed: transfers.filter((t) => t.transfer_status === "COMPLETED").length,
  }), [transfers])

  async function refreshOperationalData() {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["transfers", "backend"] }),
      queryClient.invalidateQueries({ queryKey: ["redistribution"] }),
      queryClient.invalidateQueries({ queryKey: ["emergencies"] }),
      queryClient.invalidateQueries({ queryKey: ["inventory"] }),
      queryClient.invalidateQueries({ queryKey: ["emergency-timeline"] }),
    ])
  }

  async function submitApprove() {
    if (!approveTarget || isSaving) return
    const quantity = Number(approvalQuantity)
    if (!Number.isInteger(quantity) || quantity <= 0) {
      toast.error("Approved quantity must be a positive whole number.")
      return
    }
    setIsSaving(true)
    try {
      await transferAPI.approve(approveTarget.transfer_id, quantity)
      toast.success("Transfer approved and donor stock reserved.")
      setApproveTarget(null)
      await refreshOperationalData()
    } catch (e) {
      toast.error(getErrorMessage(e))
    } finally {
      setIsSaving(false)
    }
  }

  async function submitReject() {
    if (!rejectTarget || isSaving) return
    if (rejectionReason.trim().length < 5) {
      toast.error("Enter a rejection reason of at least five characters.")
      return
    }
    setIsSaving(true)
    try {
      await transferAPI.reject(rejectTarget.transfer_id, rejectionReason.trim())
      toast.success("Transfer request rejected.")
      setRejectTarget(null)
      setRejectionReason("")
      await refreshOperationalData()
    } catch (e) {
      toast.error(getErrorMessage(e))
    } finally {
      setIsSaving(false)
    }
  }

  async function submitAssign() {
    if (!assignTarget || isSaving) return
    if (transportType.trim().length < 2) {
      toast.error("Enter a transport type.")
      return
    }
    setIsSaving(true)
    try {
      await transferAPI.assignDispatch(
        assignTarget.transfer_id,
        transportType.trim(),
        vehicleReference.trim() || undefined,
      )
      toast.success("Transport assignment recorded.")
      setAssignTarget(null)
      setVehicleReference("")
      await refreshOperationalData()
    } catch (e) {
      toast.error(getErrorMessage(e))
    } finally {
      setIsSaving(false)
    }
  }

  async function dispatch(record: TransferRecord) {
    setIsSaving(true)
    try {
      await transferAPI.dispatch(record.transfer_id)
      toast.success("Shipment marked in transit.")
      await refreshOperationalData()
    } catch (e) {
      toast.error(getErrorMessage(e))
    } finally {
      setIsSaving(false)
    }
  }

  async function deliver(record: TransferRecord) {
    const confirmed = window.confirm(
      `Confirm that ${record.approved_quantity ?? 0} units of ${record.medicine_name} have physically arrived at ${record.to_facility_name}? This settles both facilities' inventory.`,
    )
    if (!confirmed || isSaving) return
    setIsSaving(true)
    try {
      await transferAPI.markDelivered(record.transfer_id)
      toast.success("Delivery recorded and inventory settlement completed.")
      await refreshOperationalData()
    } catch (e) {
      toast.error(getErrorMessage(e))
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-5">
      <section className="panel">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="panel-title">Transfer control center</div>
            <p className="mt-1 text-sm text-ink-muted">
              Backend-recorded transfer requests, human approval, transport assignment, dispatch and delivery settlement.
            </p>
          </div>
          <Badge variant="blue">Server workflow</Badge>
        </div>

        <div className="mb-5 grid grid-cols-2 gap-3 md:grid-cols-5">
          <Metric label="Total transfer legs" value={summary.total} />
          <Metric label="Awaiting decision" value={summary.awaitingDecision} />
          <Metric label="Awaiting transport" value={summary.awaitingDispatch} />
          <Metric label="In transit" value={summary.inTransit} />
          <Metric label="Completed" value={summary.completed} />
        </div>

        {isLoading && <div className="rounded-lg bg-slate-50 p-6 text-sm text-slate-500">Loading backend transfer records…</div>}

        {isError && (
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            Transfer records could not be loaded. {getErrorMessage(error)}
          </div>
        )}

        {!isLoading && !isError && transfers.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center">
            <p className="font-semibold text-slate-900">No transfer requests recorded</p>
            <p className="mt-1 text-sm text-slate-500">
              Open an emergency, review ranked donors, and create a supply request. This table does not generate mock transfers.
            </p>
          </div>
        )}

        {!isLoading && !isError && transfers.length > 0 && (
          <div className="overflow-x-auto">
            <table className="af-table min-w-[1050px]">
              <thead>
                <tr>
                  <th>Transfer ID</th>
                  <th>Medicine</th>
                  <th>Donor facility</th>
                  <th>Receiving facility</th>
                  <th>Requested / approved</th>
                  <th>Match / distance</th>
                  <th>Transfer / dispatch state</th>
                  <th>Next action</th>
                </tr>
              </thead>
              <tbody>
                {transfers.map((record) => (
                  <tr key={record.transfer_id}>
                    <td>
                      <button className="font-medium text-blue-700 hover:underline" onClick={() => setTrackTarget(record)}>
                        #{record.transfer_id.slice(0, 8)}
                      </button>
                      <p className="mt-1 text-[10px] text-ink-muted">{time(record.requested_at)}</p>
                    </td>
                    <td>
                      <p className="font-medium">{record.medicine_name}</p>
                      <p className="text-[10px] text-ink-muted">{record.emergency_case_id ? `Emergency #${record.emergency_case_id.slice(0, 8)}` : "Non-emergency"}</p>
                    </td>
                    <td>{record.from_facility_name}</td>
                    <td>{record.to_facility_name}</td>
                    <td>
                      <p>{record.requested_quantity} requested</p>
                      <p className="text-xs text-ink-muted">{record.approved_quantity ?? "—"} approved</p>
                    </td>
                    <td>
                      <p>{record.match_score === null ? "—" : Number(record.match_score).toFixed(1)}</p>
                      <p className="text-xs text-ink-muted">
                        {record.transfer_distance_km === null ? "Distance —" : `${Number(record.transfer_distance_km).toFixed(1)} km straight-line`}
                      </p>
                    </td>
                    <td>
                      <div className="space-y-1">
                        <Badge variant={transferVariant(record.transfer_status)}>{displayStatus(record.transfer_status)}</Badge>
                        {record.dispatch_status && <p className="text-[10px] text-ink-muted">Dispatch: {record.dispatch_status.replaceAll("_", " ")}</p>}
                      </div>
                    </td>
                    <td>
                      <div className="flex flex-wrap gap-1.5">
                        {record.transfer_status === "PENDING" && canApproveTransfer(record) && (
                          <>
                            <Button size="sm" variant="green" onClick={() => { setApprovalQuantity(String(record.requested_quantity)); setApproveTarget(record) }} disabled={isSaving}>Review</Button>
                            <Button size="sm" variant="red" onClick={() => { setRejectTarget(record); setRejectionReason("") }} disabled={isSaving}>Reject</Button>
                          </>
                        )}
                        {record.transfer_status === "PENDING" && !canApproveTransfer(record) && (
                          <span className="text-xs text-ink-muted">Destination hospital decision required</span>
                        )}
                        {record.transfer_status === "APPROVED" && !record.dispatch_status && isNetworkOperations && (
                          <Button size="sm" variant="primary" onClick={() => { setAssignTarget(record); setTransportType("Hospital vehicle") }} disabled={isSaving}>Assign transport</Button>
                        )}
                        {record.transfer_status === "APPROVED" && record.dispatch_status === "ASSIGNED" && isNetworkOperations && (
                          <Button size="sm" variant="primary" onClick={() => void dispatch(record)} disabled={isSaving}>Dispatch</Button>
                        )}
                        {record.transfer_status === "IN_TRANSIT" && isNetworkOperations && (
                          <Button size="sm" variant="green" onClick={() => void deliver(record)} disabled={isSaving}>Confirm delivery</Button>
                        )}
                        {["COMPLETED", "REJECTED", "CANCELLED"].includes(record.transfer_status) && (
                          <span className="text-xs text-ink-muted">No action</span>
                        )}
                        {["APPROVED", "IN_TRANSIT"].includes(record.transfer_status) && !isNetworkOperations && (
                          <span className="text-xs text-ink-muted">Operations role required</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <p className="mt-3 text-xs text-ink-muted">
          Approval/reservation and delivery/settlement are backend transactions. A 403 indicates the signed-in role lacks permission for that action.
        </p>
      </section>

      {approveTarget && (
        <Modal
          open
          title="Review transfer request"
          subtitle={`Transfer #${approveTarget.transfer_id.slice(0, 8)}`}
          onClose={() => !isSaving && setApproveTarget(null)}
          footer={<><Button variant="ghost" onClick={() => setApproveTarget(null)} disabled={isSaving}>Cancel</Button><Button variant="green" onClick={() => void submitApprove()} disabled={isSaving}>{isSaving ? "Saving…" : "Approve & reserve stock"}</Button></>}
        >
          <p className="mb-3 text-sm text-slate-600">
            {approveTarget.from_facility_name} → {approveTarget.to_facility_name}, {approveTarget.medicine_name}.
            Approval rechecks donor inventory against its minimum stock threshold and reserves the approved units.
          </p>
          <label className="f-label" htmlFor="approved-quantity">Quantity to approve</label>
          <input id="approved-quantity" className="f-input" type="number" min="1" max={approveTarget.requested_quantity} value={approvalQuantity} onChange={(e) => setApprovalQuantity(e.target.value)} />
          <p className="mt-1 text-xs text-slate-500">Requested: {approveTarget.requested_quantity} units. Partial approval is allowed.</p>
        </Modal>
      )}

      {rejectTarget && (
        <Modal
          open
          title="Reject transfer request"
          subtitle={`Transfer #${rejectTarget.transfer_id.slice(0, 8)}`}
          onClose={() => !isSaving && setRejectTarget(null)}
          footer={<><Button variant="ghost" onClick={() => setRejectTarget(null)} disabled={isSaving}>Cancel</Button><Button variant="red" onClick={() => void submitReject()} disabled={isSaving}>{isSaving ? "Saving…" : "Record rejection"}</Button></>}
        >
          <label className="f-label" htmlFor="rejection-reason">Reason for rejection</label>
          <textarea id="rejection-reason" className="f-input min-h-24" value={rejectionReason} onChange={(e) => setRejectionReason(e.target.value)} placeholder="e.g. Quantity required for our own critical demand" />
          <p className="mt-1 text-xs text-slate-500">A reason is recorded with the hospital decision.</p>
        </Modal>
      )}

      {assignTarget && (
        <Modal
          open
          title="Assign transport"
          subtitle={`Transfer #${assignTarget.transfer_id.slice(0, 8)}`}
          onClose={() => !isSaving && setAssignTarget(null)}
          footer={<><Button variant="ghost" onClick={() => setAssignTarget(null)} disabled={isSaving}>Cancel</Button><Button variant="primary" onClick={() => void submitAssign()} disabled={isSaving}>{isSaving ? "Saving…" : "Save assignment"}</Button></>}
        >
          <p className="mb-3 text-sm text-slate-600">
            Assign a transport resource for the approved {assignTarget.approved_quantity} units. This does not mark the shipment as dispatched.
          </p>
          <label className="f-label" htmlFor="transport-type">Transport type</label>
          <select id="transport-type" className="f-input mb-3" value={transportType} onChange={(e) => setTransportType(e.target.value)}>
            <option>Hospital vehicle</option>
            <option>Ambulance</option>
            <option>Courier</option>
            <option>Cold-chain vehicle</option>
            <option>Third-party logistics</option>
          </select>
          <label className="f-label" htmlFor="vehicle-reference">Vehicle / tracking reference (optional)</label>
          <input id="vehicle-reference" className="f-input" value={vehicleReference} onChange={(e) => setVehicleReference(e.target.value)} maxLength={100} placeholder="e.g. VH-204" />
        </Modal>
      )}

      {trackTarget && (
        <Modal open title="Transfer record" subtitle={`#${trackTarget.transfer_id}`} onClose={() => setTrackTarget(null)}>
          <div className="space-y-3">
            <Detail label="Medicine" value={trackTarget.medicine_name} />
            <Detail label="From" value={trackTarget.from_facility_name} />
            <Detail label="To" value={trackTarget.to_facility_name} />
            <Detail label="Requested quantity" value={`${trackTarget.requested_quantity} units`} />
            <Detail label="Approved quantity" value={trackTarget.approved_quantity === null ? "Not approved" : `${trackTarget.approved_quantity} units`} />
            <Detail label="Transfer state" value={displayStatus(trackTarget.transfer_status)} />
            <Detail label="Transport" value={trackTarget.transport_type ?? "Not assigned"} />
            <Detail label="Vehicle reference" value={trackTarget.vehicle_reference ?? "Not recorded"} />
            <Detail label="Requested at" value={time(trackTarget.requested_at)} />
            <Detail label="Decision at" value={time(trackTarget.approved_at)} />
            <Detail label="Dispatched at" value={time(trackTarget.dispatched_at)} />
            <Detail label="Delivered at" value={time(trackTarget.delivered_at)} />
            {trackTarget.rejection_reason && <Detail label="Rejection reason" value={trackTarget.rejection_reason} />}
            {trackTarget.recommendation_reason && <div className="rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{trackTarget.recommendation_reason}</div>}
          </div>
        </Modal>
      )}
    </div>
  )
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl bg-slate-50 p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
    </div>
  )
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-2">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="max-w-[65%] break-words text-right text-sm font-medium text-slate-900">{value}</span>
    </div>
  )
}
