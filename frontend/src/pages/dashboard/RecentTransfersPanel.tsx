import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import { transferAPI } from "../../services/api"
import type { TransferRecord, TransferStatus } from "../../types/transfer-record"

function statusClass(status: TransferStatus) {
  switch (status) {
    case "COMPLETED": return "bg-green-100 text-green-700"
    case "IN_TRANSIT": return "bg-blue-100 text-blue-700"
    case "PENDING": return "bg-amber-100 text-amber-700"
    case "REJECTED":
    case "CANCELLED": return "bg-red-100 text-red-700"
    default: return "bg-slate-100 text-slate-700"
  }
}

function formatDate(value?: string | null) {
  if (!value) return "Time not recorded"
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? "Time not recorded" : date.toLocaleString()
}

export function RecentTransfersPanel() {
  const navigate = useNavigate()
  const { data = [], isLoading, isError } = useQuery<TransferRecord[]>({
    queryKey: ["transfers", "backend", "dashboard"],
    queryFn: async () => (await transferAPI.getAll()).data as TransferRecord[],
    refetchInterval: 10_000,
    refetchOnWindowFocus: true,
  })

  const recent = [...data]
    .sort((a, b) => new Date(b.requested_at).getTime() - new Date(a.requested_at).getTime())
    .slice(0, 4)

  return (
    <div className="panel shadow-md border border-border flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="panel-title">Recent Transfers</div>
        <button className="text-xs text-blue-600 hover:underline" onClick={() => navigate("/transfers")}>
          View all
        </button>
      </div>

      {isLoading ? (
        <p className="text-sm text-ink-faint py-5">Loading backend transfer records…</p>
      ) : isError ? (
        <p role="alert" className="text-sm text-red-600 py-5">
          Transfer records could not be loaded. Check the API connection or your access role.
        </p>
      ) : recent.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-ink-faint space-y-2 pb-4">
          <p className="text-sm">No transfer requests recorded yet.</p>
          <button className="text-xs text-blue-600 hover:underline" onClick={() => navigate("/emergency")}>
            Open Emergency Center
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {recent.map((record) => (
            <div key={record.transfer_id} className="rounded-lg border border-slate-100 p-3">
              <div className="flex items-start justify-between gap-2">
                <p className="font-medium text-sm text-ink">{record.medicine_name}</p>
                <span className={`rounded-full px-2 py-1 text-[10px] font-semibold ${statusClass(record.transfer_status)}`}>
                  {record.transfer_status.replaceAll("_", " ")}
                </span>
              </div>
              <p className="mt-1 text-xs text-ink-muted">
                {record.from_facility_name} → {record.to_facility_name}
              </p>
              <div className="mt-2 flex items-center justify-between gap-2 text-[11px] text-ink-faint">
                <span>{record.approved_quantity ?? record.requested_quantity} units</span>
                <span>{formatDate(record.requested_at)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
