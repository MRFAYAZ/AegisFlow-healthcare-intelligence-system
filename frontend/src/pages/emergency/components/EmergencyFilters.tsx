interface EmergencyFiltersProps {
    search: string
    setSearch: (value: string) => void
    severity: string
    setSeverity: (value: string) => void
    status: string
    setStatus: (value: string) => void
}

export function EmergencyFilters({
    search,
    setSearch,
    severity,
    setSeverity,
    status,
    setStatus,
}: EmergencyFiltersProps) {
    return (
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
            <div className="flex flex-col gap-4 md:flex-row md:items-end">
                <label className="flex-1 text-sm text-ink-muted">
                    <span className="mb-1 block">Search</span>
                    <input
                        className="w-full rounded-lg border border-border px-3 py-2"
                        placeholder="Case ID, facility, medicine"
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                    />
                </label>

                <label className="text-sm text-ink-muted">
                    <span className="mb-1 block">Severity</span>
                    <select
                        className="rounded-lg border border-border px-3 py-2"
                        value={severity}
                        onChange={(event) => setSeverity(event.target.value)}
                    >
                        <option value="ALL">All</option>
                        <option value="WARNING">Warning</option>
                        <option value="CRITICAL">Critical</option>
                        <option value="EMERGENCY">Emergency</option>
                    </select>
                </label>

                <label className="text-sm text-ink-muted">
                    <span className="mb-1 block">Status</span>
                    <select
                        className="rounded-lg border border-border px-3 py-2"
                        value={status}
                        onChange={(event) => setStatus(event.target.value)}
                    >
                        <option value="ALL">All</option>
                        <option value="ACTIVE">Active</option>
                        <option value="MATCHING">Matching</option>
                        <option value="RESOLVED">Resolved</option>
                    </select>
                </label>
            </div>
        </div>
    )
}