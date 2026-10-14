import { useEffect, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Badge } from "../../components/ui/Badge"
import { Button } from "../../components/ui/Button"
import { KPICard } from "../../components/ui/KPICard"
import { useCurrentUser } from "../../hooks/useCurrentUser"
import api, { facilitiesAPI, integrationAPI } from "../../services/api"
import type {
  IntegrationFacility,
  IntegrationMedicine,
  IntegrationMedicineMapping,
  IntegrationSnapshotEvent,
  IntegrationSource,
  IntegrationSourceCreated,
} from "../../types/integration"

function errorMessage(error: unknown) {
  if (error && typeof error === "object" && "response" in error) {
    const response = (error as { response?: { data?: { detail?: string } } }).response
    if (response?.data?.detail) return response.data.detail
  }
  return error instanceof Error ? error.message : "Request failed. Try again."
}

function dateLabel(value?: string | null) {
  if (!value) return "Never synced"
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? "Timestamp unavailable" : parsed.toLocaleString()
}

export function IntegrationsPage() {
  const queryClient = useQueryClient()
  const { data: user, isLoading: userLoading } = useCurrentUser()
  const isAdmin = user?.role === "system_admin"
  const [sourceName, setSourceName] = useState("")
  const [systemType, setSystemType] = useState("HIS")
  const [facilityId, setFacilityId] = useState("")
  const [selectedSourceId, setSelectedSourceId] = useState("")
  const [externalMedicineCode, setExternalMedicineCode] = useState("")
  const [medicineId, setMedicineId] = useState("")
  const [oneTimeKey, setOneTimeKey] = useState<IntegrationSourceCreated | null>(null)

  const sourceQuery = useQuery<IntegrationSource[]>({
    queryKey: ["integration-sources", user?.id],
    queryFn: async () => (await integrationAPI.getSources()).data as IntegrationSource[],
    enabled: Boolean(isAdmin && user?.id),
    refetchInterval: 30000,
  })
  const sources = sourceQuery.data ?? []
  const facilityQuery = useQuery<IntegrationFacility[]>({
    queryKey: ["integration-facilities", user?.id],
    queryFn: async () => (await facilitiesAPI.getAll()).data as IntegrationFacility[],
    enabled: Boolean(isAdmin && user?.id),
  })
  const facilities = facilityQuery.data ?? []
  const medicineQuery = useQuery<IntegrationMedicine[]>({
    queryKey: ["integration-medicines", user?.id],
    queryFn: async () => (await api.get("/medicines")).data as IntegrationMedicine[],
    enabled: Boolean(isAdmin && user?.id),
  })
  const medicines = medicineQuery.data ?? []
  const mappingQuery = useQuery<IntegrationMedicineMapping[]>({
    queryKey: ["integration-mappings", user?.id, selectedSourceId],
    queryFn: async () => (await integrationAPI.getMappings(selectedSourceId)).data as IntegrationMedicineMapping[],
    enabled: Boolean(isAdmin && user?.id && selectedSourceId),
  })
  const mappings = mappingQuery.data ?? []
  const eventQuery = useQuery<IntegrationSnapshotEvent[]>({
    queryKey: ["integration-events", user?.id, selectedSourceId],
    queryFn: async () => (await integrationAPI.getEvents(selectedSourceId)).data as IntegrationSnapshotEvent[],
    enabled: Boolean(isAdmin && user?.id && selectedSourceId),
    refetchInterval: 30000,
  })
  const snapshotEvents = eventQuery.data ?? []

  useEffect(() => {
    if (!selectedSourceId && sources.length > 0) setSelectedSourceId(sources[0].source_id)
  }, [sources, selectedSourceId])

  const createSource = useMutation({
    mutationFn: async () => (await integrationAPI.createSource({
      source_name: sourceName.trim(),
      system_type: systemType,
      facility_id: facilityId,
    })).data as IntegrationSourceCreated,
    onSuccess: (result) => {
      setOneTimeKey(result)
      setSelectedSourceId(result.source_id)
      setSourceName("")
      queryClient.invalidateQueries({ queryKey: ["integration-sources"] })
      toast.success("Integration source created")
    },
    onError: (error) => toast.error(errorMessage(error)),
  })
  const rotateKey = useMutation({
    mutationFn: async (sourceId: string) => (await integrationAPI.rotateKey(sourceId)).data as IntegrationSourceCreated,
    onSuccess: (result) => {
      setOneTimeKey(result)
      queryClient.invalidateQueries({ queryKey: ["integration-sources"] })
      toast.success("Key rotated; the previous credential is now invalid")
    },
    onError: (error) => toast.error(errorMessage(error)),
  })
  const disableSource = useMutation({
    mutationFn: async (sourceId: string) => (await integrationAPI.disableSource(sourceId)).data as IntegrationSource,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["integration-sources"] })
      toast.success("Integration source disabled")
    },
    onError: (error) => toast.error(errorMessage(error)),
  })
  const saveMapping = useMutation({
    mutationFn: async () => (await integrationAPI.upsertMapping(selectedSourceId, {
      external_medicine_code: externalMedicineCode.trim(),
      medicine_id: medicineId,
    })).data as IntegrationMedicineMapping,
    onSuccess: () => {
      setExternalMedicineCode("")
      setMedicineId("")
      queryClient.invalidateQueries({ queryKey: ["integration-mappings", user?.id, selectedSourceId] })
      toast.success("Medicine mapping saved")
    },
    onError: (error) => toast.error(errorMessage(error)),
  })

  const selectedSource = sources.find((source) => source.source_id === selectedSourceId)
  const activeCount = sources.filter((source) => source.is_active).length
  const syncedCount = sources.filter((source) => Boolean(source.last_snapshot_at)).length

  if (userLoading) return <div className="panel animate-pulse text-sm text-ink-faint">Loading integration permissions…</div>
  if (!isAdmin) {
    return (
      <section className="panel">
        <div className="panel-title">Integration governance</div>
        <p className="mt-2 text-sm text-ink-muted">Only a System Admin can manage external-system credentials and medicine mappings.</p>
      </section>
    )
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-ink">External System Integrations</h1>
          <p className="mt-1 max-w-3xl text-sm text-ink-muted">
            Connect a facility’s existing HIS, ERP, pharmacy or inventory platform without replacing its current system.
          </p>
        </div>
        <Badge variant="blue">Admin controlled</Badge>
      </header>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        <KPICard label="Configured sources" value={sources.length} sub="One authoritative feed per facility" color="blue" />
        <KPICard label="Active credentials" value={activeCount} sub="Accepted by the snapshot gateway" color="green" />
        <KPICard label="Ever synced" value={syncedCount} sub="At least one accepted snapshot" color="orange" />
      </div>

      {oneTimeKey && (
        <section className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="font-semibold text-emerald-950">Copy the integration key now</p>
              <p className="mt-1 text-sm text-emerald-900">{oneTimeKey.credential_note}</p>
            </div>
            <Button variant="ghost" size="sm" onClick={() => setOneTimeKey(null)}>Dismiss</Button>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <code className="min-w-0 flex-1 break-all rounded-lg border border-emerald-200 bg-white p-3 text-sm text-slate-900">{oneTimeKey.integration_key}</code>
            <Button variant="green" onClick={() => {
              void navigator.clipboard.writeText(oneTimeKey.integration_key).then(
                () => toast.success("Integration key copied"),
                () => toast.error("Clipboard unavailable; copy the key manually"),
              )
            }}>Copy key</Button>
          </div>
          <p className="mt-2 text-xs text-emerald-900">Treat the key like a password. It is not stored in browser storage and is shown only once.</p>
        </section>
      )}

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(280px,0.8fr)_minmax(500px,1.2fr)]">
        <section className="panel">
          <div className="panel-title">Register an integration source</div>
          <p className="mb-4 mt-1 text-sm text-ink-muted">Issue a credential scoped to one facility’s inventory snapshot feed.</p>
          <form onSubmit={(event) => { event.preventDefault(); createSource.mutate() }}>
            <label className="f-label" htmlFor="source-name">Connection name</label>
            <input id="source-name" className="f-input mb-3" value={sourceName} onChange={(event) => setSourceName(event.target.value)} minLength={3} maxLength={255} placeholder="e.g. Apollo Hospital HIS" required />
            <label className="f-label" htmlFor="source-type">System type</label>
            <select id="source-type" className="f-input mb-3" value={systemType} onChange={(event) => setSystemType(event.target.value)}>
              <option value="HIS">Hospital Information System</option>
              <option value="ERP">ERP / Procurement</option>
              <option value="PHARMACY_POS">Pharmacy POS</option>
              <option value="HL7_FHIR">HL7 / FHIR adapter</option>
              <option value="CUSTOM_API">Custom API</option>
              <option value="CSV_ADAPTER">CSV adapter</option>
            </select>
            <label className="f-label" htmlFor="source-facility">Facility</label>
            <select id="source-facility" className="f-input mb-4" value={facilityId} onChange={(event) => setFacilityId(event.target.value)} required>
              <option value="">Select a facility</option>
              {facilities.map((facility) => (
                <option key={facility.facility_id} value={facility.facility_id}>
                  {facility.facility_name}{facility.city ? " · " + facility.city : ""}
                </option>
              ))}
            </select>
            <Button type="submit" disabled={createSource.isPending || !sourceName.trim() || !facilityId}>
              {createSource.isPending ? "Creating source…" : "Create source & issue key"}
            </Button>
          </form>
          <div className="mt-4 rounded-lg border border-blue-100 bg-blue-50 p-3 text-xs text-blue-900">
            The gateway accepts batch-level inventory snapshots. Partner-specific connectors still need validation against real HIS/ERP systems.
          </div>
        </section>

        <section className="panel">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="panel-title">Configured sources</div>
              <p className="mt-1 text-sm text-ink-muted">Credential state and last accepted snapshot.</p>
            </div>
            <Button variant="ghost" size="sm" onClick={() => queryClient.invalidateQueries({ queryKey: ["integration-sources"] })}>Refresh</Button>
          </div>
          {sourceQuery.isLoading && <div className="mt-4 rounded-lg bg-slate-50 p-5 text-sm text-ink-muted">Loading registered sources…</div>}
          {sourceQuery.isError && <div role="alert" className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">{errorMessage(sourceQuery.error)}</div>}
          {!sourceQuery.isLoading && !sourceQuery.isError && sources.length === 0 && (
            <div className="mt-4 rounded-lg border border-dashed border-slate-300 p-7 text-center">
              <p className="font-semibold text-ink">No external sources configured</p>
              <p className="mt-1 text-sm text-ink-muted">Register a facility to start integration onboarding.</p>
            </div>
          )}
          {sources.length > 0 && (
            <div className="mt-4 space-y-3">
              {sources.map((source) => {
                const facility = facilities.find((item) => item.facility_id === source.facility_id)
                return (
                  <article key={source.source_id} className={"rounded-xl border p-4 " + (selectedSourceId === source.source_id ? "border-blue-300 bg-blue-50/40" : "border-border bg-white")}>
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <button className="text-left" onClick={() => setSelectedSourceId(source.source_id)}>
                        <p className="font-semibold text-ink">{source.source_name}</p>
                        <p className="mt-1 text-xs text-ink-muted">{facility?.facility_name ?? source.facility_id} · {source.system_type}</p>
                      </button>
                      <Badge variant={source.is_active ? "green" : "red"}>{source.is_active ? "ACTIVE" : "DISABLED"}</Badge>
                    </div>
                    <p className="mt-3 text-xs text-ink-muted">Last accepted snapshot: {dateLabel(source.last_snapshot_at)}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <Button size="sm" variant={selectedSourceId === source.source_id ? "primary" : "ghost"} onClick={() => setSelectedSourceId(source.source_id)}>Manage mappings</Button>
                      <Button size="sm" variant="ghost" disabled={rotateKey.isPending} onClick={() => {
                        if (window.confirm("Rotate this key? The current integration will stop working until it receives the new key.")) rotateKey.mutate(source.source_id)
                      }}>{source.is_active ? "Rotate key" : "Re-enable & rotate"}</Button>
                      {source.is_active && (
                        <Button size="sm" variant="red" disabled={disableSource.isPending} onClick={() => {
                          if (window.confirm("Disable this source? Its key will no longer be accepted.")) disableSource.mutate(source.source_id)
                        }}>Disable</Button>
                      )}
                    </div>
                  </article>
                )
              })}
            </div>
          )}
        </section>
      </div>

      <section className="panel">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="panel-title">External medicine mappings</div>
            <p className="mt-1 text-sm text-ink-muted">Unmapped partner medicine codes are rejected rather than guessed.</p>
          </div>
          <div className="min-w-56">
            <label className="f-label" htmlFor="mapping-source">Selected source</label>
            <select id="mapping-source" className="f-input" value={selectedSourceId} onChange={(event) => setSelectedSourceId(event.target.value)}>
              <option value="">Select a source</option>
              {sources.map((source) => <option key={source.source_id} value={source.source_id}>{source.source_name}</option>)}
            </select>
          </div>
        </div>
        {!selectedSource && <p className="mt-4 text-sm text-ink-muted">Select or create a source to configure mappings.</p>}
        {selectedSource && (
          <>
            <form className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-[minmax(160px,0.7fr)_minmax(240px,1.3fr)_auto]" onSubmit={(event) => { event.preventDefault(); saveMapping.mutate() }}>
              <div>
                <label className="f-label" htmlFor="external-code">Partner medicine code</label>
                <input id="external-code" className="f-input" value={externalMedicineCode} onChange={(event) => setExternalMedicineCode(event.target.value)} maxLength={100} placeholder="e.g. MED-INS-001" required />
              </div>
              <div>
                <label className="f-label" htmlFor="canonical-medicine">AegisFlow medicine</label>
                <select id="canonical-medicine" className="f-input" value={medicineId} onChange={(event) => setMedicineId(event.target.value)} required>
                  <option value="">Select canonical medicine</option>
                  {medicines.map((medicine) => <option key={medicine.medicine_id} value={medicine.medicine_id}>{medicine.medicine_name} · {medicine.medicine_code}</option>)}
                </select>
              </div>
              <div className="flex items-end"><Button type="submit" disabled={saveMapping.isPending || !externalMedicineCode.trim() || !medicineId}>{saveMapping.isPending ? "Saving…" : "Save mapping"}</Button></div>
            </form>
            {mappingQuery.isError && <div role="alert" className="mt-3 text-sm text-red-700">{errorMessage(mappingQuery.error)}</div>}
            {mappingQuery.isLoading && <p className="mt-4 text-sm text-ink-muted">Loading mappings…</p>}
            {!mappingQuery.isLoading && !mappingQuery.isError && mappings.length === 0 && <p className="mt-4 text-sm text-ink-muted">No mappings yet for {selectedSource.source_name}.</p>}
            {mappings.length > 0 && (
              <div className="mt-4 overflow-x-auto">
                <table className="af-table min-w-[640px]">
                  <thead><tr><th>Partner code</th><th>AegisFlow medicine</th><th>Status</th></tr></thead>
                  <tbody>
                    {mappings.map((mapping) => {
                      const medicine = medicines.find((item) => item.medicine_id === mapping.medicine_id)
                      return (
                        <tr key={mapping.mapping_id}>
                          <td className="font-medium">{mapping.external_medicine_code}</td>
                          <td>{medicine ? medicine.medicine_name + " · " + medicine.medicine_code : mapping.medicine_id}</td>
                          <td><Badge variant={mapping.is_active ? "green" : "red"}>{mapping.is_active ? "ACTIVE" : "DISABLED"}</Badge></td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </section>

      <section className="panel">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="panel-title">Accepted snapshot history</div>
            <p className="mt-1 text-sm text-ink-muted">
              Up to 100 successful receipts for the selected source. Rejected requests are returned as HTTP errors and are not recorded in this receipt table.
            </p>
          </div>
          <Button variant="ghost" size="sm" disabled={!selectedSourceId} onClick={() => queryClient.invalidateQueries({ queryKey: ["integration-events", user?.id, selectedSourceId] })}>Refresh history</Button>
        </div>
        {!selectedSourceId && <p className="mt-3 text-sm text-ink-muted">Select a source to inspect accepted snapshots.</p>}
        {selectedSourceId && eventQuery.isLoading && <p className="mt-3 text-sm text-ink-muted">Loading accepted receipts…</p>}
        {eventQuery.isError && <div role="alert" className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">{errorMessage(eventQuery.error)}</div>}
        {selectedSourceId && !eventQuery.isLoading && !eventQuery.isError && snapshotEvents.length === 0 && (
          <div className="mt-3 rounded-lg border border-dashed border-slate-300 p-5 text-sm text-ink-muted">No successful inventory snapshots have been accepted for this source yet.</div>
        )}
        {snapshotEvents.length > 0 && (
          <div className="mt-4 overflow-x-auto">
            <table className="af-table min-w-[740px]">
              <thead><tr><th>External event ID</th><th>Source timestamp</th><th>Received at</th><th>Records</th><th>Status</th></tr></thead>
              <tbody>
                {snapshotEvents.map((event) => (
                  <tr key={event.integration_event_id}>
                    <td className="font-medium">{event.external_event_id}</td>
                    <td>{dateLabel(event.source_timestamp)}</td>
                    <td>{dateLabel(event.received_at)}</td>
                    <td>{event.records_processed}</td>
                    <td><Badge variant={event.status === "APPLIED" ? "green" : "orange"}>{event.status}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="rounded-xl border border-border bg-white p-4">
        <h2 className="font-semibold text-ink">Snapshot gateway</h2>
        <p className="mt-1 text-sm text-ink-muted">Send the key server-to-server only; do not embed it in public browser code.</p>
        <div className="mt-3 rounded-lg bg-slate-950 p-3 font-mono text-sm text-slate-100">
          POST /api/v1/integrations/inventory/snapshot<br />
          X-Integration-Key: [partner securely stores the issued key]
        </div>
        <div className="mt-3 grid grid-cols-1 gap-2 text-sm md:grid-cols-2">
          <div className="rounded-lg bg-slate-50 p-3"><strong>Required input</strong><p className="mt-1 text-xs text-ink-muted">External event ID, timezone-aware source timestamp, medicine mapping and batch/expiry-level quantities.</p></div>
          <div className="rounded-lg bg-slate-50 p-3"><strong>Replay safety</strong><p className="mt-1 text-xs text-ink-muted">Identical event replays are no-ops. Changed payloads under the same event ID and stale snapshots are rejected.</p></div>
        </div>
      </section>
    </div>
  )
}
