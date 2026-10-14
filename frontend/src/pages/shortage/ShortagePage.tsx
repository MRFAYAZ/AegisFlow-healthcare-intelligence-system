import { useMemo } from "react"
import { useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Badge } from "../../components/ui/Badge"
import { Button } from "../../components/ui/Button"
import { KPICard } from "../../components/ui/KPICard"
import { inventoryAPI } from "../../services/api"
import type { StockoutForecast } from "../../types/forecast"
import { useCurrentUser } from "../../hooks/useCurrentUser"

function riskVariant(risk: StockoutForecast["risk_level"]): "red" | "orange" | "yellow" | "green" | "blue" {
  switch (risk) {
    case "CRITICAL": return "red"
    case "HIGH": return "orange"
    case "WARNING": return "yellow"
    case "SAFE": return "green"
    default: return "blue"
  }
}

function actionLabel(action: StockoutForecast["recommended_action"]) {
  switch (action) {
    case "SOURCE_NETWORK": return "Source network"
    case "REPLENISH": return "Replenish"
    case "REVIEW_REPLENISHMENT": return "Review replenishment"
    case "REVIEW_CONSUMPTION": return "Review consumption data"
    default: return "Monitor"
  }
}

function stockoutLabel(days: number | null) {
  if (days === null) return "Insufficient consumption data"
  if (days === 0) return "Now"
  return `${days.toFixed(1)} days`
}

export function ShortagePage() {
  const navigate = useNavigate()
  const { data: user } = useCurrentUser()
  const { data: forecasts = [], isLoading, isError, error } = useQuery<StockoutForecast[]>({
    queryKey: ["stockout-forecasts", user?.id ?? "anonymous"],
    queryFn: async () => (await inventoryAPI.getForecast()).data as StockoutForecast[],
    enabled: Boolean(user?.id),
    refetchInterval: 15_000,
    refetchOnWindowFocus: true,
  })

  const summary = useMemo(() => ({
    critical: forecasts.filter((item) => item.risk_level === "CRITICAL").length,
    high: forecasts.filter((item) => item.risk_level === "HIGH").length,
    warning: forecasts.filter((item) => item.risk_level === "WARNING").length,
    needsData: forecasts.filter((item) => item.risk_level === "INSUFFICIENT_DATA").length,
  }), [forecasts])

  const message = error instanceof Error ? error.message : "Forecast API request failed."

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <KPICard label="Critical stockout risk" value={summary.critical} sub="Projected at or before lead time" color="red" />
        <KPICard label="High risk" value={summary.high} sub="Needs prompt replenishment action" color="orange" />
        <KPICard label="Warnings" value={summary.warning} sub="Stock buffer below target" color="orange" />
        <KPICard label="Needs consumption data" value={summary.needsData} sub="Cannot project stockout reliably" color="blue" />
      </div>

      <section className="panel">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="panel-title">Predictive shortage intelligence</div>
            <p className="mt-1 max-w-3xl text-sm text-ink-muted">
              Explainable stockout projection using recorded available stock, daily consumption, replenishment lead time and medicine safety-stock policy.
            </p>
          </div>
          <Badge variant="blue">Rule-based forecast</Badge>
        </div>

        <div className="mb-4 rounded-lg border border-blue-100 bg-blue-50 p-3 text-xs text-blue-900">
          This is deterministic decision support, not a trained ML forecast. Reserved units are shown separately and are not counted as usable stock. Unknown consumption is reported as insufficient data rather than silently labelled safe.
        </div>

        {isLoading && (
          <div className="rounded-lg bg-slate-50 p-6 text-sm text-slate-500">
            Calculating stockout exposure from current inventory records…
          </div>
        )}

        {isError && (
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            Forecasts could not be loaded. {message}
          </div>
        )}

        {!isLoading && !isError && forecasts.length === 0 && (
          <div className="rounded-lg border border-dashed border-slate-300 p-8 text-center">
            <p className="font-semibold text-slate-900">No forecastable inventory records</p>
            <p className="mt-1 text-sm text-slate-500">
              Add facility inventory with daily consumption and lead-time data to generate projections.
            </p>
          </div>
        )}

        {!isLoading && !isError && forecasts.length > 0 && (
          <div className="overflow-x-auto">
            <table className="af-table min-w-[1100px]">
              <thead>
                <tr>
                  <th>Medicine / facility</th>
                  <th>Available / verified</th>
                  <th>Batch / expiry</th>
                  <th>Daily use</th>
                  <th>Projected stockout</th>
                  <th>Risk</th>
                  <th>Recommended action</th>
                  <th>Reason</th>
                  <th>Next step</th>
                </tr>
              </thead>
              <tbody>
                {forecasts.map((item) => (
                  <tr key={item.inventory_id}>
                    <td>
                      <p className="font-medium text-ink">{item.medicine_name}</p>
                      <p className="mt-1 text-xs text-ink-muted">{item.facility_name}</p>
                    </td>
                    <td>
                      <p>{item.available_stock} aggregate available</p>
                      <p className="text-xs text-ink-muted">{item.reserved_stock} reserved</p>
                      <p className="mt-1 text-xs font-semibold text-slate-700">{item.batch_verified_usable_stock} batch-verified usable</p>
                    </td>
                    <td>
                      <div className="space-y-1">
                        <Badge variant={item.batch_traceability === "VERIFIED" ? "green" : "red"}>
                          {item.batch_traceability.replaceAll("_", " ")}
                        </Badge>
                        <p className="text-xs text-ink-muted">{item.eligible_batch_count} eligible lots</p>
                        <p className="text-xs text-ink-muted">{item.expired_batch_quantity} expired units</p>
                      </div>
                    </td>
                    <td>
                      {item.daily_consumption_rate > 0 ? `${item.daily_consumption_rate} units/day` : "Not recorded"}
                    </td>
                    <td>
                      <p className="font-semibold">{stockoutLabel(item.projected_stockout_days)}</p>
                      <p className="text-xs text-ink-muted">{item.lead_time_days}d lead · {item.safety_stock_days}d safety</p>
                    </td>
                    <td>
                      <div className="space-y-1">
                        <Badge variant={riskVariant(item.risk_level)}>{item.risk_level.replaceAll("_", " ")}</Badge>
                        <p className="text-xs text-ink-muted">{item.risk_score === null ? "Score unavailable" : `Risk score ${item.risk_score.toFixed(1)} / 100`}</p>
                      </div>
                    </td>
                    <td>{actionLabel(item.recommended_action)}</td>
                    <td className="max-w-sm whitespace-normal text-xs text-ink-muted">{item.explanation}</td>
                    <td>
                      {item.recommended_action === "SOURCE_NETWORK"
                        ? <Button size="sm" variant="red" onClick={() => navigate("/emergency")}>Open EOC</Button>
                        : <Button size="sm" variant="ghost" onClick={() => navigate("/inventory")}>Review inventory</Button>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <p className="mt-3 text-xs text-ink-muted">
          Forecasts refresh every 15 seconds from the backend. They do not reserve inventory, create emergency cases or place purchase orders automatically.
        </p>
      </section>
    </div>
  )
}
