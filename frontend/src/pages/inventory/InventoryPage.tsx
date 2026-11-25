import { useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Badge } from "../../components/ui/Badge"
import { Button } from "../../components/ui/Button"
import { useInventory } from "../../hooks/useInventory"
import type { InventoryRecord } from "../../types/inventory"

const severityStyle: Record<string, "red" | "orange" | "yellow" | "green"> = {
  EMERGENCY: "red",
  CRITICAL: "orange",
  WARNING: "yellow",
  SAFE: "green",
}

function labelSeverity(value?: string) {
  if (!value) return "Unknown"
  return value.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase())
}

export function InventoryPage() {
  const navigate = useNavigate()
  const { data = [], isLoading, isError } = useInventory()
  const [search, setSearch] = useState("")
  const [filter, setFilter] = useState<"all" | "critical" | "warning" | "adequate">("all")

  const inventory = data
  const filtered = useMemo(() => inventory.filter((item) => {
    const query = search.trim().toLowerCase()
    const name = String(item.medicine_name ?? "").toLowerCase()
    const facility = String(item.facility_name ?? "").toLowerCase()
    const matchesSearch = !query || name.includes(query) || facility.includes(query)
    const severity = String(item.severity ?? "").toUpperCase()
    const matchesFilter = filter === "all"
      || (filter === "critical" && ["CRITICAL", "EMERGENCY"].includes(severity))
      || (filter === "warning" && severity === "WARNING")
      || (filter === "adequate" && severity === "SAFE")
    return matchesSearch && matchesFilter
  }), [inventory, search, filter])

  if (isLoading) {
    return <div className="panel p-6">Loading inventory from the backend…</div>
  }

  if (isError) {
    return (
      <div role="alert" className="panel p-6 text-red-700">
        Inventory could not be loaded. Check the API connection and your signed-in role.
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <section className="panel">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="panel-title">Inventory register</div>
            <p className="mt-1 text-sm text-ink-muted">
              Live inventory records from the AegisFlow backend.
            </p>
          </div>
          <Badge variant="blue">Backend data · Read only</Badge>
        </div>

        <div className="mb-4 flex flex-wrap items-center gap-2">
          <input
            className="f-input"
            style={{ width: 240 }}
            placeholder="Search medicine or facility…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <select
            className="f-input"
            style={{ width: 170 }}
            value={filter}
            onChange={(event) => setFilter(event.target.value as typeof filter)}
          >
            <option value="all">All stock levels</option>
            <option value="critical">Critical / Emergency</option>
            <option value="warning">Warning</option>
            <option value="adequate">Adequate</option>
          </select>
          <span className="text-sm text-ink-muted">{filtered.length} inventory records</span>
        </div>

        <div className="overflow-x-auto">
          <table className="af-table min-w-[850px]">
            <thead>
              <tr>
                <th>Medicine</th>
                <th>Facility</th>
                <th>Total</th>
                <th>Available</th>
                <th>Reserved</th>
                <th>Stock level</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => {
                const severity = String(item.severity ?? "").toUpperCase()
                const total = Number(item.total_stock ?? 0)
                const available = Number(item.available_stock ?? 0)
                const reserved = Number(item.reserved_stock ?? 0)
                const pct = total > 0 ? Math.max(0, Math.min(100, Math.round((available / total) * 100))) : 0
                const needsSupply = ["CRITICAL", "EMERGENCY", "WARNING"].includes(severity)
                return (
                  <tr key={item.inventory_id}>
                    <td className="font-medium text-ink">{item.medicine_name || "Unknown medicine"}</td>
                    <td className="text-ink-muted">{item.facility_name || "Unknown facility"}</td>
                    <td>{total}</td>
                    <td>{available}</td>
                    <td>{reserved}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="progress-track" style={{ width: 64 }}>
                          <div className="progress-fill" style={{ width: `${pct}%` }} />
                        </div>
                        <Badge variant={severityStyle[severity] ?? "yellow"}>{labelSeverity(severity)}</Badge>
                      </div>
                    </td>
                    <td>
                      {needsSupply ? (
                        <Button size="sm" variant="primary" onClick={() => navigate("/emergency")}>
                          Open Emergency
                        </Button>
                      ) : (
                        <span className="text-xs text-ink-muted">No action</span>
                      )}
                    </td>
                  </tr>
                )
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-ink-muted">No inventory records match this filter.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <p className="mt-4 rounded-lg bg-slate-50 p-3 text-xs text-ink-muted">
          This screen displays backend inventory and does not create local-only stock records. Use authorized inventory integrations to update stock; use Emergency Center to initiate a redistribution request.
        </p>
      </section>
    </div>
  )
}
